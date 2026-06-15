# loom on Android — no GPU, no cloud, KB files

The deterministic runtime is pure Python + stdlib + PyYAML, so it runs on a phone via **Termux**.
**Playing a loom needs no model at all** — only *authoring a new one* uses an LLM (and that can be
a 4B running locally, or done once on a bigger machine and the KB artifact copied over).

## Run an existing loom (zero model, zero GPU)
```sh
pkg install python
pip install pyyaml
git clone https://github.com/evengineer1ng/loom && cd loom

# speech (optional): install the Termux:API app, then:
pkg install termux-api          # provides termux-tts-speak; loom auto-detects it

python -m tools.loomify --tape data/f1_barcelona_2026.json --voice town_crier --speak
```
This is the whole "Siri but loom" runtime: a few-KB tape → spoken narration, instantly, offline.

## Author a new loom on-device (uses a small local model)
Run a 4B-class model locally (e.g. Ollama in Termux/proot, or any OpenAI-compatible server), then
point loom at it — nothing is hardcoded:
```sh
export LOOM_LLM_ENDPOINT=http://127.0.0.1:11434/api/generate   # local Ollama (default)
export LOOM_LLM_MODEL=qwen2.5:3b                               # whatever your phone can run
python -m tools.loomify --idea "my heart rate as a poet" --speak
```
Or use a cloud model from the phone (no local model needed):
```sh
export LOOM_LLM=openai LOOM_LLM_BASE=https://api.openai.com/v1 LOOM_LLM_KEY=sk-...
export LOOM_LLM_MODEL=gpt-4o-mini
python -m tools.loomify --idea "soup http" --speak
```

## Why this fits a phone (and Siri doesn't)
Siri thinks on every utterance. Loom thinks **once** (authoring → a KB declaration), then **replays
deterministically** forever — no model in the hot path. The expensive part is amortized into bytes;
the runtime is featherweight. TTS is the only OS-specific bit, and `speech_out.py` covers Windows
(SAPI), macOS (`say`), Linux (`espeak`), and Android (`termux-tts-speak`) — set `LOOM_TTS` to force one.
"""
