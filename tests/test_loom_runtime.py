import json
import zipfile
from pathlib import Path

from oradio_engine.loom_runtime import (
    discover_all_looms,
    load_edge_textures,
    read_active_loom_state,
    request_ribbonos_load,
    resolve_active_loom,
    set_edge_texture,
    upsert_oradio_into_loom,
    write_active_loom_state,
)


def test_active_loom_state_round_trip(tmp_path: Path):
    loom = tmp_path / "stonehenge.loom"
    loom.write_text("universe: stonehenge\noradios: []\n", encoding="utf-8")

    write_active_loom_state(tmp_path, loom)

    assert read_active_loom_state(tmp_path)["loom_path"] == str(loom.resolve())
    assert resolve_active_loom(tmp_path) == loom


def test_request_ribbonos_load_writes_switch_request(tmp_path: Path):
    loom = tmp_path / "stonehenge.loom"
    request_ribbonos_load(tmp_path, loom)

    payload = json.loads((tmp_path / ".switch_request").read_text(encoding="utf-8"))
    assert payload == {"action": "load_loom", "loom_path": str(loom)}


def test_upsert_oradio_into_loom_adds_node_and_relationship(tmp_path: Path):
    loom = tmp_path / "stonehenge.loom"
    loom.write_text(
        "universe: stonehenge\n"
        "oradios:\n"
        "  - id: kernel\n"
        "    label: Kernel\n"
        "    oradio: exports/kernel.oradio\n",
        encoding="utf-8",
    )
    oradio = tmp_path / "iRacing.oradio"
    with zipfile.ZipFile(oradio, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", '{"id":"iRacing","title":"iRacing UI","duration_s":3.0}')

    result = upsert_oradio_into_loom(loom, oradio, soulmate_ids=["kernel"])

    assert result["node_id"] == "iracing"
    text = loom.read_text(encoding="utf-8")
    assert "id: iracing" in text
    assert "soulmate: kernel" in text


def test_discover_all_looms_dedupes_same_universe(tmp_path: Path):
    (tmp_path / "a.loom").write_text("universe: stonehenge\noradios: []\n", encoding="utf-8")
    (tmp_path / "b.loom").write_text("universe: stonehenge\noradios: []\n", encoding="utf-8")

    looms = discover_all_looms(tmp_path)

    assert len(looms) == 1


def test_edge_texture_round_trip(tmp_path: Path):
    textures = set_edge_texture(tmp_path, "stonehenge", "kernel", "iracing", "C:/textures/red-string.png")
    assert textures["iracing__kernel"] == "C:/textures/red-string.png"
    assert load_edge_textures(tmp_path, "stonehenge")["iracing__kernel"] == "C:/textures/red-string.png"

    textures = set_edge_texture(tmp_path, "stonehenge", "kernel", "iracing", None)
    assert "iracing__kernel" not in textures
