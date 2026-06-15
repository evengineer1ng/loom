# loomspeech — a decode benchmark

**Claim under test:** loom deterministically compresses text into sung audio. If that audio is a
*language*, a model should be able to **listen and recover the text.** This benchmark hands you an
encoder that mints unlimited, free, perfectly-labeled `(text → audio)` pairs and asks you to invert
it.

## The task
Given a `.wav`, predict the source text. The encoder maps each **word → a fixed 1–3 note motif**
(on an A-minor pentatonic scale) sung on the word's own vowels. Same word → same sound, forever, on
any machine — so labels are free and infinite.

```sh
pip install soundfile numpy
python bench/encode.py --builtin --n 2000 --out data/ls     # mint 2000 labeled pairs (no input needed)
python bench/encode.py --corpus my_lines.txt --out data/ls  # or your own text, one line per utterance
# ... train / write a decoder that emits predictions.jsonl: {"id": N, "text": "..."} per line ...
python bench/score.py data/ls/manifest.jsonl predictions.jsonl
```

## Metrics
- **exact-line accuracy** — whole utterance recovered, in order.
- **word accuracy** — position-wise word matches.

## Baseline (the floor to beat)
`bench/baseline.py` — **no ML**: split on silence → FFT pitch per note → snap to a scale degree →
greedy-match the degree sequence against the known lexicon. It ignores vowels and timbre entirely.

```sh
python bench/baseline.py data/ls/manifest.jsonl data/ls > preds.jsonl
python bench/score.py data/ls/manifest.jsonl preds.jsonl
```
On 120 built-in pairs: **~43% word accuracy, ~20% exact-line.** That's pitch-only with a known
vocabulary. The headroom is the point:
- the **vowels** carry the signal a pitch-only decoder throws away (→ out-of-vocabulary words),
- motif **collisions** and **segmentation** errors cap a naive parser,
- a real model should need **no lexicon** and should **survive noise** (add some and see).

## The two questions (what to actually answer)
1. **Is it a language?** How close to 100% can a model decode the audio back to text? If high, the
   codec carries the meaning losslessly — it *is* a language, learnable by ear or by net.
2. **Where's the boundary?** loom is the deterministic extreme — faithful, ~free, no model. Where
   does a generative model actually become *necessary* vs a deterministic codec being enough?

## Determinism
`word_motif` is a clean uint32 hash → the mapping is identical on every machine and run. The
encoder has no model, no randomness (a fixed breath seed only). Regenerate the same data anywhere.
Interactive cousin: the booth (`docs/booth.html`, pitch → "word = note").
