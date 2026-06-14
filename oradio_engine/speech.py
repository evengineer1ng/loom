"""The speech kernel — deterministic, domain-agnostic data-to-text. No ML, no GPU.

This is the "rung 4 seed": it turns role-bearing rows into spoken English using a *metadata
lexicon* (words defined by structure — register pools, tense — not prose) plus grammatical
realization (articles, number-to-words, light cohesion). The SAME code speaks any domain;
the domain lives entirely in the rows + the lexicon, never here. Swap the lexicon and the
role-tags and basketball becomes biometrics-as-poetry with zero code change — that is the
whole proof.

Roles ride on a candidate's ``tags`` as ``"key:value"`` (actor/action/object/magnitude/
unit/valence/pronoun/definite), so the frozen NormalizedCandidate contract is untouched.

Pure stdlib (json/hashlib) — imported lazily by the ``tape_to_speech`` transform so
``import oradio_engine`` stays stdlib+PyYAML.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional, Sequence

ROLE_KEYS = ("actor", "action", "object", "magnitude", "unit", "valence", "pronoun", "definite")

_ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
         "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
         "seventeen", "eighteen", "nineteen"]
_TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

# Deterministic color, keyed by valence — the "vibe" without a model. Each carries its own
# leading punctuation so it appends cleanly. Chosen per-row by hashing, so it varies yet repeats.
VALENCE_CODA: Dict[str, List[str]] = {
    "hype": [" — count it!", ", and the place erupts.", " — are you kidding?"],
    "alarm": [", and the room tightens.", " — something shifts."],
    "calm": [", easy as breathing.", ", like nothing at all."],
    "grit": [", the hard way.", ", no give in it."],
}
TRANSITIONS = ["", "", "", "Then, ", "Moments later, ", "Now, ", "And just like that, "]


def number_to_words(n: int) -> str:
    n = int(n)
    if n < 0:
        return "minus " + number_to_words(-n)
    if n < 20:
        return _ONES[n]
    if n < 100:
        rest = n % 10
        return _TENS[n // 10] + ("-" + _ONES[rest] if rest else "")
    if n < 1000:
        rest = n % 100
        return _ONES[n // 100] + " hundred" + (" " + number_to_words(rest) if rest else "")
    rest = n % 1000
    return number_to_words(n // 1000) + " thousand" + (" " + number_to_words(rest) if rest else "")


def article(word: str) -> str:
    return "an" if word[:1].lower() in "aeiou" else "a"


def regular_past(verb: str) -> str:
    """Graceful default tense for any verb the lexicon doesn't cover — regular English past.
    (Irregulars are handled by a lexicon ``past``; this is the floor, not the whole grammar.)"""
    v = (verb or "").strip()
    if not v:
        return v
    if v.endswith("e"):
        return v + "d"
    if len(v) > 2 and v[-1] == "y" and v[-2] not in "aeiou":
        return v[:-1] + "ied"
    return v + "ed"


def _pick(pool: Sequence[str], *key: Any) -> str:
    """Deterministic choice from a pool: same key -> same pick (variety that replays exactly)."""
    if not pool:
        return ""
    h = int(hashlib.sha256(":".join(str(k) for k in key).encode("utf-8")).hexdigest()[:8], 16)
    return pool[h % len(pool)]


def roles_from_tags(tags: Sequence[str]) -> Dict[str, str]:
    """Extract role:value pairs from a candidate's tags (the contract-safe role channel)."""
    roles: Dict[str, str] = {}
    for tag in tags or ():
        if isinstance(tag, str) and ":" in tag:
            key, value = tag.split(":", 1)
            if key in ROLE_KEYS:
                roles[key] = value.replace("_", " ")
    return roles


class SpeechGrammar:
    """Realizes role rows into spoken lines under a register (plain/hype/poetic…) and mode."""

    def __init__(self, lexicon: Dict[str, Any], *, register: str = "plain", mode: str = "radio") -> None:
        self.lex = lexicon or {}
        self.register = register
        self.mode = mode

    @classmethod
    def from_file(cls, path: str, **kw: Any) -> "SpeechGrammar":
        with open(path, "r", encoding="utf-8") as f:
            return cls(json.load(f), **kw)

    def _verb(self, action: str, key: Any) -> str:
        entry = self.lex.get(action, {})
        registers = entry.get("register", {}) if isinstance(entry, dict) else {}
        pool = registers.get(self.register) or registers.get("plain") or [entry.get("past") or regular_past(action)]
        return _pick(pool, action, self.register, key)

    def line(self, roles: Dict[str, str], *, prev_roles: Optional[Dict[str, str]] = None,
             position: int = 0, key: Any = 0) -> str:
        """Render one role row to a sentence. Returns '' when there is nothing to say."""
        action = roles.get("action")
        if not action:
            return ""

        actor = roles.get("actor", "")
        # light cohesion: same actor as the previous line -> use the pronoun (don't re-name them)
        subject = actor
        if prev_roles and actor and prev_roles.get("actor") == actor and position > 0 and roles.get("pronoun"):
            subject = roles["pronoun"]

        clause = f"{subject} {self._verb(action, key)}".strip()

        obj = roles.get("object")
        if obj:
            if roles.get("definite") == "1":
                clause += f" the {obj}"
            elif obj[:1].isupper():        # proper noun (a name) takes no article
                clause += f" {obj}"
            else:
                clause += f" {article(obj)} {obj}"

        magnitude = roles.get("magnitude")
        if magnitude:
            unit = roles.get("unit", "")
            number = number_to_words(int(magnitude)) if magnitude.isdigit() else magnitude
            clause += f" to {number}{(' ' + unit) if unit else ''}"

        transition = _pick(TRANSITIONS, "trans", self.mode, key, position) if position > 0 else ""
        coda = _pick(VALENCE_CODA.get(roles.get("valence", ""), [""]), "coda", key)

        text = f"{transition}{clause}{coda}".strip()
        if text:
            text = text[0].upper() + text[1:]
        if text and not text.endswith((".", "!", "?")):
            text += "."
        return text

    def narrate(self, role_seq: Sequence[Dict[str, str]]) -> List[str]:
        """Speak a whole tape with cohesion across rows."""
        out: List[str] = []
        prev: Optional[Dict[str, str]] = None
        for i, roles in enumerate(role_seq):
            line = self.line(roles, prev_roles=prev, position=i, key=roles.get("_key", i))
            if line:
                out.append(line)
                prev = roles
        return out
