# loom can sing & play — the sampler (no ML, no GPU)

A song is a tape; a voice or instrument is a **sample**. The sampler renders a note-tape into audio
by pitch-shifting + timing + concatenating ONE recorded sample. **Borrowed timbre, deterministic
arrangement** — byte-identical, no model. The loom thesis, in sound.

## Run it now (synth placeholder proves the pipeline)
```sh
python -m tools.sing --synth --notes "C4 D4 E4 F4 G4 A4 B4 C5" --out transcripts/scale.wav
```
Prints an **FFT pitch-correctness check** per note — the deterministic receipt. (Timbre realness is
your ears + an ABX test; this proves the pitch math.)

## Real timbre via Freesound (CC-licensed)
Free token at <https://freesound.org/apiv2/apply>, then `export FREESOUND_API_KEY=...`:
```sh
python -m tools.sing --query "cello single note"           --notes "C4 E4 G4 C5"   # instrument — the win
python -m tools.sing --query "opera vowel ah sustained"    --notes "C4 G4 C5"      # voice — the frontier
```
Freesound previews are CC — the author is printed on fetch; **attribute them.**

## Honest scope
- **Instruments are the solved case.** This is a SoundFont/sampler — a 30-year-proven, deterministic,
  human-sounding technique. Get the win here first.
- **Voice/opera is the frontier.** The POC pitch-shifts by resampling, so formants shift too
  ("chipmunk" on big jumps). The real-engine upgrade is a **formant-preserving phase vocoder** +
  **vibrato/expression**. The opera ABX test probes how far the deterministic mirror climbs.
- **The genre/voice knob** = swap the sample (a Freesound query) + expression params (vibrato, attack,
  swing). It's the grammar-voice fader, one layer down — live-swappable. Wiring it into the booth as a
  "sing" mode is the next step.
