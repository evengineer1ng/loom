"""The meta-layer: turn ANY domain idea into a running deterministic narrator.

You describe a domain (even an absurd one). A local LLM authors a small loom pipeline — a sample
TAPE (role-tagged rows) + a GRAMMAR (voice) — under a STRICT schema. We then VALIDATE by actually
running it through the deterministic engine; if it doesn't parse/compile/narrate, we feed the error
back and retry. Output is the narration + the saved artifacts. The model authors once; the engine
renders deterministically (faithful-by-construction, proven in tests/test_receipts.py).

This is "vibe coders make no mistakes": the guarantee is the VALIDATOR, not the prompt — anything
that doesn't run is rejected. Declarative only (no arbitrary code executed).

    python -m tools.loomify --model qwen3:8b "a haunted office printer"
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.request

from oradio_engine.speech import Grammar

OLLAMA = "http://127.0.0.1:11434/api/generate"
VERBS = json.load(open("data/english/irregular_verbs.json", encoding="utf-8"))

SCHEMA = """Output ONLY a JSON object: {"tape": [...rows...]}.
A row = {"tags": ["actor:NAME","action:VERB","object:THING","magnitude:NUMBER","unit:UNIT","valence:hype|alarm|calm"],
         "priority": 0.7}. Rules:
- actor and action are REQUIRED. action MUST be a plain present-tense verb lemma (spike, drop, jam,
  open, fail, whisper) — the engine conjugates it to past tense itself. Do NOT past-tense it.
- object/magnitude/unit/valence optional. valence is exactly one of hype/alarm/calm if present.
- Reuse the SAME few actor names across rows so a thread forms. 7 rows telling a tiny story.
Output JSON only, no prose."""


def gen(prompt, model):
    body = {"model": model, "prompt": prompt, "stream": False, "think": False,
            "options": {"temperature": 0.4, "num_predict": 700}}
    req = urllib.request.Request(OLLAMA, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    resp = json.load(urllib.request.urlopen(req, timeout=180))
    return re.sub(r"(?is)<think>.*?</think>", "", resp.get("response") or "")


def loomify(idea, model, grammar_file, feedback=""):
    prompt = f"{SCHEMA}\n\nDOMAIN IDEA: \"{idea}\"\n{feedback}"
    raw = gen(prompt, model)
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        raise ValueError("no JSON in output")
    obj = json.loads(m.group(0))
    tape = obj["tape"]
    g = Grammar.from_file(grammar_file, verbs="data/english/irregular_verbs.json")  # vetted voice, reused
    lines = []
    for row in tape:
        roles = {}
        for t in row.get("tags", []):
            if ":" in t:
                k, v = t.split(":", 1)
                roles[k] = v.replace("_", " ")
        if not roles.get("action"):
            continue
        line = g.line(roles, key=str(row.get("tags")))
        if not line.strip():
            raise ValueError("a row narrated to empty text")
        lines.append(line)
    if len(lines) < 3:
        raise ValueError("too few narratable rows")
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen3:8b")
    ap.add_argument("--voice", default="intern")
    ap.add_argument("idea", nargs="+")
    args = ap.parse_args()
    idea = " ".join(args.idea)
    grammar_file = f"data/grammars/{args.voice}.json"

    print(f'\n=== loomify · "{idea}" · {args.model} · voice={args.voice} ===\n')
    feedback = ""
    for attempt in (1, 2, 3):
        try:
            lines = loomify(idea, args.model, grammar_file, feedback)
            print(f"[compiled on attempt {attempt}]\n")
            for ln in lines:
                print("  " + ln)
            return
        except Exception as exc:
            feedback = f"Your previous output FAILED validation: {type(exc).__name__}: {exc}. Output STRICT JSON only."
            print(f"  (attempt {attempt} rejected: {type(exc).__name__}: {str(exc)[:70]})")
    print("\n  could not produce a running pipeline in 3 tries — honest failure, the validator held.")


if __name__ == "__main__":
    main()
