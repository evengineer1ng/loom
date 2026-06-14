"""Inquiry — expectations generate questions; the curiosity dial governs how many."""

from __future__ import annotations

from oradio_engine.inquiry import ask, anomalous_repeat, investigate, violation_without_cause
from oradio_engine.speech import Grammar

G = Grammar({"form": "{actor} {verb}{object}{magnitude}{coda}", "codas": {"*": [""]}},
            {"pit": "pitted", "clock": "clocked"})

DOUBLE_PIT = [
    {"actor": "Lindblad", "action": "pit", "lap": "29", "_key": "1"},
    {"actor": "Verstappen", "action": "pit", "lap": "30", "_key": "2"},
    {"actor": "Lindblad", "action": "pit", "lap": "31", "_key": "3"},   # 2 laps after his last -> anomaly
]


def test_anomalous_repeat_fires_on_quick_double():
    qs = anomalous_repeat(DOUBLE_PIT, action="pit", within=4)
    assert len(qs) == 1 and qs[0].about == 2
    assert "Lindblad" in qs[0].text and "again" in qs[0].text


def test_anomalous_repeat_silent_when_spaced_out():
    spaced = [{"actor": "X", "action": "pit", "lap": "10", "_key": "1"},
              {"actor": "X", "action": "pit", "lap": "40", "_key": "2"}]
    assert anomalous_repeat(spaced, action="pit", within=4) == []


def test_violation_without_cause():
    no_pit = [{"actor": "X", "action": "clock", "object": "fastest lap", "lap": "12", "_key": "1"}]
    assert len(violation_without_cause(no_pit, effect="clock", cause="pit")) == 1
    with_pit = [{"actor": "X", "action": "pit", "lap": "10", "_key": "0"},
                {"actor": "X", "action": "clock", "object": "fastest lap", "lap": "12", "_key": "1"}]
    assert violation_without_cause(with_pit, effect="clock", cause="pit") == []


def test_curiosity_dial_more_expectations_more_questions():
    few = ask(DOUBLE_PIT, curiosity=["double_pit"])
    many = ask(DOUBLE_PIT, curiosity=["double_pit", "unexplained_pace", "double_fastest"])
    assert len(many) >= len(few) >= 1


def test_investigate_pairs_question_with_traced_thread():
    qs = ask(DOUBLE_PIT, curiosity=["double_pit"])
    answered = investigate(DOUBLE_PIT, G, qs, depth=2)
    assert len(answered) == 1
    question, thread = answered[0]
    assert question.endswith("?")
    assert "Lindblad" in thread     # the thread is about the questioned event
