"""Tests for loom-switching discovery + active-loom keying (ribbon_os_shell).

Covers the pure pieces of the "Go to loom ▸" right-click swap: enumerating looms, building the
carousel from a SPECIFIC loom, and resolving a loom's door/crossover key (incl. the legacy
'default' migration). The Tk-driven orchestration (_switch_to_loom) is not exercised here.
"""

from __future__ import annotations

import types
import zipfile
from pathlib import Path

import ribbon_os_shell as r
from ribbon_os_shell import RadioShell, DEFAULT_LOOM_ID, GalaxyMap


def test_discover_all_looms_unique_ids_and_readable_labels():
    looms = r._discover_all_looms()
    assert looms, "expected at least one .loom on disk"
    ids = [lid for _p, lid, _lbl in looms]
    assert len(ids) == len(set(ids)), "loom_ids must be de-duped (one menu entry per universe)"
    # the label is the file stem (the universe can be a long descriptive sentence)
    for path, _lid, label in looms:
        assert label == path.stem
    # stonehenge is the genesis loom and uses a clean universe id
    assert any(lid == "stonehenge" for _p, lid, _lbl in looms)


def test_load_items_for_is_loom_specific():
    looms = r._discover_all_looms()
    by_id = {lid: p for p, lid, _lbl in looms}
    # the primary loom should always resolve at least one item; another loom should remain distinct
    prim = r.load_oradio_shell_items_for(r._discover_primary_loom())
    assert prim
    other_id = next((lid for lid in by_id if lid != "stonehenge"), None)
    if other_id is not None:
        other = r.load_oradio_shell_items_for(by_id[other_id])
        assert other, "a non-primary loom should still resolve its oradios"
        assert isinstance(other, list)


def test_load_items_for_none_falls_back_to_standalone():
    # None loom_path -> standalone .oradio discovery (never raises, may be empty)
    items = r.load_oradio_shell_items_for(None)
    assert isinstance(items, list)


def test_loom_id_for():
    # no loom on disk -> the legacy default key
    assert RadioShell._loom_id_for(None, None) == DEFAULT_LOOM_ID
    # a real loom resolves to its universe id
    prim = r._discover_primary_loom()
    universe, _nodes = r.load_declaration_text(prim.read_text(encoding="utf-8"))
    assert RadioShell._loom_id_for(None, prim) == (universe or prim.stem)


def test_loom_id_for_stem_fallback(tmp_path: Path):
    # a .loom whose declaration has no universe falls back to the file stem
    f = tmp_path / "lonely.loom"
    f.write_text("oradios: []\n", encoding="utf-8")
    assert RadioShell._loom_id_for(None, f) == "lonely"


def test_door_loom_id_legacy_migration():
    """A loom with no door of its own inherits the legacy 'default' set IFF it is the active
    loom and that set exists on disk; other looms keep their own key."""
    from bookmark import door
    class _Fake:
        _active_loom_id = "stonehenge"
    fake = _Fake()
    idx = door._load_index(r.CLUB_DIR)
    legacy_exists = (Path(r.CLUB_DIR) / "doors" / DEFAULT_LOOM_ID).is_dir()
    got = RadioShell._door_loom_id(fake, "stonehenge")
    if "stonehenge" in idx:                       # the loom has its own door -> use it
        assert got == "stonehenge"
    else:                                          # else inherit the legacy 'default' set if present
        assert got == (DEFAULT_LOOM_ID if legacy_exists else "stonehenge")
    # a non-active loom never claims the legacy default
    assert RadioShell._door_loom_id(fake, "basketball") == "basketball"


def test_load_items_for_preserves_multi_soulmates(tmp_path: Path):
    oradio = tmp_path / "kernel.oradio"
    with zipfile.ZipFile(oradio, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", '{"id":"kernel","title":"Kernel","duration_s":3.0}')
    loom = tmp_path / "stonehenge.loom"
    loom.write_text(
        "universe: stonehenge\n"
        "oradios:\n"
        "  - id: kernel\n"
        "    label: kernel\n"
        "    oradio: kernel.oradio\n"
        "    soulmates: [iracing, paddock]\n",
        encoding="utf-8",
    )

    items = r.load_oradio_shell_items_for(loom)

    assert items[0].soulmate == "iracing"
    assert items[0].soulmates == ["iracing", "paddock"]


def test_refresh_stations_uses_active_loom(monkeypatch):
    shell = RadioShell.__new__(RadioShell)
    shell._active_loom_path = Path("active.loom")
    shell._nav_mode = "galaxy"
    shell.galaxy = types.SimpleNamespace(set_nodes=lambda nodes: setattr(shell, "_galaxy_nodes", list(nodes)))
    shell.home_tiles = [{"station": types.SimpleNamespace(station_id="kernel")}]
    shell.selected_idx = 0
    shell.root = types.SimpleNamespace(after=lambda _ms, fn: fn())
    shell._render_cards = lambda: None
    shell._highlight_selected = lambda: None
    shell._focused_station = lambda: types.SimpleNamespace(station_id="kernel")
    shell._focus_station_ribbon = lambda _station: None
    shell._relayout = lambda _idx, animate=False: None
    shell._current_oradio_id = "kernel"

    called = {"loom": None}

    def fake_load_for(path):
        called["loom"] = path
        return [types.SimpleNamespace(station_id="kernel")]

    monkeypatch.setattr(r, "load_oradio_shell_items_for", fake_load_for)

    shell.refresh_stations()

    assert called["loom"] == Path("active.loom")
    assert shell.stations[0].station_id == "kernel"


def test_galaxy_edge_hit_test():
    g = GalaxyMap()
    g.edges = [(0, 1)]
    g._proj = [(100.0, 100.0, 1.0), (200.0, 100.0, 1.0)]

    assert g.hit_test_edge(150, 105) == (0, 1)
    assert g.hit_test_edge(150, 140) is None
