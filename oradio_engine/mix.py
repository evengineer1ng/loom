"""The Mixer — the faders you ride over one deterministic pipeline.

Every knob we built, in one object you can read fresh on a running tick:

  - depth      : flavour — how FAR you pull each thread
  - flavour    : DIRECTION of the pull (back=causes / forward=consequences / both)
  - curiosity  : how many expectations fire -> how many questions get born (0 = none)
  - salience   : what's worth narrating (min_priority)
  - continuity : whether carried state is woven in ("for the second time")
  - voice      : the grammar (how it speaks)

A MIX is itself a tape: record (tick -> Mixer) as an automation lane and the performance replays
byte-for-byte — but like a cassette, you keep as much as YOU want (punch in the takes you like).
That's the DJ booth: live to perform, deterministic to keep. Pure stdlib.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

from oradio_engine.speech import Grammar
from oradio_engine.thread import build_edges, narrate_salient, pull, weave

Event = Dict[str, Any]


@dataclass
class Mixer:
    depth: int = 2
    flavour: str = "both"        # back | forward | both
    curiosity: int = 0           # 0 = no questions; higher = deeper expectations active
    salience: float = 0.7        # min_priority to narrate
    continuity: bool = True
    voice: str = "intern"        # which grammar speaks (a pedal: live-swappable)

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LiveNarrator:
    """Streams a (replay) tape one salient event at a time, narrating each through the mixer's
    CURRENT settings — so faders ride live. Pure (no UI), so the booth's brain is testable."""

    def __init__(self, events: Sequence[Event], *, rules: Optional[List[Dict[str, Any]]] = None) -> None:
        self.events = events
        self.cause, self.effect = build_edges(events, rules)
        self.i = 0
        self.consumed: set = set()

    @property
    def done(self) -> bool:
        return self.i >= len(self.events)

    def step(self, grammar: Grammar, mixer: "Mixer") -> Optional[Tuple[Any, str]]:
        """Advance to the next salient, unconsumed event and narrate it. Returns (lap, line),
        or None for this beat (silent thread-material, filtered out, or end of tape)."""
        while self.i < len(self.events):
            idx = self.i
            self.i += 1
            e = self.events[idx]
            if idx in self.consumed or float(e.get("priority", 0)) < mixer.salience:
                continue
            line = weave(self.events, idx, grammar, depth=mixer.depth, flavour=mixer.flavour,
                         continuity=mixer.continuity, cause=self.cause, effect=self.effect)
            causes, fwds = pull(self.cause, self.effect, idx, mixer.depth, flavour=mixer.flavour)
            self.consumed.add(idx)
            for j, _ in causes:
                self.consumed.add(j)
            for k, _ in fwds:
                self.consumed.add(k)
            return e.get("lap"), line
        return None


def render(events: Sequence[Event], grammar: Grammar, mixer: Mixer, *,
           rules: Optional[List[Dict[str, Any]]] = None, inquiry: Any = None
           ) -> Tuple[List[Tuple[Any, str]], List[Tuple[str, str]]]:
    """One render of a tape through the mixer's current settings -> (stories, questions)."""
    stories = narrate_salient(events, grammar, depth=mixer.depth, rules=rules,
                              min_priority=mixer.salience, flavour=mixer.flavour,
                              continuity=mixer.continuity)
    questions: List[Tuple[str, str]] = []
    if mixer.curiosity and inquiry is not None:
        from oradio_engine.inquiry import investigate
        qs = inquiry.ask(events, curiosity=mixer.curiosity)
        questions = investigate(events, grammar, qs, depth=mixer.depth, rules=rules)
    return stories, questions
