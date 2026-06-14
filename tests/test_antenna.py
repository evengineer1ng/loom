"""The antenna — many tapes, toggle on/off, interleaved mix; heterogeneous events coexist."""

from __future__ import annotations

from oradio_engine.antenna import Antenna, Source
from oradio_engine.mix import LiveNarrator, Mixer
from oradio_engine.speech import Grammar

RACE = [{"action": "pit", "actor": "X", "priority": 0.9, "_key": "a1"},
        {"action": "clock", "actor": "X", "priority": 0.9, "_key": "a2"}]
NEWS = [{"title": "Breaking F1 news", "body": "Breaking F1 news", "priority": 0.9, "_key": "b1"}]


def test_stream_interleaves_enabled_sources_round_robin():
    ant = Antenna().add(Source("race", RACE)).add(Source("news", NEWS))
    s = ant.stream()
    assert [e["source"] for e in s] == ["race", "news", "race"]   # race0, news0, race1
    assert s[0]["action"] == "pit" and s[1]["title"] == "Breaking F1 news"


def test_toggle_drops_a_lane_live():
    ant = Antenna().add(Source("race", RACE)).add(Source("news", NEWS))
    ant.toggle("news", False)
    s = ant.stream()
    assert len(s) == 2 and all(e["source"] == "race" for e in s)


def test_heterogeneous_headline_speaks_verbatim():
    # a raw headline (no roles) rides the same stream as structured events, spoken verbatim
    G = Grammar({"form": "{actor} {verb}"}, {"pit": "pitted"})
    line = LiveNarrator(NEWS).step(G, Mixer(salience=0.5))
    assert line is not None and line[1] == "Breaking F1 news"
