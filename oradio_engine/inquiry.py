"""Inquiry — the tape asks questions about itself. The genome of threads.

A QUESTION is born where reality deviates from an EXPECTATION (an assumption). You can't ask
without an expectation, and challenging it = pulling the thread to check the tape. More active
expectations -> more deviations noticed -> more questions -> more threads. That set of active
expectations is the CURIOSITY DIAL — the birth-genome that generates seeds, sitting *above* the
thread-puller (a question is a seed with a reason to exist).

Deterministic: expectations are anomaly/violation TEMPLATES over the event tape — kin to the
engine's EvidenceService, where a prediction is an assumption the tape later grades. Templated
questions are free and repeatable; a genuinely novel "huh, that's weird" is authored by an LLM at
compile time (a new template), runtime stays pure. Pure stdlib.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from oradio_engine.speech import Grammar
from oradio_engine.thread import build_edges, weave

Event = Dict[str, Any]


def _lap(e: Event) -> Optional[int]:
    try:
        return int(e.get("lap"))
    except (TypeError, ValueError):
        return None


@dataclass
class Question:
    about: int          # the event index the question concerns (a thread seed)
    kind: str
    text: str
    salience: float = 0.9


# --- expectation / anomaly templates (each: events -> [Question]) --------------------------- #
def anomalous_repeat(events: Sequence[Event], *, action: str, within: int = 4) -> List[Question]:
    """Expectation: an actor doesn't repeat ACTION within `within` laps. Deviation -> question.
    (This is the one you spotted: the suspicious double-pit.)"""
    out: List[Question] = []
    last: Dict[str, Optional[int]] = {}
    for i, e in enumerate(events):
        if e.get("action") != action:
            continue
        actor, lap = e.get("actor"), _lap(e)
        prev = last.get(actor)
        if prev is not None and lap is not None and lap - prev <= within:
            gap = lap - prev
            out.append(Question(about=i, kind="repeat",
                                text=f"Why did {actor} {action} again only {gap} lap{'s' if gap != 1 else ''} after the last?"))
        last[actor] = lap if lap is not None else prev
    return out


def violation_without_cause(events: Sequence[Event], *, effect: str, cause: str, within: int = 6) -> List[Question]:
    """Expectation: EFFECT follows a recent same-actor CAUSE (fast lap <- fresh tyres). Deviation:
    the effect with no preceding cause -> question (where did it come from?)."""
    out: List[Question] = []
    for i, e in enumerate(events):
        if e.get("action") != effect:
            continue
        actor, lap = e.get("actor"), _lap(e)
        has_cause = any(
            c.get("action") == cause and c.get("actor") == actor and _lap(c) is not None
            and lap is not None and 0 <= lap - _lap(c) <= within
            for c in events[:i]
        )
        if not has_cause:
            out.append(Question(about=i, kind="uncaused",
                                text=f"How did {actor} manage the {effect} with no recent {cause}?"))
    return out


# The dial: each entry is one expectation. Turning more on = more questions = more threads.
QUESTION_BANK: Dict[str, Callable[[Sequence[Event]], List[Question]]] = {
    "double_pit": lambda ev: anomalous_repeat(ev, action="pit", within=4),
    "double_fastest": lambda ev: anomalous_repeat(ev, action="clock", within=3),
    "unexplained_pace": lambda ev: violation_without_cause(ev, effect="clock", cause="pit"),
}


def ask(events: Sequence[Event], *, curiosity: Optional[List[str]] = None) -> List[Question]:
    """Run the active expectations. ``curiosity`` IS the dial — the list of active question kinds;
    more active expectations notice more deviations. None = maximally curious (all)."""
    active = curiosity if curiosity is not None else list(QUESTION_BANK)
    out: List[Question] = []
    for kind in active:
        fn = QUESTION_BANK.get(kind)
        if fn:
            out.extend(fn(events))
    out.sort(key=lambda q: q.about)
    return out


def investigate(events: Sequence[Event], grammar: Grammar, questions: Sequence[Question], *,
                depth: int = 2, rules: Optional[List[Dict[str, Any]]] = None) -> List[Tuple[str, str]]:
    """Pull the thread around each question to (try to) answer it: (question, traced context).
    If the thread holds no cause, the question stands unanswered — which fingers the detector."""
    cause, effect = build_edges(events, rules)
    return [(q.text, weave(events, q.about, grammar, depth=depth, cause=cause, effect=effect))
            for q in questions]
