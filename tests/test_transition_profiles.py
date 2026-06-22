"""Transition personalities (the style library): the carrier is one style; profiles swap the
velocity field / coord transform / feedback. Pure-ish checks (registry, resolver, field shapes) +
the per-edge style storage + sync wiring. Full-render determinism is verified separately (live)."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

import bookmark.mint as M
import oradio_engine.loom_runtime as LR
from bookmark.transitions import (
    CARRIER_PROFILES, DEFAULT_PROFILE, carrier_profile, np,
    _field_aurora, _field_whirlpool, _field_woven, _coords_kaleidoscope,
)
from oradio_engine.loom_runtime import edge_style_key, load_edge_styles, set_edge_style


def test_registry_has_the_five_plus_default():
    for name in ("ribbon_drift", "aurora", "echo", "whirlpool", "kaleidoscope", "woven"):
        assert name in CARRIER_PROFILES
    # the default is the original and is a true no-op (no field/transform/knob changes)
    d = CARRIER_PROFILES["ribbon_drift"]
    assert d.field is None and d.coord_transform is None
    assert (d.move_mul, d.decay_bias, d.gain_mul, d.particle_mul, d.bell_k_mul) == (1.0, 0.0, 1.0, 1.0, 1.0)


def test_carrier_profile_resolves_unknown_to_default():
    assert carrier_profile(None).name == DEFAULT_PROFILE
    assert carrier_profile("nope-not-real").name == DEFAULT_PROFILE
    assert carrier_profile("whirlpool").name == "whirlpool"


def test_profile_identities():
    # echo = default field + persistence (afterimage), no field override
    assert CARRIER_PROFILES["echo"].field is None and CARRIER_PROFILES["echo"].decay_bias > 0
    # whirlpool/woven swap the field; kaleidoscope adds a coord transform
    assert CARRIER_PROFILES["whirlpool"].field is _field_whirlpool
    assert CARRIER_PROFILES["woven"].field is _field_woven
    assert CARRIER_PROFILES["kaleidoscope"].coord_transform is _coords_kaleidoscope


@pytest.mark.skipif(np is None, reason="needs numpy")
def test_field_functions_return_well_shaped_fields():
    w, h = 64, 48
    gy, gx = np.mgrid[0:h, 0:w]
    gx = gx.astype(np.float32); gy = gy.astype(np.float32)
    rng = np.random.default_rng(7)
    for fn in (_field_aurora, _field_whirlpool, _field_woven):
        fx, fy = fn(gx, gy, w, h, 1.0, rng, 0.7)
        assert fx.shape == (h, w) and fy.shape == (h, w)
        assert np.isfinite(fx).all() and np.isfinite(fy).all()


@pytest.mark.skipif(np is None, reason="needs numpy")
def test_kaleidoscope_coords_are_finite_and_folded():
    w, h = 80, 80
    gy, gx = np.mgrid[0:h, 0:w]
    sx, sy = _coords_kaleidoscope(gx.astype("f4"), gy.astype("f4"), w, h, segments=6)
    assert sx.shape == (h, w) and sy.shape == (h, w)
    assert np.isfinite(sx).all() and np.isfinite(sy).all()
    # folding into one wedge collapses the variety -> fewer distinct sample points than identity
    assert len(np.unique(np.round(sx))) < w


# ---- per-edge style storage + sync wiring ----

def test_edge_style_key_is_sorted():
    assert edge_style_key("kernel", "iracing") == edge_style_key("iracing", "kernel") == "iracing__kernel"


def test_set_load_clear_styles(tmp_path):
    club = tmp_path / "club"
    set_edge_style(club, "stonehenge", "iracing", "kernel", "whirlpool")
    assert load_edge_styles(club, "stonehenge") == {"iracing__kernel": "whirlpool"}
    # setting the default clears the entry
    set_edge_style(club, "stonehenge", "kernel", "iracing", "ribbon_drift")
    assert load_edge_styles(club, "stonehenge") == {}


def test_sync_passes_per_edge_profile_and_only_edge(tmp_path, monkeypatch):
    captured = []

    def fake_extract(o, d):
        d = Path(d); d.write_bytes(b"x"); return d

    def fake_mint(lf, lr, *, from_id, to_id, loom_id, club_dir, profile=None, **kw):
        captured.append((from_id, to_id, profile))
        dd = Path(club_dir) / "crossovers" / loom_id; dd.mkdir(parents=True, exist_ok=True)
        e = dd / f"{from_id}__{to_id}.entry.mp4"; x = dd / f"{from_id}__{to_id}.exit.mp4"
        e.write_bytes(b"E"); x.write_bytes(b"X")
        return {"entry": e, "exit": x, "rung": "carrier"}

    monkeypatch.setattr(M, "extract_loop", fake_extract)
    monkeypatch.setattr(M, "mint_crossover", fake_mint)

    for n in ("kernel", "iracing", "cyberpunk"):
        (tmp_path / f"{n}.oradio").write_bytes(b"o")
    loom = tmp_path / "s.loom"; loom.write_text("u", encoding="utf-8")
    nodes = [{"id": "kernel", "oradio": str(tmp_path / "kernel.oradio"), "soulmates": []},
             {"id": "iracing", "oradio": str(tmp_path / "iracing.oradio"), "soulmates": ["kernel"]},
             {"id": "cyberpunk", "oradio": str(tmp_path / "cyberpunk.oradio"), "soulmates": ["kernel"]}]
    set_edge_style(tmp_path / "club", "stonehenge", "iracing", "kernel", "whirlpool")

    LR.sync_crossovers(tmp_path, loom, "stonehenge", nodes, only_edge=("iracing", "kernel"))
    assert captured == [("iracing", "kernel", "whirlpool")]   # only that edge, with its style
