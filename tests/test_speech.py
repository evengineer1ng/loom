"""The deterministic speech kernel — domain-agnostic, no ML, repeatable."""

from __future__ import annotations

from oradio_engine.binding import build_transform
from oradio_engine.contract import NormalizedCandidate
from oradio_engine.speech import SpeechGrammar, number_to_words, roles_from_tags

LEX = {
    "make": {"past": "made", "register": {"plain": ["made"], "hype": ["drilled", "buried"]}},
    "rise": {"past": "rose", "register": {"plain": ["rose"], "poetic": ["lifted like a tide"]}},
    "rebound": {"past": "rebounded", "register": {"plain": ["grabbed"]}},
}


def test_number_to_words():
    assert number_to_words(3) == "three"
    assert number_to_words(72) == "seventy-two"
    assert number_to_words(118) == "one hundred eighteen"


def test_roles_from_tags_is_contract_safe_channel():
    tags = ["nba", "actor:Towns", "action:make", "object:three", "valence:hype", "junk"]
    roles = roles_from_tags(tags)
    assert roles == {"actor": "Towns", "action": "make", "object": "three", "valence": "hype"}


def test_same_code_speaks_two_domains():
    g = SpeechGrammar(LEX, register="plain")
    hoops = g.line({"action": "make", "actor": "Towns", "object": "three"}, key="b1")
    bio = g.line({"action": "rise", "actor": "your heart", "magnitude": "118", "unit": "bpm"}, key="r1")
    assert hoops == "Towns made a three."
    assert bio == "Your heart rose to one hundred eighteen bpm."  # zero domain code between them


def test_register_changes_word_choice():
    plain = SpeechGrammar(LEX, register="plain").line({"action": "make", "actor": "Towns", "object": "three"}, key="k")
    hype = SpeechGrammar(LEX, register="hype").line({"action": "make", "actor": "Towns", "object": "three"}, key="k")
    assert plain != hype
    assert any(w in hype for w in ("drilled", "buried"))


def test_deterministic_replay():
    g = SpeechGrammar(LEX, register="hype")
    rows = [{"action": "make", "actor": "Towns", "object": "three", "_key": "x"},
            {"action": "make", "actor": "Towns", "object": "layup", "_key": "y"}]
    assert g.narrate(rows) == g.narrate(rows)  # byte-identical, no RNG drift


def test_cohesion_uses_pronoun_for_repeated_actor():
    g = SpeechGrammar(LEX, register="plain")
    rows = [
        {"action": "make", "actor": "Wembanyama", "object": "jumper", "pronoun": "he", "_key": "1"},
        {"action": "rebound", "actor": "Wembanyama", "object": "board", "pronoun": "he", "_key": "2"},
    ]
    lines = g.narrate(rows)
    assert lines[0].startswith("Wembanyama")
    assert "He " in lines[1] and "Wembanyama" not in lines[1]  # second line pronominalizes


def test_registered_transform_reads_roles_from_candidate_tags():
    t = build_transform("tape_to_speech", register="plain")  # no lexicon -> falls back to lemma
    c = NormalizedCandidate(post_id="p1", source="court", title="t", body="b", priority=0.5,
                            ts=1.0, type="play", tags=("actor:Towns", "action:rebound", "object:board"))
    out = t(c)
    assert out is not None and out["text"] == "Towns rebounded a board."
    # a row with no action role produces nothing to say
    assert t(NormalizedCandidate("p2", "court", "t", "b", 0.5, 1.0, "play", ("nba",))) is None
