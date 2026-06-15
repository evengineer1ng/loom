"""Deterministic vocal synthesis — a voice from LOGIC, no samples. The true audio analog of the
grammar: generate the waveform from a tiny table, never borrow recorded human sound.

Source-filter model: a glottal source (harmonic-rich tone at f0) -> formant filters (each vowel is
just a set of resonance frequencies) + vibrato (f0 x a slow sine, dialable) + an envelope + breath.
Pure numpy, no ML, no source. "No source is the test." A note-tape sung by math.

POC honesty: it'll sound synthy — a human-passable pure-synth voice is the frontier. This is the
substrate to MEASURE how far deterministic logic climbs (your ABX), with vibrato/formants as knobs.
"""
from __future__ import annotations

import numpy as np

# vowel = a set of formant resonance frequencies (Hz). A tiny KB, not a sample. (tenor-ish)
FORMANTS = {
    "a": [700, 1220, 2600], "e": [400, 1700, 2600], "i": [240, 2400, 2900],
    "o": [450, 800, 2830], "u": [325, 700, 2530],
}


def estimate_f0(audio: np.ndarray, sr: int, fmin: float = 80.0, fmax: float = 700.0) -> float:
    """Autocorrelation pitch — robust for a formant-shaped voice (FFT-argmax would pick a formant)."""
    x = audio[: int(0.5 * sr)].astype(float)
    x = x - np.mean(x)
    if not np.any(x):
        return 0.0
    corr = np.correlate(x, x, mode="full")[len(x) - 1:]
    lo, hi = int(sr / fmax), min(int(sr / fmin), len(corr) - 1)
    lag = lo + int(np.argmax(corr[lo:hi]))
    if not lag:
        return 0.0
    peak = corr[lag]
    for m in (2, 3, 4):                               # octave correction: prefer the true (longer) period
        ml = lag * m
        if ml < hi and corr[ml] >= 0.8 * peak:
            lag = ml
    return sr / lag


def _glottal(f0_track: np.ndarray, sr: int) -> np.ndarray:
    """Band-limited sawtooth-ish glottal source via phase integration (handles vibrato in f0)."""
    phase = np.cumsum(2 * np.pi * f0_track / sr)
    sig = np.zeros_like(phase)
    fmax = float(np.max(f0_track))
    k = 1
    while k * fmax < sr / 2 and k <= 50:
        sig += np.sin(k * phase) / k                 # 1/k -> sawtooth spectrum (rich for formants)
        k += 1
    return sig


def _formant_filter(sig: np.ndarray, formants, sr: int, bw: float = 90.0) -> np.ndarray:
    """Shape the source spectrum with resonance peaks at the vowel's formants (freq-domain)."""
    n = len(sig)
    spec = np.fft.rfft(sig)
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    env = np.full_like(freqs, 0.03)
    for f in formants:
        env += np.exp(-0.5 * ((freqs - f) / bw) ** 2)
    return np.fft.irfft(spec * env, n=n)


def _envelope(n: int, sr: int) -> np.ndarray:
    a = min(int(0.04 * sr), n // 4) or 1
    env = np.ones(n)
    env[:a] = np.linspace(0, 1, a) ** 2
    env[-a:] = np.linspace(1, 0, a) ** 2
    return env


def sing_note(hz: float, dur_s: float, *, vowel: str = "a", vibrato_depth: float = 0.0,
              vibrato_rate: float = 5.5, breath: float = 0.005, sr: int = 44100) -> np.ndarray:
    t = np.arange(int(dur_s * sr)) / sr
    f0 = hz * (1.0 + vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t))
    voiced = _formant_filter(_glottal(f0, sr), FORMANTS.get(vowel, FORMANTS["a"]), sr)
    voiced = voiced / (np.max(np.abs(voiced)) or 1.0)
    rng = np.random.RandomState(0)                   # deterministic breath
    out = (voiced + breath * rng.randn(len(voiced))) * _envelope(len(voiced), sr)
    return (0.6 * out).astype(np.float32)


def render_tape(notes, *, vowel="a", vibrato_depth=0.0, sr=44100, gap=0.03) -> np.ndarray:
    silence = np.zeros(int(gap * sr), dtype=np.float32)
    out = []
    for nt in notes:
        out.append(sing_note(nt["hz"], float(nt.get("dur", 0.5)), vowel=nt.get("vowel", vowel),
                             vibrato_depth=vibrato_depth, sr=sr))
        out.append(silence)
    return np.concatenate(out).astype(np.float32) if out else np.zeros(1, dtype=np.float32)
