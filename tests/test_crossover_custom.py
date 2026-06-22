"""Custom crossover clips ('hard mode'): an author-provided clip overrides the generated carrier
clip, lives in a durable club/crossovers/<loom>/custom dir, and survives a full regen."""

from __future__ import annotations

from pathlib import Path

import bookmark.mint as M
import oradio_engine.loom_runtime as LR
import ribbon_os_shell as R
from ribbon_os_shell import RadioShell


def _shell(loom_id="stonehenge"):
    sh = RadioShell.__new__(RadioShell)
    sh._active_loom_id = loom_id
    return sh


def test_custom_clip_wins_over_generated(tmp_path, monkeypatch):
    monkeypatch.setattr(R, "CLUB_DIR", str(tmp_path))
    sh = _shell()
    gen = tmp_path / "crossovers" / "stonehenge"
    gen.mkdir(parents=True)
    (gen / "iracing__kernel.entry.mp4").write_bytes(b"GEN")

    # only the generated clip exists -> use it
    assert Path(sh._oradio_crossover_clip("iracing", "kernel")) == gen / "iracing__kernel.entry.mp4"

    # author drops a custom clip -> it wins
    (gen / "custom").mkdir()
    (gen / "custom" / "iracing__kernel.entry.mp4").write_bytes(b"SORA")
    got = sh._oradio_crossover_clip("iracing", "kernel")
    assert Path(got) == gen / "custom" / "iracing__kernel.entry.mp4"
    assert Path(got).read_bytes() == b"SORA"

    # unbonded / no clip either way -> None (caller dissolves)
    assert sh._oradio_crossover_clip("kernel", "iracing") is None
    assert sh._oradio_crossover_clip("iracing", "iracing") is None


def test_custom_path_targets_active_loom(tmp_path, monkeypatch):
    monkeypatch.setattr(R, "CLUB_DIR", str(tmp_path))
    sh = _shell("myloom")
    p = sh._custom_crossover_path("a", "b")
    assert p.endswith(str(Path("crossovers") / "myloom" / "custom" / "a__b.entry.mp4"))


def test_full_regen_preserves_custom(tmp_path, monkeypatch):
    # fast stubs so we don't run the real carrier render
    def fake_extract(o, d):
        d = Path(d); d.write_bytes(b"x"); return d

    def fake_mint(lf, lr, *, from_id, to_id, loom_id, club_dir, **kw):
        d = Path(club_dir) / "crossovers" / loom_id
        d.mkdir(parents=True, exist_ok=True)
        e = d / f"{from_id}__{to_id}.entry.mp4"; x = d / f"{from_id}__{to_id}.exit.mp4"
        e.write_bytes(b"E"); x.write_bytes(b"X")
        return {"entry": e, "exit": x, "rung": "carrier"}

    monkeypatch.setattr(M, "extract_loop", fake_extract)
    monkeypatch.setattr(M, "mint_crossover", fake_mint)

    for n in ("kernel", "iracing"):
        (tmp_path / f"{n}.oradio").write_bytes(b"o")
    loom = tmp_path / "s.loom"; loom.write_text("u", encoding="utf-8")
    nodes = [{"id": "kernel", "oradio": str(tmp_path / "kernel.oradio"), "soulmates": []},
             {"id": "iracing", "oradio": str(tmp_path / "iracing.oradio"), "soulmates": ["kernel"]}]

    LR.sync_crossovers(tmp_path, loom, "stonehenge", nodes)
    cdir = tmp_path / "club" / "crossovers" / "stonehenge"
    (cdir / "custom").mkdir(exist_ok=True)
    (cdir / "custom" / "iracing__kernel.entry.mp4").write_bytes(b"MYSORA")

    LR.sync_crossovers(tmp_path, loom, "stonehenge", nodes)   # full rebuild
    assert (cdir / "custom" / "iracing__kernel.entry.mp4").read_bytes() == b"MYSORA"  # survived
    assert (cdir / "iracing__kernel.entry.mp4").exists()                              # rebuilt
