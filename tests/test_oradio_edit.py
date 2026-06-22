"""Edit .oradio: attaching a PNG thumbnail / MP3 soundtrack to a minted bundle (set_bundle_asset),
and the card/galaxy label using the mint Title (not the slug id)."""

from __future__ import annotations

import json
import types
import zipfile
from pathlib import Path

from bookmark.mint import read_manifest, set_bundle_asset
from ribbon_os_shell import RadioShell


def _make_oradio(path: Path) -> Path:
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("manifest.json", json.dumps({"id": "demo", "title": "Demo", "loop": "loop.mp4"}))
        z.writestr("loop.mp4", b"\x00\x00")
    return path


def test_set_bundle_asset_adds_file_and_manifest_key(tmp_path):
    o = _make_oradio(tmp_path / "demo.oradio")
    png = tmp_path / "t.png"; png.write_bytes(b"\x89PNG\r\nFAKE")
    set_bundle_asset(o, src=png, bundle_name="thumbnail.png", manifest_key="thumbnail")

    names = set(zipfile.ZipFile(o).namelist())
    assert "thumbnail.png" in names
    assert {"manifest.json", "loop.mp4"} <= names      # nothing else lost
    m = read_manifest(o)
    assert m["thumbnail"] == "thumbnail.png"
    assert m["title"] == "Demo"                         # untouched


def test_set_bundle_asset_replaces_in_place(tmp_path):
    o = _make_oradio(tmp_path / "demo.oradio")
    a = tmp_path / "a.png"; a.write_bytes(b"AAAA")
    b = tmp_path / "b.png"; b.write_bytes(b"BBBBBBBB")
    set_bundle_asset(o, src=a, bundle_name="thumbnail.png", manifest_key="thumbnail")
    set_bundle_asset(o, src=b, bundle_name="thumbnail.png", manifest_key="thumbnail")
    with zipfile.ZipFile(o) as zf:
        assert zf.read("thumbnail.png") == b"BBBBBBBB"
        assert zf.namelist().count("thumbnail.png") == 1   # not duplicated


def test_set_bundle_asset_removes(tmp_path):
    o = _make_oradio(tmp_path / "demo.oradio")
    mp3 = tmp_path / "a.mp3"; mp3.write_bytes(b"ID3")
    set_bundle_asset(o, src=mp3, bundle_name="audio.mp3", manifest_key="audio")
    assert read_manifest(o).get("audio") == "audio.mp3"
    set_bundle_asset(o, src=None, bundle_name="audio.mp3", manifest_key="audio")
    assert "audio.mp3" not in set(zipfile.ZipFile(o).namelist())
    assert "audio" not in read_manifest(o)


def _station(descriptor=None, name=None, sid="kernel"):
    return types.SimpleNamespace(
        station_id=sid,
        descriptor=descriptor,
        manifest=({"station": {"name": name}} if name else {}),
    )


def test_station_title_prefers_mint_title():
    st = _station(descriptor={"title": "Bookmark"}, name="kernel", sid="kernel")
    assert RadioShell._station_title(None, st) == "Bookmark"


def test_station_title_falls_back_to_name_then_id():
    assert RadioShell._station_title(None, _station(descriptor={}, name="iRacing", sid="iracing")) == "iRacing"
    assert RadioShell._station_title(None, _station(descriptor=None, name=None, sid="cyberpunk")) == "cyberpunk"
