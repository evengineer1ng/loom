"""Colorist — a guarded LLM colorist. The mirror line is already fact-true; a local model is asked
ONLY to add flair; a faithfulness guard rejects any output that introduces an unsupported specific
(a new person, score, car/lap number, turn, position, team, or wrong sport) and falls back to the
mirror line. So the colored output can never be less faithful than the mirror — worst case it IS
the mirror.

Endpoint module (calls a local LLM via urllib) — deliberately NOT imported by oradio_engine, so
the decoder stays stdlib+PyYAML pure.
"""
from __future__ import annotations

import json
import re
import urllib.request
from typing import Callable, Iterable, Optional

OLLAMA = "http://127.0.0.1:11434/api/generate"
TEAMS = ["mercedes", "ferrari", "red bull", "mclaren", "aston martin", "racing point",
         "alpine", "williams", "haas", "alphatauri", "sauber", "racing bulls"]
WRONG_SPORT = ["soccer", "nba", "nascar", "basketball", "football", "hockey", "baseball", "tennis"]
WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def introduces_unsupported(colored: str, original: str, entities: Iterable[str]) -> bool:
    """True if `colored` adds a specific that `original` did not license."""
    if not colored:
        return True
    low, olow = colored.lower(), original.lower()
    ents = list(entities)
    allowed = {e for e in ents if e.lower() in olow}
    if any(e.lower() not in low for e in allowed):
        return True                                            # dropped/swapped an original name
    if any(e.lower() in low for e in ents if e not in allowed):
        return True                                            # named someone not in the line
    return bool(
        any(w in low for w in WEEKDAYS)                        # invented a day
        or re.search(r"\b\d+\s*[-–]\s*\d+\b", colored)    # invented score "4-2"
        or re.search(r"#\d+", colored)                          # car number "#15"
        or re.search(r"\b\d+\s*(minute|minutes|second|seconds|goal|goals|point|points|lap|laps)\b", low)
        or re.search(r"\bturn \d+", low)
        or re.search(r"\b(p\d|first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\s+(place|position)\b", low)
        or any(t in low for t in TEAMS)
        or any(w in low for w in WRONG_SPORT)
    )


class Colorist:
    def __init__(self, model: str) -> None:
        self.model = model

    def _generate(self, prompt: str) -> str:
        body = {"model": self.model, "prompt": prompt, "stream": False, "think": False,
                "options": {"temperature": 0.6, "num_predict": 40}}
        req = urllib.request.Request(OLLAMA, data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        resp = json.load(urllib.request.urlopen(req, timeout=60))
        return re.sub(r"(?is)<think>.*?</think>", "", resp.get("response") or "").strip()

    def colorize(self, line: str, entities: Iterable[str], *, gen: Optional[Callable[[str], str]] = None) -> str:
        """Return a flaired version of `line`, or `line` unchanged if the model hallucinates."""
        gen = gen or self._generate
        prompt = ("Rewrite this race update with vivid flair. Keep the SAME facts and names. Do NOT "
                  "add positions, lap or car numbers, scores, teams, other sports, or other people. "
                  "One sentence.\nUpdate: " + line)
        try:
            out = gen(prompt).strip().strip('"').strip()
        except Exception:
            return line
        return line if introduces_unsupported(out, line, entities) else out
