"""Tests for the shared open-resolver (bookmark/launch.py::resolve_open_plan).

This is the single source of truth for "what does an oradio open to", used by BOTH the file-manager
double-click (oradio_player.py) and the RibbonOS carousel/galaxy (ribbon_os_shell.py). The ladder:
shortcut -> html -> brick-app (registry-resolved, else loop) -> descriptor -> loop.
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

from bookmark.launch import resolve_open_plan


def _make_oradio(path: Path, manifest: dict) -> Path:
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("manifest.json", json.dumps(manifest))
        z.writestr("loop.mp4", b"\x00\x00")
    return path


def _make_brick(root: Path, brick_id: str, *, lang: str = "python") -> Path:
    d = root / "pkg"
    d.mkdir(parents=True, exist_ok=True)
    asset = d / "app.py"
    asset.write_text("print('hi')", encoding="utf-8")
    (d / "b.concept.json").write_text(json.dumps({
        "api_version": "loom.concept.v1", "id": brick_id, "kind": "app", "lang": lang,
        "asset": "app.py", "version": "0.1.0", "deterministic": False,
        "inputs": [], "outputs": [], "requires": [], "provides": [], "side_effects": [],
        "ui_slots": [], "tags": [], "description": "a test brick",
    }), encoding="utf-8")
    return asset


def test_brick_app_resolves_to_asset(tmp_path):
    bricks = tmp_path / "bricks"
    asset = _make_brick(bricks, "demo.app")
    o = _make_oradio(tmp_path / "k.oradio", {"id": "k", "bricks": ["demo.app"], "open": None,
                                             "kernel": True, "loop": "loop.mp4"})
    plan = resolve_open_plan(o, bricks_root=bricks)
    assert plan["mode"] == "app"
    assert Path(plan["asset"]) == asset
    assert plan["lang"] == "python"
    assert plan["is_kernel"] is True


def test_unresolved_brick_degrades_to_loop(tmp_path):
    bricks = tmp_path / "bricks"
    bricks.mkdir()
    o = _make_oradio(tmp_path / "x.oradio", {"id": "x", "bricks": ["nope.nothere"], "loop": "loop.mp4"})
    plan = resolve_open_plan(o, bricks_root=bricks)
    assert plan["mode"] == "loop"
    assert plan["unresolved_brick"] == "nope.nothere"
    assert plan["loop"] == "loop.mp4"


def test_shortcut_wins(tmp_path):
    o = _make_oradio(tmp_path / "s.oradio", {
        "id": "s", "bricks": ["demo.app"],   # bricks present but shortcut takes priority
        "open": {"kind": "shortcut", "target": "steam://rungameid/440", "launch": "auto"}})
    plan = resolve_open_plan(o, bricks_root=tmp_path / "bricks")
    assert plan["mode"] == "shortcut"
    assert plan["target"] == "steam://rungameid/440"


def test_html_open(tmp_path):
    o = _make_oradio(tmp_path / "h.oradio", {
        "id": "h", "open": {"kind": "html", "asset": "page.html"}})
    plan = resolve_open_plan(o, bricks_root=tmp_path / "bricks")
    assert plan["mode"] == "html"
    assert plan["open"]["kind"] == "html"


def test_pure_loop(tmp_path):
    o = _make_oradio(tmp_path / "l.oradio", {"id": "l", "open": None, "loop": "loop.mp4"})
    plan = resolve_open_plan(o, bricks_root=tmp_path / "bricks")
    assert plan["mode"] == "loop"
    assert "unresolved_brick" not in plan


def test_descriptor_non_zip(tmp_path):
    p = tmp_path / "d.oradio"
    p.write_text("universe: demo\noradios: []\n", encoding="utf-8")
    plan = resolve_open_plan(p)
    assert plan["mode"] == "descriptor"


def test_real_kernel_oradio_opens_to_bookmark():
    """The shipped kernel.oradio resolves to running bookmark.py (the authoring kernel)."""
    repo = Path(__file__).resolve().parent.parent
    kernel = repo / "exports" / "kernel.oradio"
    if not kernel.exists():
        return  # not all checkouts carry the minted kernel
    plan = resolve_open_plan(kernel)
    assert plan["mode"] == "app"
    assert Path(plan["asset"]).name == "bookmark.py"
    assert plan["is_kernel"] is True
