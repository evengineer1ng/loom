# Putting loom on HuggingFace

Two artifacts, one question. The **Space** lets them *hear* it; the **benchmark** makes them
*test* it.

## 1. The Static Space (zero backend — it just runs)
HuggingFace Spaces has a `static` SDK: your HTML *is* the app. No model, no server — which is the
whole point, and proof in itself.

1. `huggingface.co/new-space` → **SDK: Static**.
2. Put these at the Space repo root (copy from this repo's `docs/`):
   - `index.html`  (the artifact — the landing page)
   - `booth.html`  (the faders + lexical pitch)
   - `ncm.html`    (the Night City portal, REPLAY mode)
3. Give the Space's `README.md` this frontmatter:

```yaml
---
title: loom — a tape, sung
emoji: 🧵
colorFrom: indigo
colorTo: yellow
sdk: static
pinned: false
---
```

That's it — it serves `index.html`, runs in their browser, ~10KB.
(`ncm.html` runs in its read-only REPLAY mode on the Space; LIVE control needs the local relay.)

## 2. The benchmark (the thing that earns engagement)
Point them at [`bench/`](../bench) — a deterministic encoder that mints unlimited labeled
`(text → audio)` pairs, a scorer, and a non-ML baseline (~43% word accuracy) to beat. The task:
**decode the audio back to the text.** If they can, it's a language.

## How to post (in order of leverage)
- **HF Post** (the feed on hf.co) + a **Forum** thread (discuss.huggingface.co → *Research* or
  *Show and tell*). Draft:

> Built a deterministic codec that turns any event stream — a race, a heartbeat, a sentence — into
> sung language. No model, no server, ~10KB. Each word maps to a fixed musical motif, so it's
> **reversible**.
> Two questions for this crowd:
> 1. It emits unlimited (text→audio) pairs for free, and a pitch-only baseline already decodes ~43%.
>    **Can you train a model to beat that and recover the text?** If you can, it's a language.
> 2. Where's the real line between what a deterministic codec can *faithfully* say vs what genuinely
>    needs a generative model?
> Live in your browser: [Space link] · benchmark: [repo link]. Roast it.

**Framing note:** don't ask "is it AI?" — ask the decode challenge. It turns *"no model"* from a
shrug into a puzzle, and the absence of weights becomes the interesting part. Stay humble: it's
*a* proof and a concrete task, not a manifesto.
