"""Tests for the visual-signature transition engine (bookmark/transitions.py).

The ladder-SELECTION logic is pure and tested without ffmpeg. The OPERATOR/bridge integration
is gated behind ffmpeg availability (skipped if ffmpeg isn't on PATH / known dirs).
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from bookmark import transitions as T
from bookmark.mint import MintError, _tool


# ---------------------------------------------------------------------------
# pure: signature + ladder selection (no ffmpeg)
# ---------------------------------------------------------------------------

def _sig(tmp_path, oid, family="ribbon", with_anchors=True, palette=None):
    entry = exit_ = ""
    if with_anchors:
        e = tmp_path / f"{oid}.entry.png"
        x = tmp_path / f"{oid}.exit.png"
        e.write_bytes(b"\x89PNG\r\n")   # presence is all has_anchors() checks
        x.write_bytes(b"\x89PNG\r\n")
        entry, exit_ = str(e), str(x)
    return T.VisualSignature(
        oradio_id=oid, family=family, palette=palette or ["#112233"],
        entry_anchor=entry, exit_anchor=exit_,
    )


def test_signature_roundtrip():
    s = T.VisualSignature(oradio_id="a", family="smoke", palette=["#ff0000", "#00ff00"],
                          motion_vector="clockwise", density=0.7, texture="glass")
    s2 = T.VisualSignature.from_dict(s.to_dict())
    assert s2.oradio_id == "a" and s2.family == "smoke"
    assert s2.palette == ["#ff0000", "#00ff00"]
    assert s2.motion_vector == "clockwise" and s2.density == 0.7


def test_blend_hex_midpoint():
    assert T.blend_hex("#000000", "#ffffff", 0.5) == "#808080"
    assert T.blend_hex("#ff0000", "#0000ff", 0.5) == "#800080"
    assert T.blend_hex("#123456", "#123456", 0.5) == "#123456"


def test_ladder_same_family_offers_morph_first(tmp_path):
    a = _sig(tmp_path, "a", family="ribbon")
    b = _sig(tmp_path, "b", family="ribbon")
    chain = T.select_rungs(a, b)
    assert chain[0] == T.RUNG_MORPH
    assert chain == [T.RUNG_MORPH, T.RUNG_NEUTRAL, T.RUNG_HARDCUT]


def test_ladder_cross_family_skips_morph(tmp_path):
    a = _sig(tmp_path, "a", family="ribbon")
    b = _sig(tmp_path, "b", family="smoke")
    chain = T.select_rungs(a, b)
    assert T.RUNG_MORPH not in chain
    assert chain == [T.RUNG_NEUTRAL, T.RUNG_HARDCUT]


def test_ladder_custom_wins(tmp_path):
    custom = tmp_path / "authored.mp4"
    custom.write_bytes(b"\x00\x00")
    a = _sig(tmp_path, "a")
    b = _sig(tmp_path, "b")
    chain = T.select_rungs(a, b, custom=str(custom))
    assert chain[0] == T.RUNG_CUSTOM


def test_ladder_no_anchors_no_custom_is_empty(tmp_path):
    a = _sig(tmp_path, "a", with_anchors=False)
    b = _sig(tmp_path, "b", with_anchors=False)
    assert T.select_rungs(a, b) == []


def test_bridge_without_anchors_raises(tmp_path):
    a = _sig(tmp_path, "a", with_anchors=False)
    b = _sig(tmp_path, "b", with_anchors=False)
    with pytest.raises(MintError):
        T.bridge(a, b, tmp_path / "out.mp4")


# ---------------------------------------------------------------------------
# integration: real ffmpeg (gated)
# ---------------------------------------------------------------------------

def _have_ffmpeg() -> bool:
    try:
        _tool("ffmpeg")
        return True
    except MintError:
        return False


ffmpeg_only = pytest.mark.skipif(not _have_ffmpeg(), reason="ffmpeg not available")


def _make_clip(dst: Path, *, color: str, dur: float = 3.0) -> Path:
    from bookmark.mint import _run
    dst.parent.mkdir(parents=True, exist_ok=True)
    _run([
        _tool("ffmpeg"), "-y", "-f", "lavfi",
        "-i", f"color=c={color}:s=320x180:r=30:d={dur}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(dst),
    ])
    return dst


@ffmpeg_only
def test_derive_signature_real(tmp_path):
    clip = _make_clip(tmp_path / "red.mp4", color="red")
    sig = T.derive_signature(clip, oradio_id="red", out_dir=tmp_path / "sig")
    assert sig.has_anchors()
    assert sig.palette and sig.palette[0].startswith("#")
    # a pure-red source should read as dominant red-ish
    r = int(sig.palette[0][1:3], 16)
    assert r > 150


@ffmpeg_only
def test_bridge_morph_same_family(tmp_path):
    a_clip = _make_clip(tmp_path / "a.mp4", color="red")
    b_clip = _make_clip(tmp_path / "b.mp4", color="blue")
    a = T.derive_signature(a_clip, oradio_id="a", out_dir=tmp_path / "s", family="ribbon")
    b = T.derive_signature(b_clip, oradio_id="b", out_dir=tmp_path / "s", family="ribbon")
    res = T.bridge(a, b, tmp_path / "bridge.mp4")
    assert res.rung == T.RUNG_MORPH
    assert res.path.exists() and res.path.stat().st_size > 0
    assert not res.degraded


@ffmpeg_only
def test_bridge_cross_family_uses_neutral(tmp_path):
    a_clip = _make_clip(tmp_path / "a.mp4", color="red")
    b_clip = _make_clip(tmp_path / "b.mp4", color="blue")
    a = T.derive_signature(a_clip, oradio_id="a", out_dir=tmp_path / "s", family="ribbon")
    b = T.derive_signature(b_clip, oradio_id="b", out_dir=tmp_path / "s", family="smoke")
    res = T.bridge(a, b, tmp_path / "bridge.mp4")
    assert res.rung == T.RUNG_NEUTRAL
    assert res.path.exists() and res.path.stat().st_size > 0


@ffmpeg_only
def test_bridge_custom_clip_used_verbatim(tmp_path):
    a_clip = _make_clip(tmp_path / "a.mp4", color="red")
    b_clip = _make_clip(tmp_path / "b.mp4", color="blue")
    custom = _make_clip(tmp_path / "authored.mp4", color="green", dur=1.0)
    a = T.derive_signature(a_clip, oradio_id="a", out_dir=tmp_path / "s")
    b = T.derive_signature(b_clip, oradio_id="b", out_dir=tmp_path / "s")
    res = T.bridge(a, b, tmp_path / "bridge.mp4", custom=str(custom))
    assert res.rung == T.RUNG_CUSTOM
    assert res.path.read_bytes() == custom.read_bytes()


@ffmpeg_only
def test_signature_json_roundtrip_on_disk(tmp_path):
    clip = _make_clip(tmp_path / "c.mp4", color="purple")
    sig = T.derive_signature(clip, oradio_id="c", out_dir=tmp_path / "s")
    p = T.write_signature(sig, tmp_path / "c.signature.json")
    back = T.read_signature(p)
    assert back.oradio_id == "c"
    assert back.entry_anchor == sig.entry_anchor
