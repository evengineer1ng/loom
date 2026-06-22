import json

from loom.app2 import _loom_dict, _relationship_edges
from oradio_engine.loom_graph import declaration_text, graph_nodes, load_declaration_text
from oradio_engine.loom_runtime import request_ribbonos_load


def test_loom_dict_preserves_universe_and_oradio_relationships():
    doc = _loom_dict(
        "my ribbon universe",
        [
            {"label": "Alpha", "oradio": "exports/alpha.oradio", "soulmate": "beta"},
            {"label": "Beta", "oradio": "exports/beta.oradio", "soulmate": "alpha"},
        ],
    )

    assert doc["universe"] == "my ribbon universe"
    assert doc["oradios"][0]["id"] == "alpha"
    assert doc["oradios"][0]["soulmate"] == "beta"
    assert doc["oradios"][1]["id"] == "beta"


def test_declaration_round_trip_loads_new_loom_shape():
    text = declaration_text(
        "constellation of moods",
        [
            {"id": "quiet-house", "label": "Quiet House", "oradio": "exports/quiet-house.oradio", "soulmate": "market-signal"},
            {"id": "market-signal", "label": "Market Signal", "oradio": "exports/market-signal.oradio", "soulmate": "quiet-house"},
        ],
    )

    universe, nodes = load_declaration_text(text)

    assert universe == "constellation of moods"
    assert nodes[0]["id"] == "quiet-house"
    assert nodes[0]["soulmate"] == "market-signal"
    assert nodes[1]["oradio"] == "exports/market-signal.oradio"


def test_declaration_round_trip_preserves_multi_soulmates():
    text = declaration_text(
        "constellation of moods",
        [
            {
                "id": "kernel",
                "label": "Kernel",
                "oradio": "exports/kernel.oradio",
                "soulmates": ["iracing", "stonehenge"],
            },
            {
                "id": "iracing",
                "label": "iRacing",
                "oradio": "exports/iracing.oradio",
                "soulmate": "kernel",
            },
        ],
    )

    universe, nodes = load_declaration_text(text)

    assert universe == "constellation of moods"
    assert nodes[0]["soulmate"] == "iracing"
    assert nodes[0]["soulmates"] == ["iracing", "stonehenge"]


def test_relationship_edges_are_unique_pairs():
    edges = _relationship_edges(
        [
            {"id": "kernel", "soulmates": ["iracing", "stonehenge"]},
            {"id": "iracing", "soulmates": ["kernel"]},
            {"id": "stonehenge", "soulmate": "kernel"},
        ]
    )

    assert edges == [("iracing", "kernel"), ("kernel", "stonehenge")]


def test_request_ribbonos_load_requests_specific_loom(tmp_path):
    target = tmp_path / "stonehenge.loom"

    request_ribbonos_load(tmp_path, target)

    payload = json.loads((tmp_path / ".switch_request").read_text(encoding="utf-8"))
    assert payload == {"action": "load_loom", "loom_path": str(target)}


def test_graph_nodes_positions_and_ids_are_deterministic():
    layout_a = graph_nodes(
        "same universe",
        [
            {"label": "Alpha", "oradio": "exports/alpha.oradio", "soulmate": "beta"},
            {"label": "Beta", "oradio": "exports/beta.oradio", "soulmate": "alpha"},
        ],
    )
    layout_b = graph_nodes(
        "same universe",
        [
            {"label": "Alpha", "oradio": "exports/alpha.oradio", "soulmate": "beta"},
            {"label": "Beta", "oradio": "exports/beta.oradio", "soulmate": "alpha"},
        ],
    )

    assert [node["id"] for node in layout_a] == ["alpha", "beta"]
    assert [(node["x"], node["y"]) for node in layout_a] == [(node["x"], node["y"]) for node in layout_b]
