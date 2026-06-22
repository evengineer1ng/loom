"""The visual-signature transition engine — deterministic, local, no LLM.

The idea (convergence 2026-06-20): don't ask an AI to invent a transition every time. Each
oradio exposes a small **visual signature**; RibbonOS then derives a deterministic BRIDGE between
two signatures by interpolating a few authored anchor points:

    source signature  ->  neutral ribbon CARRIER  ->  target signature

The ribbon is the universal carrier: during the bridge it sheds the source's color/motion/texture
and adopts the target's, so it always feels like "RibbonOS is taking me there," not "MP4 A
awkwardly cut to MP4 B."

Because a transition only needs to respect first frame / last frame / dominant palette / motion
direction / theme family, it never has to understand the whole video — so it stays local,
deterministic, and shippable with no embedded model. The same machinery powers both crossovers
between soulmates AND the boot-screen "door" transition (see memory: visual-continuity-engine,
loom-as-relationship-lens).

QUALITY LADDER (graceful degradation) — `bridge()` walks it top-down and degrades on failure:

    best     custom authored transition clip       -> use it verbatim
    hero     fluid CARRIER (live loops + storm)     -> A loop -> swirling color storm -> B loop
    good     deterministic signature morph          -> exit_anchor -> tinted carrier -> entry_anchor
    safe     fade through a neutral logo / void      -> exit_anchor -> logo|black -> entry_anchor
    fallback hard cut with a short dissolve          -> exit_anchor -> entry_anchor (tiny xfade)

The CARRIER is the hero: it plays both LIVE loops under a deterministic, seeded swirling
color-storm (vortex-advected fluid + injected clip colors), dissolving A->B at the MIDDLE so the
last frame lands clean on B's first frame. Every edge looks different (10+ seeded lanes) yet
replays byte-identically; the exit is the entry reversed. Needs opencv+numpy; degrades to the
anchor rungs if unavailable. See memory: visual-continuity-engine.

Pure/headless; reuses bookmark.mint's ffmpeg resolution.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .mint import MintError, _run, _tool

try:
    import cv2  # type: ignore
    import numpy as np  # type: ignore
    HAS_CV2 = True
except Exception:  # pragma: no cover - optional dependency
    cv2 = None  # type: ignore
    np = None  # type: ignore
    HAS_CV2 = False

# Rungs of the quality ladder, best -> fallback.
RUNG_CUSTOM = "custom"
RUNG_CARRIER = "carrier"
RUNG_MORPH = "morph"
RUNG_NEUTRAL = "neutral"
RUNG_HARDCUT = "hardcut"

SIGNATURE_VERSION = "loom.visual_signature.v1"
DEFAULT_SIZE: Tuple[int, int] = (640, 360)
DEFAULT_FPS = 30

# Carrier defaults
CARRIER_FPS = 30
CARRIER_SECONDS = 5.0
CARRIER_SECONDS_RANGE: Tuple[float, float] = (3.0, 6.0)  # seeded length lane when seconds=None
CARRIER_SIZE: Tuple[int, int] = (960, 540)
_CARRIER_REF_W = 1280  # lane magnitudes were tuned at this width; scale to any render size

# Attract / push-to-start loop defaults (the seamless idle that sits AT the bookmark door before
# you "push start"). Longer + calmer than the carrier; a SEAMLESS LOOP, not a one-shot.
ATTRACT_FPS = 30
ATTRACT_SECONDS = 6.0
ATTRACT_SECONDS_RANGE: Tuple[float, float] = (5.0, 8.0)  # seeded length lane
ATTRACT_SIZE: Tuple[int, int] = (960, 540)


# ---------------------------------------------------------------------------
# transition PERSONALITIES (the style library)
# ---------------------------------------------------------------------------
# The carrier is not "the engine" — it's one STYLE. Same renderer underneath (seeded advection +
# particles + colour injection + purity ramp + seamless + deterministic, never fades to black); a
# personality only swaps the VELOCITY FIELD (its topology is what gives a family its taste — vortex
# soup vs whirlpool vs woven), optionally a sample-space COORD TRANSFORM (kaleidoscope), and the
# feedback / particle / move knobs. Colour identity is shared (no per-style tints by request).
# "ribbon_drift" is the original, default, byte-for-byte unchanged. See memory visual-continuity.
#
# A field_fn returns a RAW velocity field (fx, fy); the renderer normalises it. A coord_transform
# returns sample coords (sx, sy); the renderer blends identity->transform by the purity envelope so
# the seams stay clean (frame 0 == pure from-loop, last == pure to-loop).

@dataclass
class CarrierProfile:
    """One transition personality. `field`/`coord_transform` None = the default ribbon-drift flow.
    The mul/bias knobs reshape feedback (decay = persistence/afterimage), motion, particle density,
    and the time envelope without touching the shared renderer or colour identity."""
    name: str
    field: Optional[Callable[..., Tuple[Any, Any]]] = None
    coord_transform: Optional[Callable[..., Tuple[Any, Any]]] = None
    move_mul: float = 1.0
    decay_bias: float = 0.0          # + = longer trails / afterimage (Echo)
    gain_mul: float = 1.0
    particle_mul: float = 1.0
    bell_k_mul: float = 1.0


def _field_aurora(gx, gy, w, h, sw, rng, vigor):
    """Aurora Drift: a calm upward curtain — gentle vertical drift with slow side-sway that varies
    with height, like northern-lights sheets. (Pair with low move + high decay for silk.)"""
    ph = float(rng.uniform(0, 6.28)); ph2 = float(rng.uniform(0, 6.28))
    sway = np.sin(gy * (2.2 * np.pi / h) + ph) * 0.55 + np.sin(gx * (1.5 * np.pi / w) + ph2) * 0.2
    rise = -np.ones_like(gy, dtype=np.float32) * (0.7 + 0.3 * vigor)   # -y = up
    return sway.astype(np.float32), rise


def _field_whirlpool(gx, gy, w, h, sw, rng, vigor):
    """Whirlpool: one dominant off-centre spiral — strong tangential spin + inward pull, stronger
    near the eye. A single sink instead of the default vortex soup."""
    cx = w * float(rng.uniform(0.35, 0.65)); cy = h * float(rng.uniform(0.35, 0.65))
    spin = float(rng.choice([-1.0, 1.0])) * (1.5 + 1.0 * vigor)
    dx = gx - cx; dy = gy - cy
    dist = np.sqrt(dx * dx + dy * dy) + 1e-3
    fx = (-dy / dist) * spin + (-dx / dist) * 0.7      # tangential + inward
    fy = (dx / dist) * spin + (-dy / dist) * 0.7
    fall = np.clip(1.0 - dist / (0.85 * max(w, h)), 0.12, 1.0)
    return (fx * fall).astype(np.float32), (fy * fall).astype(np.float32)


def _field_woven(gx, gy, w, h, sw, rng, vigor):
    """Woven (warp + weft): two orthogonal sinusoidal thread-flows interleaved — horizontal threads
    carried by a vertical phase and vertical threads by a horizontal one, a basket weave. Loom-core."""
    ph1 = float(rng.uniform(0, 6.28)); ph2 = float(rng.uniform(0, 6.28))
    nx = int(rng.integers(3, 7)); ny = int(rng.integers(3, 7))
    fx = np.sin(gy * (ny * np.pi / h) + ph1)
    fy = np.cos(gx * (nx * np.pi / w) + ph2)
    return fx.astype(np.float32), fy.astype(np.float32)


def _coords_kaleidoscope(gx, gy, w, h, segments=6):
    """Fold the plane into mirrored wedges around centre -> kaleidoscopic symmetry. Blended in by
    the renderer's purity envelope, so the seams stay clean."""
    cx, cy = w / 2.0, h / 2.0
    dx = gx - cx; dy = gy - cy
    r = np.sqrt(dx * dx + dy * dy)
    theta = np.arctan2(dy, dx)
    wedge = 2.0 * np.pi / segments
    t = np.mod(theta, wedge)
    t = np.minimum(t, wedge - t)            # mirror within the wedge
    sx = cx + r * np.cos(t)
    sy = cy + r * np.sin(t)
    return sx.astype(np.float32), sy.astype(np.float32)


# The shipped library. Add families by adding entries — the renderer is reused.
CARRIER_PROFILES: Dict[str, CarrierProfile] = {
    "ribbon_drift": CarrierProfile("ribbon_drift"),                              # the original (default)
    "aurora":       CarrierProfile("aurora", field=_field_aurora, move_mul=0.6,
                                   decay_bias=0.06, particle_mul=0.8),
    "echo":         CarrierProfile("echo", decay_bias=0.13, gain_mul=0.85,       # afterimage (default field)
                                   particle_mul=0.6),
    "whirlpool":    CarrierProfile("whirlpool", field=_field_whirlpool, move_mul=1.1, decay_bias=0.02),
    "kaleidoscope": CarrierProfile("kaleidoscope", coord_transform=_coords_kaleidoscope, move_mul=0.85),
    "woven":        CarrierProfile("woven", field=_field_woven, move_mul=0.8, decay_bias=0.04),
}
DEFAULT_PROFILE = "ribbon_drift"


def carrier_profile(name: Optional[str]) -> CarrierProfile:
    """Resolve a profile by name; unknown / None -> the default ribbon-drift."""
    return CARRIER_PROFILES.get(name or DEFAULT_PROFILE, CARRIER_PROFILES[DEFAULT_PROFILE])


# ---------------------------------------------------------------------------
# the signature
# ---------------------------------------------------------------------------

@dataclass
class VisualSignature:
    """A small, authored-or-derived fingerprint of an oradio's look.

    Anchors (entry/exit) are the only frames a bridge truly needs; the rest (family, palette,
    motion, texture, density) steer which operator is chosen and how the carrier is tinted.
    """
    oradio_id: str
    family: str = "ribbon"                  # theme family: ribbon | smoke | void | ...
    palette: List[str] = field(default_factory=list)   # hex colors, [0] = dominant
    motion_vector: str = "static"           # sweep_left_to_right | clockwise | static | ...
    density: float = 0.5
    texture: str = "glass"
    entry_anchor: str = ""                  # path to the first-frame png (enter cleanly FROM)
    exit_anchor: str = ""                   # path to the last-frame png  (exit cleanly TO)
    loop: str = "loop.mp4"
    transition_mask: Optional[str] = None   # optional alpha mask path
    version: str = SIGNATURE_VERSION

    def to_dict(self) -> Dict[str, object]:
        return {
            "version": self.version,
            "oradio_id": self.oradio_id,
            "family": self.family,
            "palette": self.palette,
            "motion_vector": self.motion_vector,
            "density": self.density,
            "texture": self.texture,
            "entry_anchor": self.entry_anchor,
            "exit_anchor": self.exit_anchor,
            "loop": self.loop,
            "transition_mask": self.transition_mask,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_dict(cls, d: Dict[str, object]) -> "VisualSignature":
        return cls(
            oradio_id=str(d.get("oradio_id", "")),
            family=str(d.get("family", "ribbon")),
            palette=list(d.get("palette", []) or []),
            motion_vector=str(d.get("motion_vector", "static")),
            density=float(d.get("density", 0.5)),
            texture=str(d.get("texture", "glass")),
            entry_anchor=str(d.get("entry_anchor", "")),
            exit_anchor=str(d.get("exit_anchor", "")),
            loop=str(d.get("loop", "loop.mp4")),
            transition_mask=(str(d["transition_mask"]) if d.get("transition_mask") else None),
            version=str(d.get("version", SIGNATURE_VERSION)),
        )

    def has_anchors(self) -> bool:
        return bool(self.entry_anchor and self.exit_anchor
                    and Path(self.entry_anchor).exists() and Path(self.exit_anchor).exists())


# ---------------------------------------------------------------------------
# deriving a signature from a loop (ffmpeg)
# ---------------------------------------------------------------------------

def _run_bin(cmd: List[str]) -> bytes:
    """Like mint._run but captures raw bytes (for reading pixel data off ffmpeg stdout)."""
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        tail = (proc.stderr or b"").decode("utf-8", "replace").strip().splitlines()[-6:]
        raise MintError(f"{Path(cmd[0]).name} failed:\n" + "\n".join(tail))
    return proc.stdout


def _extract_frame(loop: Path, dst: Path, *, at_end: bool) -> Path:
    """Grab the first (at_end=False) or last (at_end=True) frame of a loop as a PNG anchor."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = [_tool("ffmpeg"), "-y"]
    if at_end:
        # seek ~one frame before EOF so we land on a real last frame, not past it.
        cmd += ["-sseof", "-0.08"]
    cmd += ["-i", str(loop), "-frames:v", "1", "-q:v", "2", str(dst)]
    _run(cmd)
    return dst


def dominant_color(loop: Path) -> str:
    """Average the loop down to a single pixel and return it as #rrggbb (the dominant palette)."""
    raw = _run_bin([
        _tool("ffmpeg"), "-v", "error", "-i", str(loop),
        "-vf", "scale=1:1", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1",
    ])
    if len(raw) < 3:
        return "#808080"
    r, g, b = raw[0], raw[1], raw[2]
    return f"#{r:02x}{g:02x}{b:02x}"


def derive_signature(
    loop: str | Path,
    *,
    oradio_id: str,
    out_dir: str | Path,
    family: str = "ribbon",
    motion_vector: str = "static",
    texture: str = "glass",
    density: float = 0.5,
    transition_mask: Optional[str] = None,
    palette: Optional[List[str]] = None,
) -> VisualSignature:
    """Derive a VisualSignature from a baked loop: bake entry/exit anchor PNGs + dominant color.

    family/motion/texture/density are authored hints (sensible defaults); palette is derived
    unless supplied. Anchors are written into out_dir as <id>.entry.png / <id>.exit.png.
    """
    loop = Path(loop)
    if not loop.exists():
        raise MintError(f"loop not found: {loop}")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    entry = _extract_frame(loop, out_dir / f"{oradio_id}.entry.png", at_end=False)
    exit_ = _extract_frame(loop, out_dir / f"{oradio_id}.exit.png", at_end=True)
    pal = palette if palette else [dominant_color(loop)]

    return VisualSignature(
        oradio_id=oradio_id,
        family=family,
        palette=pal,
        motion_vector=motion_vector,
        density=density,
        texture=texture,
        entry_anchor=str(entry),
        exit_anchor=str(exit_),
        loop=str(loop),
        transition_mask=transition_mask,
    )


# ---------------------------------------------------------------------------
# color helpers
# ---------------------------------------------------------------------------

def _parse_hex(c: str) -> Tuple[int, int, int]:
    c = (c or "").lstrip("#")
    if len(c) != 6:
        return (128, 128, 128)
    try:
        return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16))
    except ValueError:
        return (128, 128, 128)


def blend_hex(a: str, b: str, t: float = 0.5) -> str:
    """Linear blend of two #rrggbb colors; the carrier's neutral tint between two signatures."""
    ar, ag, ab = _parse_hex(a)
    br, bg, bb = _parse_hex(b)
    r = round(ar + (br - ar) * t)
    g = round(ag + (bg - ag) * t)
    bl = round(ab + (bb - ab) * t)
    return f"#{r:02x}{g:02x}{bl:02x}"


def _carrier_color(sig_from: VisualSignature, sig_to: VisualSignature) -> str:
    a = sig_from.palette[0] if sig_from.palette else "#808080"
    b = sig_to.palette[0] if sig_to.palette else "#808080"
    return blend_hex(a, b, 0.5)


# ---------------------------------------------------------------------------
# operators (each writes a transition clip to dst and returns it)
# ---------------------------------------------------------------------------

def _still(path_or_color: str, *, dur: float, size: Tuple[int, int], fps: int) -> Tuple[List[str], str]:
    """Build an ffmpeg input spec for a still source (a png path or a '#rrggbb' color).

    Returns (input_args, filter_prefix_label_unset) — caller wires the filter label.
    """
    w, h = size
    if path_or_color.startswith("#"):
        color = "0x" + path_or_color.lstrip("#")
        return (["-f", "lavfi", "-t", f"{dur}", "-i",
                 f"color=c={color}:s={w}x{h}:r={fps}"], "color")
    return (["-loop", "1", "-t", f"{dur}", "-i", path_or_color], "still")


def _chain(stills: List[str], dst: Path, *, dur: float, xfade: float,
           size: Tuple[int, int], fps: int) -> Path:
    """Concatenate N still segments (png paths or #colors) with xfade-dissolve seams between them.

    Each still holds `dur` seconds; consecutive stills crossfade over `xfade` seconds.
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    w, h = size
    inputs: List[str] = []
    norm: List[str] = []
    for i, s in enumerate(stills):
        in_args, _ = _still(s, dur=dur, size=size, fps=fps)
        inputs += in_args
        norm.append(
            f"[{i}:v]scale={w}:{h},fps={fps},format=yuv420p,setpts=PTS-STARTPTS[v{i}]"
        )

    # Fold the normalized segments together with successive xfades.
    filt = list(norm)
    prev = "v0"
    seg_len = dur  # running duration of the accumulated stream
    for i in range(1, len(stills)):
        out = f"x{i}"
        offset = max(0.0, seg_len - xfade)
        filt.append(
            f"[{prev}][v{i}]xfade=transition=dissolve:duration={xfade}:offset={offset}[{out}]"
        )
        prev = out
        seg_len = seg_len + dur - xfade

    cmd = [_tool("ffmpeg"), "-y"] + inputs + [
        "-filter_complex", ";".join(filt),
        "-map", f"[{prev}]", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(dst),
    ]
    _run(cmd)
    return dst


def op_morph(sig_from: VisualSignature, sig_to: VisualSignature, dst: Path, *,
             dur: float = 0.45, xfade: float = 0.45,
             size: Tuple[int, int] = DEFAULT_SIZE, fps: int = DEFAULT_FPS) -> Path:
    """GOOD rung: exit_anchor -> tinted neutral carrier -> entry_anchor (the ribbon morph)."""
    carrier = _carrier_color(sig_from, sig_to)
    return _chain([sig_from.exit_anchor, carrier, sig_to.entry_anchor],
                  dst, dur=dur, xfade=xfade, size=size, fps=fps)


def op_neutral_fade(sig_from: VisualSignature, sig_to: VisualSignature, dst: Path, *,
                    logo: Optional[str] = None, dur: float = 0.5, xfade: float = 0.5,
                    size: Tuple[int, int] = DEFAULT_SIZE, fps: int = DEFAULT_FPS) -> Path:
    """SAFE rung: exit_anchor -> neutral logo (or black void) -> entry_anchor. The safety net."""
    mid = logo if (logo and Path(logo).exists()) else "#000000"
    return _chain([sig_from.exit_anchor, mid, sig_to.entry_anchor],
                  dst, dur=dur, xfade=xfade, size=size, fps=fps)


def op_hardcut(sig_from: VisualSignature, sig_to: VisualSignature, dst: Path, *,
               dur: float = 0.25, xfade: float = 0.12,
               size: Tuple[int, int] = DEFAULT_SIZE, fps: int = DEFAULT_FPS) -> Path:
    """FALLBACK rung: exit_anchor -> entry_anchor with only a tiny dissolve (a near hard cut)."""
    return _chain([sig_from.exit_anchor, sig_to.entry_anchor],
                  dst, dur=dur, xfade=xfade, size=size, fps=fps)


# ---------------------------------------------------------------------------
# the CARRIER (hero rung): live loops under a deterministic seeded color-storm
# ---------------------------------------------------------------------------
# Ported from the proven prototype (exports/crossover_demo/_build_carrier.py). Fully deterministic:
# every lane is drawn from md5(edge_key); motion is pure feedback advection of a static seeded
# vortex field. "Our signature is transitions" — 10+ seeded lanes => each edge is unique, yet a
# replay is byte-identical. Changes here must be ADDITIVE (more lanes), never iron out behaviours.

def _carrier_loop_frames(path: str | Path, size: Tuple[int, int]) -> List[Any]:
    if not HAS_CV2:
        raise MintError("carrier needs opencv (cv2) + numpy")
    cap = cv2.VideoCapture(str(path))
    frames = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(cv2.resize(f, size).astype(np.float32))
    cap.release()
    if not frames:
        raise MintError(f"no frames decoded from loop: {path}")
    return frames


def _vivid(img, s):
    g = img.mean(axis=2, keepdims=True)
    return np.clip(g + (img - g) * s, 0, 255)


def _hsv_bgr(h, s, v):
    px = np.uint8([[[int(h / 2) % 180, int(s), int(v)]]])
    return cv2.cvtColor(px, cv2.COLOR_HSV2BGR)[0, 0].astype(np.float32)


def carrier_frames(loop_from: str | Path, loop_to: str | Path, *, edge_key: str,
                   vigor: float = 0.7, seconds: Optional[float] = None,
                   fps: int = CARRIER_FPS, size: Tuple[int, int] = CARRIER_SIZE,
                   profile: Optional[str] = None) -> List[Any]:
    """Render the directional transition frames: from-loop live -> seeded swirling storm (dissolve
    at the MIDDLE) -> to-loop live, last frame == to-loop frame 0. Deterministic for
    (edge_key, vigor, size, profile). `seconds=None` => a seeded LENGTH (3-6s) from the edge_key.

    `profile` selects a transition PERSONALITY (see CARRIER_PROFILES) — same renderer, a different
    velocity field / coord transform / feedback. None == 'ribbon_drift', the original (byte-identical
    to before profiles existed)."""
    if not HAS_CV2:
        raise MintError("carrier needs opencv (cv2) + numpy")
    w2, h2 = int(size[0]), int(size[1])
    sw = w2 / _CARRIER_REF_W
    fa = _carrier_loop_frames(loop_from, (w2, h2))
    fb = _carrier_loop_frames(loop_to, (w2, h2))
    na, nb = len(fa), len(fb)
    gy, gx = np.mgrid[0:h2, 0:w2]
    gx = gx.astype(np.float32); gy = gy.astype(np.float32)

    seed = int(hashlib.md5(edge_key.encode()).hexdigest()[:8], 16)
    rng = np.random.default_rng(seed)

    # seeded LENGTH lane (drawn FIRST so it's stable per edge): each edge has its own repeatable
    # duration; entry & exit use different edge_keys, so they can differ in length.
    if seconds is None:
        seconds = float(rng.uniform(*CARRIER_SECONDS_RANGE))
    n = int(round(seconds * fps))

    # ---- seeded variance lanes (ADDITIVE; add more, never remove) ----
    K = int(rng.integers(3, 8))
    vx = rng.uniform(0.05, 0.95, K) * w2
    vy = rng.uniform(0.05, 0.95, K) * h2
    vspin = rng.uniform(0.7, 2.0, K) * rng.choice([-1.0, 1.0], K)
    vrad = rng.uniform(0.18, 0.6, K) * w2
    vpull = rng.uniform(-0.5, 0.45, K)
    turb_f = rng.uniform(0.004, 0.013) * sw
    turb_ph = rng.uniform(0, 6.28)
    hue1 = rng.uniform(0, 360)
    hue_mid = (hue1 + rng.uniform(30, 150)) % 360
    hue2 = (hue1 + rng.uniform(120, 300)) % 360
    c_lo = _hsv_bgr(hue1, 255, 120); c_mid = _hsv_bgr(hue_mid, 255, 200); c_hi = _hsv_bgr(hue2, 255, 255)
    tint = rng.uniform(0.45, 0.78)
    flow_sign = float(rng.choice([-1.0, 1.0]))
    bell_k = rng.uniform(0.7, 1.15)
    diss_w = rng.uniform(0.05, 0.20)
    contrast = rng.uniform(1.15, 1.45)
    bg_floor = rng.uniform(0.02, 0.15)
    bloom2_mul = rng.uniform(2.5, 5.0); bloom2_w = rng.uniform(0.08, 0.32)
    jdecay = rng.uniform(-0.03, 0.03); jgain = rng.uniform(-0.15, 0.15)
    jglow = rng.uniform(-1.0, 2.0)

    move = (3.0 + 16.0 * vigor) * sw
    decay = float(np.clip(0.80 + 0.12 * vigor + jdecay, 0.6, 0.95))
    gain = 0.9 + 0.4 * vigor + jgain
    cover = 0.55 + 0.40 * vigor
    sat = 1.4 + 0.7 * vigor
    glow_sigma = max(1.2, (2.0 + 5.0 * vigor + jglow) * sw)
    glow_w = 0.14 + 0.18 * vigor
    spark_w = 0.15 + 0.20 * vigor
    dark = 0.65

    fx = np.zeros((h2, w2), np.float32); fy = np.zeros((h2, w2), np.float32)
    eps = 1e-3
    for k in range(K):
        dx = gx - vx[k]; dy = gy - vy[k]
        dist = np.sqrt(dx * dx + dy * dy) + eps
        infl = np.exp(-(dist / vrad[k]) ** 2) * vspin[k]
        fx += (-dy / dist) * infl + (dx / dist) * vpull[k] * infl
        fy += (dx / dist) * infl + (dy / dist) * vpull[k] * infl
    fx += np.sin(gy * turb_f + turb_ph) * 0.6
    fy += np.cos(gx * turb_f + turb_ph) * 0.6
    norm = np.percentile(np.sqrt(fx * fx + fy * fy), 90) + eps
    fx = fx / norm * flow_sign; fy = fy / norm * flow_sign

    # ---- PERSONALITY: a profile may REPLACE the velocity field (drawing its own rng AFTER all the
    # default lanes, so 'ribbon_drift' stays byte-identical) and reshape motion/feedback/particles
    # and add a sample-space transform (kaleidoscope). Default profile = a no-op. ----
    prof = carrier_profile(profile)
    if prof.field is not None:
        fx, fy = prof.field(gx, gy, w2, h2, sw, rng, vigor)
        norm = np.percentile(np.sqrt(fx * fx + fy * fy), 90) + eps
        fx = (fx / norm).astype(np.float32); fy = (fy / norm).astype(np.float32)
    move = move * prof.move_mul
    decay = float(np.clip(decay + prof.decay_bias, 0.6, 0.985))
    gain = gain * prof.gain_mul
    bell_k = bell_k * prof.bell_k_mul
    # Kaleidoscope-style coord transform (target sample coords), blended in per-frame by purity.
    tf_x = tf_y = None
    if prof.coord_transform is not None:
        tf_x, tf_y = prof.coord_transform(gx, gy, w2, h2)

    map_x = (gx - fx * move).astype(np.float32)
    map_y = (gy - fy * move).astype(np.float32)

    P = int((800 + 4000 * vigor) * (w2 * h2) / (_CARRIER_REF_W * 720) * prof.particle_mul)
    px = rng.uniform(0, w2, P).astype(np.float32)
    py = rng.uniform(0, h2, P).astype(np.float32)
    pbright = rng.uniform(0.6, 1.4, P).astype(np.float32)

    trail = np.zeros((h2, w2, 3), np.float32)
    frames = []
    for i in range(n):
        t = i / (n - 1)
        bell = float(np.sin(np.pi * t) ** bell_k)
        ai = int((t * na)) % na          # A starts at frame 0 (t=0)
        bi = int(((t - 1) * nb)) % nb     # B ends at frame 0 (t=1)
        wgt = float(np.clip((t - (0.5 - diss_w)) / (2 * diss_w), 0.0, 1.0))
        wgt = wgt * wgt * (3 - 2 * wgt)
        base = fa[ai] * (1 - wgt) + fb[bi] * wgt
        src0 = _vivid(base, sat)
        cmax = src0.max(axis=2); cmin = src0.min(axis=2)
        sat_mask = (cmax - cmin) / (cmax + 1.0)
        lum = src0.mean(axis=2) / 255.0
        content = np.maximum(sat_mask, np.clip((lum - 0.3) / 0.7, 0, 1) * 0.7)
        inj_w = (bg_floor + (1.0 - bg_floor) * content)[..., None]
        half = np.clip(lum * 2, 0, 1)[..., None]
        half2 = np.clip(lum * 2 - 1, 0, 1)[..., None]
        duo = c_lo[None, None, :] * (1 - half) + c_mid[None, None, :] * half
        duo = duo * (1 - half2) + c_hi[None, None, :] * half2
        src = src0 * (1 - tint) + duo * tint

        advected = cv2.remap(trail, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        trail = decay * advected + (1.0 - decay) * src * (bell * gain) * inj_w

        xi = px.astype(np.int32) % w2; yi = py.astype(np.int32) % h2
        px = (px - fx[yi, xi] * move) % w2
        py = (py - fy[yi, xi] * move) % h2
        spark = np.zeros((h2, w2, 3), np.float32)
        np.add.at(spark, (yi, xi), src[yi, xi] * (pbright[:, None] * bell * content[yi, xi][:, None]))
        trail = np.clip(trail + spark * spark_w, 0, 255)

        glow = (cv2.GaussianBlur(trail, (0, 0), glow_sigma) * glow_w
                + cv2.GaussianBlur(trail, (0, 0), glow_sigma * bloom2_mul) * bloom2_w)
        backdrop = base * (1 - cover * bell) * (1 - dark * bell)
        # PURITY RAMP: the storm + colour-grade ramp to ZERO at both ends (purity = bell), so the
        # first frame == the pure from-loop frame and the last == the pure to-loop frame. The loops
        # are NOT colour-graded, so this guarantees a seamless splice into the loop (full grade in
        # the middle where it sells; ungraded at the seams). Keeps every lane -- just scopes them.
        purity = bell
        out = backdrop + (trail + glow) * purity
        eff_contrast = 1.0 + (contrast - 1.0) * purity
        out = np.clip((out - 110.0) * eff_contrast + 110.0, 0, 255)
        if tf_x is not None:
            # blend identity -> kaleidoscope by purity so frame 0 / last stay the pure loop (clean seam)
            bx = (gx * (1.0 - purity) + tf_x * purity).astype(np.float32)
            by = (gy * (1.0 - purity) + tf_y * purity).astype(np.float32)
            out = cv2.remap(out, bx, by, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        out = out.astype(np.uint8)
        frames.append(out)
    return frames


def _write_frames(frames: List[Any], dst: str | Path, fps: int,
                  size: Tuple[int, int]) -> Path:
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    raw = dst.with_name("_" + dst.stem + ".raw.mp4")
    vw = cv2.VideoWriter(str(raw), cv2.VideoWriter_fourcc(*"mp4v"), fps, (int(size[0]), int(size[1])))
    for f in frames:
        vw.write(f)
    vw.release()
    try:
        _run([_tool("ffmpeg"), "-y", "-v", "error", "-i", str(raw),
              "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(dst)])
    finally:
        raw.unlink(missing_ok=True)
    return dst


def swap_edge_key(key: str) -> str:
    """'loom:A__B' -> 'loom:B__A' (the reverse direction's seed) so the exit is its own edge."""
    prefix, _, rest = key.partition(":") if ":" in key else ("", "", key)
    if "__" in rest:
        a, b = rest.split("__", 1)
        rest = f"{b}__{a}"
    return f"{prefix}:{rest}" if prefix else rest


def carrier_transition(loop_from: str | Path, loop_to: str | Path, dst_entry: str | Path,
                       dst_exit: Optional[str | Path] = None, *, edge_key: str,
                       exit_edge_key: Optional[str] = None, vigor: float = 0.7,
                       seconds: Optional[float] = None, fps: int = CARRIER_FPS,
                       size: Tuple[int, int] = CARRIER_SIZE,
                       profile: Optional[str] = None) -> Dict[str, Path]:
    """Render the entry (from->to) and, if dst_exit given, the exit as an INDEPENDENT directional
    carrier (to->from, seeded by the swapped key). Each direction has its own seeded length (when
    seconds=None), so entry and exit of a combo can differ in length -- both fully repeatable.
    `profile` selects the transition personality for both directions (see CARRIER_PROFILES)."""
    ef = carrier_frames(loop_from, loop_to, edge_key=edge_key, vigor=vigor,
                        seconds=seconds, fps=fps, size=size, profile=profile)
    out = {"entry": _write_frames(ef, dst_entry, fps, size)}
    if dst_exit is not None:
        ekey = exit_edge_key or swap_edge_key(edge_key)
        xf = carrier_frames(loop_to, loop_from, edge_key=ekey, vigor=vigor,
                            seconds=seconds, fps=fps, size=size, profile=profile)
        out["exit"] = _write_frames(xf, dst_exit, fps, size)
    return out


def op_carrier(sig_from: VisualSignature, sig_to: VisualSignature, dst: str | Path, *,
               edge_key: str, vigor: float = 0.7, seconds: Optional[float] = None,
               fps: int = CARRIER_FPS, size: Tuple[int, int] = CARRIER_SIZE,
               profile: Optional[str] = None) -> Path:
    """Ladder rung wrapper: render the carrier ENTRY from the two signatures' loop videos."""
    frames = carrier_frames(sig_from.loop, sig_to.loop, edge_key=edge_key, vigor=vigor,
                            seconds=seconds, fps=fps, size=size, profile=profile)
    return _write_frames(frames, dst, fps, size)


# ---------------------------------------------------------------------------
# the ATTRACT loop (push-to-start): a seamless idle derived from the bookmark door
# ---------------------------------------------------------------------------
# A FORK of the carrier, modified for a different job. The carrier is a one-shot A->B storm (a
# bell that ramps up then down, with a mid dissolve). The attract loop is the opposite: it must
# LOOP SEAMLESSLY (first frame == last frame) and stay CALM (it's an idle, "push start" screen).
#
# It keeps the bookmark door's own loop fully visible (so the PTS is themed to the loom you're
# loading into) and adds SMOKE that trails off the most distinct, dense-coloured parts of it: the
# vivid ribbon regions shed coloured smoke that drifts on a gentle seeded current. "Move the mouse
# and RibbonOS wakes up" -> the boot/entry chain takes over.
#
# Seamlessness with a feedback (smoke) buffer is solved by rendering `n + cf` frames with the
# source sampled PERIODICALLY (period n) and continuous feedback, then crossfading the head `cf`
# frames against their one-period-later continuation -> the wrap (frame n-1 -> frame 0) is exact.
# Every loom's PTS differs (seeded lanes: current, vortices, smoke density/decay, breath, glow),
# yet a replay is byte-identical -- "signature look within a scoped range," not one hard look.

def attract_loop_frames(loop: str | Path, *, key: str, vigor: float = 0.5,
                        seconds: Optional[float] = None, fps: int = ATTRACT_FPS,
                        size: Tuple[int, int] = ATTRACT_SIZE) -> List[Any]:
    """Render a SEAMLESS attract/PTS loop from a single source loop (the bookmark door's loop),
    with coloured smoke trailing off its densest regions. Deterministic for (key, vigor, size)."""
    if not HAS_CV2:
        raise MintError("attract loop needs opencv (cv2) + numpy")
    w2, h2 = int(size[0]), int(size[1])
    sw = w2 / _CARRIER_REF_W
    src = _carrier_loop_frames(loop, (w2, h2))   # the door loop (already a seamless palindrome)
    ns = len(src)
    gy, gx = np.mgrid[0:h2, 0:w2]
    gx = gx.astype(np.float32); gy = gy.astype(np.float32)

    seed = int(hashlib.md5(key.encode()).hexdigest()[:8], 16)
    rng = np.random.default_rng(seed)

    # seeded LENGTH lane (drawn first so it's stable per key)
    if seconds is None:
        seconds = float(rng.uniform(*ATTRACT_SECONDS_RANGE))
    n = int(round(seconds * fps))

    # ---- seeded variance lanes (ADDITIVE; calm/idle ranges, not a storm) ----
    K = int(rng.integers(2, 5))                       # fewer, gentler eddies than the carrier
    vx = rng.uniform(0.1, 0.9, K) * w2
    vy = rng.uniform(0.1, 0.9, K) * h2
    vspin = rng.uniform(0.25, 0.8, K) * rng.choice([-1.0, 1.0], K)
    vrad = rng.uniform(0.25, 0.7, K) * w2
    turb_f = rng.uniform(0.003, 0.009) * sw
    turb_ph = rng.uniform(0, 6.28)
    # the SMOKE drift: a steady current, biased UPWARD (smoke rises) with a seeded lean.
    lean = rng.uniform(-0.5, 0.5)                      # left/right lean of the rising smoke
    drift = np.array([lean, -1.0], np.float32)
    drift = drift / (np.linalg.norm(drift) + 1e-6)
    dense_thresh = float(rng.uniform(0.42, 0.66))      # how selective the smoke sources are
    smoke_decay = float(np.clip(0.88 + 0.08 * vigor, 0.84, 0.97))  # how long smoke lingers
    smoke_gain = 0.7 + 0.8 * vigor
    smoke_op = 0.55 + 0.5 * vigor                      # smoke opacity over the live door
    breath_amp = float(rng.uniform(0.015, 0.06))       # gentle luminance pulse of the door
    breath_ph = rng.uniform(0, 6.28)
    sat = 1.15 + 0.35 * vigor
    tint_hue = rng.uniform(0, 360)
    tint_amt = float(rng.uniform(0.0, 0.22))           # faint colour bias of the smoke
    tint_col = _hsv_bgr(tint_hue, 220, 255)
    glow_sigma = max(1.2, (2.5 + 4.0 * vigor) * sw)
    glow_w = 0.12 + 0.14 * vigor
    bloom_mul = rng.uniform(2.6, 4.2); bloom_w = 0.06 + 0.10 * vigor

    # static drift+swirl field (constant current + gentle eddies); feedback advects the smoke.
    fx = np.full((h2, w2), drift[0], np.float32) * 1.4
    fy = np.full((h2, w2), drift[1], np.float32) * 1.4
    eps = 1e-3
    for k in range(K):
        dx = gx - vx[k]; dy = gy - vy[k]
        dist = np.sqrt(dx * dx + dy * dy) + eps
        infl = np.exp(-(dist / vrad[k]) ** 2) * vspin[k]
        fx += (-dy / dist) * infl
        fy += (dx / dist) * infl
    fx += np.sin(gy * turb_f + turb_ph) * 0.4
    fy += np.cos(gx * turb_f + turb_ph) * 0.4
    norm = np.percentile(np.sqrt(fx * fx + fy * fy), 90) + eps
    rise = (3.5 + 7.0 * vigor) * sw                    # smoke travel per frame (gentle)
    fx = fx / norm; fy = fy / norm
    map_x = (gx - fx * rise).astype(np.float32)
    map_y = (gy - fy * rise).astype(np.float32)

    def _compose(trail, t):
        si = int(t * ns) % ns
        base = src[si]
        breath = 1.0 + breath_amp * np.sin(2 * np.pi * t + breath_ph)
        src0 = np.clip(_vivid(base, sat) * breath, 0, 255)
        cmax = src0.max(axis=2); cmin = src0.min(axis=2)
        sat_mask = (cmax - cmin) / (cmax + 1.0)
        lum = src0.mean(axis=2) / 255.0
        content = np.clip(sat_mask * np.clip((lum - 0.12) / 0.88, 0, 1), 0, 1)
        # the MOST distinct dense-coloured parts emit smoke (soft threshold above dense_thresh)
        dense = np.clip((content - dense_thresh) / (1.0 - dense_thresh + 1e-6), 0, 1)[..., None]
        emit = src0 * dense
        if tint_amt > 0:
            emit = emit * (1 - tint_amt) + tint_col[None, None, :] * (emit.mean(axis=2, keepdims=True)
                                                                      / 255.0) * tint_amt * 255.0
        advected = cv2.remap(trail, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        trail = smoke_decay * advected + (1.0 - smoke_decay) * emit * smoke_gain
        glow = (cv2.GaussianBlur(trail, (0, 0), glow_sigma) * glow_w
                + cv2.GaussianBlur(trail, (0, 0), glow_sigma * bloom_mul) * bloom_w)
        out = np.clip(base + (trail + glow) * smoke_op, 0, 255)
        return trail, out

    # settle the smoke field for ~half a period so the recorded loop starts in steady state
    trail = np.zeros((h2, w2, 3), np.float32)
    for i in range(int(0.5 * n)):
        trail, _ = _compose(trail, (i % n) / n)

    # render n + cf frames (source periodic with n, continuous feedback)
    cf = max(2, int(round(0.16 * n)))
    rendered: List[Any] = []
    for i in range(n + cf):
        trail, out = _compose(trail, (i % n) / n)
        rendered.append(out)

    # seamless wrap: head `cf` frames crossfade from their one-period-later continuation back to
    # themselves, so frame n-1 -> frame 0 is exactly continuous on loop.
    frames: List[Any] = []
    for i in range(n):
        if i < cf:
            w = i / cf
            blended = rendered[n + i] * (1.0 - w) + rendered[i] * w
            frames.append(np.clip(blended, 0, 255).astype(np.uint8))
        else:
            frames.append(rendered[i].astype(np.uint8))
    return frames


def build_attract_loop(loop: str | Path, dst: str | Path, *, key: str, vigor: float = 0.5,
                       seconds: Optional[float] = None, fps: int = ATTRACT_FPS,
                       size: Tuple[int, int] = ATTRACT_SIZE) -> Path:
    """Render + encode a seamless attract/PTS loop to `dst`. Seeded by `key` (replayable)."""
    frames = attract_loop_frames(loop, key=key, vigor=vigor, seconds=seconds, fps=fps, size=size)
    return _write_frames(frames, dst, fps, size)


# ---------------------------------------------------------------------------
# the ladder
# ---------------------------------------------------------------------------

@dataclass
class TransitionResult:
    rung: str            # which rung produced the clip (custom/morph/neutral/hardcut)
    path: Path
    operator: str        # human label
    degraded: bool       # True if a higher rung was attempted and failed


def select_rungs(sig_from: VisualSignature, sig_to: VisualSignature, *,
                 custom: Optional[str] = None, logo: Optional[str] = None) -> List[str]:
    """PURE: the ordered degradation chain of rungs to attempt, best applicable first.

    Separated from execution so the ladder logic is testable without ffmpeg.
    """
    chain: List[str] = []
    if custom and Path(custom).exists():
        chain.append(RUNG_CUSTOM)
    loops = (HAS_CV2 and bool(sig_from.loop) and bool(sig_to.loop)
             and Path(sig_from.loop).exists() and Path(sig_to.loop).exists())
    if loops:
        chain.append(RUNG_CARRIER)   # hero: live loops + seeded color-storm
    anchors = sig_from.has_anchors() and sig_to.has_anchors()
    if anchors and sig_from.family == sig_to.family:
        chain.append(RUNG_MORPH)
    if anchors:
        chain.append(RUNG_NEUTRAL)   # safe net works cross-family (fades through neutral)
        chain.append(RUNG_HARDCUT)   # ultimate fallback
    if not chain:
        # No loops, no anchors, no custom clip — nothing deterministic to build.
        return []
    return chain


def bridge(sig_from: VisualSignature, sig_to: VisualSignature, dst: str | Path, *,
           custom: Optional[str] = None, logo: Optional[str] = None,
           edge_key: Optional[str] = None, vigor: float = 0.7,
           size: Tuple[int, int] = DEFAULT_SIZE, fps: int = DEFAULT_FPS) -> TransitionResult:
    """Build the cheapest VALID transition from sig_from -> sig_to, degrading on failure.

    Walks select_rungs() top-down: tries each rung, and if it fails, falls to the next rung down
    the ladder. The carrier rung is seeded by edge_key (defaults to the two oradio ids) so the
    same edge always replays the same storm. Returns which rung actually produced the clip.
    """
    dst = Path(dst)
    if not edge_key:
        edge_key = f"{sig_from.oradio_id}__{sig_to.oradio_id}"
    chain = select_rungs(sig_from, sig_to, custom=custom, logo=logo)
    if not chain:
        raise MintError(
            "cannot bridge: no loops, no anchors, and no custom clip were provided"
        )

    last_err: Optional[Exception] = None
    for idx, rung in enumerate(chain):
        try:
            if rung == RUNG_CUSTOM:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(custom, dst)  # type: ignore[arg-type]
                op = "custom authored clip"
            elif rung == RUNG_CARRIER:
                op_carrier(sig_from, sig_to, dst, edge_key=edge_key, vigor=vigor, fps=fps)
                op = "fluid carrier (live loops + seeded color-storm)"
            elif rung == RUNG_MORPH:
                op_morph(sig_from, sig_to, dst, size=size, fps=fps)
                op = "signature morph (exit -> tinted carrier -> entry)"
            elif rung == RUNG_NEUTRAL:
                op_neutral_fade(sig_from, sig_to, dst, logo=logo, size=size, fps=fps)
                op = "neutral fade (exit -> logo/void -> entry)"
            else:  # RUNG_HARDCUT
                op_hardcut(sig_from, sig_to, dst, size=size, fps=fps)
                op = "hard cut + short dissolve"
            return TransitionResult(rung=rung, path=dst, operator=op, degraded=(idx > 0))
        except Exception as e:  # noqa: BLE001 - degrade to the next rung
            last_err = e
            continue

    raise MintError(f"all transition rungs failed; last error: {last_err}")


def write_signature(sig: VisualSignature, dst: str | Path) -> Path:
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(sig.to_json(), encoding="utf-8")
    return dst


def read_signature(path: str | Path) -> VisualSignature:
    return VisualSignature.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
