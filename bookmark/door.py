"""The bookmark "door" — where a loom's boot screen transitions TO.

Convergence (2026-06-20): each loom carries ONE **bookmark** = "the door of your loom, currently"
= the oradio the boot screen lands on. Default = the kernel. You set it by right-clicking an
oradio in the carousel/galaxy ("set as bookmark"). The boot screen must always have a proper
transition to the current bookmark: an ENTRY (boot -> bookmark) and an EXIT (bookmark -> boot),
built by the deterministic fluid carrier (bookmark/transitions.py) and stored Club-side. Switching
loom = exit current door -> reverse boot -> forward boot -> enter the next loom's door ("you take
your door to their door"). See memory: loom-as-relationship-lens, visual-continuity-engine.

Storage:
  club/doors/index.json                      {loom_id: bookmark_oradio_id}
  club/doors/<loom_id>/boot__<bm>.entry.mp4  boot -> bookmark
  club/doors/<loom_id>/boot__<bm>.exit.mp4   bookmark -> boot
  club/doors/<loom_id>/<bm>.pts.mp4          the seamless push-to-start attract loop (idle)

Club CACHE policy (user): keep only the 2 most-recent door entry/exit PAIRS, then flush -- you
only ever traverse one door at a time, so don't pile up.

Pure/headless; deterministic (the carrier is seeded by the door's edge key).
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

DEFAULT_BOOKMARK = "kernel"          # a loom's default door is the kernel (Phase-1 genesis)
DOOR_CACHE_KEEP = 2                   # keep only the 2 most-recent door pairs Club-side


def _doors_root(club_dir: str | Path) -> Path:
    return Path(club_dir) / "doors"


def _index_path(club_dir: str | Path) -> Path:
    return _doors_root(club_dir) / "index.json"


def _load_index(club_dir: str | Path) -> Dict[str, str]:
    p = _index_path(club_dir)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_index(club_dir: str | Path, idx: Dict[str, str]) -> None:
    p = _index_path(club_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(idx, indent=2, ensure_ascii=False), encoding="utf-8")


def get_bookmark(club_dir: str | Path, loom_id: str) -> str:
    """The loom's current door (oradio id). Defaults to the kernel if none set."""
    return _load_index(club_dir).get(loom_id, DEFAULT_BOOKMARK)


def set_bookmark(club_dir: str | Path, loom_id: str, oradio_id: str) -> str:
    """Set the loom's door to `oradio_id` (right-click 'set as bookmark'). Exactly one per loom."""
    idx = _load_index(club_dir)
    idx[loom_id] = oradio_id
    _save_index(club_dir, idx)
    return oradio_id


def door_edge_key(loom_id: str, bookmark_id: str) -> str:
    """Seed key for the boot<->bookmark door transition (entry direction)."""
    return f"{loom_id}:boot__{bookmark_id}"


def attract_edge_key(loom_id: str, bookmark_id: str) -> str:
    """Seed key for the loom's push-to-start attract loop (its own deterministic signature look)."""
    return f"{loom_id}:pts__{bookmark_id}"


def attract_clip_path(club_dir: str | Path, loom_id: str, bookmark_id: str) -> Path:
    """Where the loom's generated push-to-start attract LOOP lives."""
    return _doors_root(club_dir) / loom_id / f"{bookmark_id}.pts.mp4"


def attract_entry_path(club_dir: str | Path, loom_id: str, bookmark_id: str) -> Path:
    """boot -> pts: the transition INTO the push-to-start loop (replaces the old splash)."""
    return _doors_root(club_dir) / loom_id / f"{bookmark_id}.pts.entry.mp4"


def attract_exit_path(club_dir: str | Path, loom_id: str, bookmark_id: str) -> Path:
    """pts -> bookmark loop: the transition OUT of pts when you "move the mouse / push start"."""
    return _doors_root(club_dir) / loom_id / f"{bookmark_id}.pts.exit.mp4"


def build_attract_loop(
    bookmark_loop: str | Path,
    *,
    loom_id: str,
    bookmark_id: str,
    club_dir: str | Path,
    boot_loop: Optional[str | Path] = None,
    vigor: float = 0.5,
    seconds: Optional[float] = None,
) -> Dict[str, object]:
    """Build the loom's push-to-start TRIPTYCH (entry -> loop -> exit) and store it Club-side:

      loop  = the seamless idle that sits AT the door (smoke off the bookmark loop), seeded
              `loom:pts__bm`.
      entry = boot_loop -> pts loop  (the transition INTO pts; only built if `boot_loop` given)
      exit  = pts loop -> bookmark_loop  (waking up: "move the mouse" -> into the bookmark)

    entry/exit are carrier transitions (calm vigor) so the PTS owns its own in/out instead of the
    old ribbon splash/entry clips. Returns {'loop', 'entry', 'exit'} (entry/exit None if no
    boot_loop). See bookmark/transitions (attract_loop_frames + carrier_transition)."""
    from .transitions import build_attract_loop as _render_loop, carrier_transition

    store = _doors_root(club_dir) / loom_id
    store.mkdir(parents=True, exist_ok=True)
    loop_dst = attract_clip_path(club_dir, loom_id, bookmark_id)
    _render_loop(bookmark_loop, loop_dst, key=attract_edge_key(loom_id, bookmark_id),
                 vigor=vigor, seconds=seconds)

    entry = exit_ = None
    if boot_loop is not None:
        entry = attract_entry_path(club_dir, loom_id, bookmark_id)
        exit_ = attract_exit_path(club_dir, loom_id, bookmark_id)
        # entry: boot -> pts  (seeded ptsin) ;  exit: pts -> bookmark  (seeded ptsout)
        carrier_transition(boot_loop, loop_dst, entry,
                           edge_key=f"{loom_id}:ptsin__{bookmark_id}", vigor=vigor)
        carrier_transition(loop_dst, bookmark_loop, exit_,
                           edge_key=f"{loom_id}:ptsout__{bookmark_id}", vigor=vigor)
    return {"loop": loop_dst, "entry": entry, "exit": exit_}


def flush_door_cache(club_dir: str | Path, keep: int = DOOR_CACHE_KEEP) -> int:
    """Keep only the `keep` most-recent door entry/exit PAIRS (by mtime); delete older. Returns
    the number of pairs deleted."""
    root = _doors_root(club_dir)
    if not root.exists():
        return 0
    pairs: Dict[str, float] = {}    # stem -> newest mtime among its files
    for p in list(root.rglob("*.entry.mp4")) + list(root.rglob("*.exit.mp4")):
        stem = str(p)
        for suf in (".entry.mp4", ".exit.mp4"):
            if stem.endswith(suf):
                stem = stem[: -len(suf)]
                break
        pairs[stem] = max(pairs.get(stem, 0.0), p.stat().st_mtime)
    if len(pairs) <= keep:
        return 0
    ordered = sorted(pairs, key=lambda s: pairs[s], reverse=True)
    deleted = 0
    for stem in ordered[keep:]:
        for suf in (".entry.mp4", ".exit.mp4"):
            f = Path(stem + suf)
            if f.exists():
                f.unlink()
        deleted += 1
    return deleted


def build_boot_door(
    boot_loop: str | Path,
    bookmark_loop: str | Path,
    *,
    loom_id: str,
    bookmark_id: str,
    club_dir: str | Path,
    vigor: float = 0.7,
    seconds: Optional[float] = None,
    size: Optional[Tuple[int, int]] = None,
) -> Dict[str, object]:
    """Build the loom's boot-door transition with the deterministic carrier and store it Club-side.

    entry = boot_loop -> (storm) -> bookmark_loop  (what plays when the boot screen opens the door)
    exit  = bookmark_loop -> (storm) -> boot_loop  (independently seeded; can differ in length)
    Both are seeded (entry by `loom:boot__bm`, exit by the swapped key), so the door replays the
    same morph every time. Records the bookmark in the index and flushes the cache to 2 pairs.
    Returns {'entry', 'exit', 'edge_key', 'bookmark'}."""
    from .transitions import carrier_transition, CARRIER_SIZE

    store = _doors_root(club_dir) / loom_id
    store.mkdir(parents=True, exist_ok=True)
    entry = store / f"boot__{bookmark_id}.entry.mp4"
    exit_ = store / f"boot__{bookmark_id}.exit.mp4"
    edge_key = door_edge_key(loom_id, bookmark_id)

    carrier_transition(
        boot_loop, bookmark_loop, entry, exit_,
        edge_key=edge_key, vigor=vigor, seconds=seconds,
        size=size or CARRIER_SIZE,
    )
    # Also build the loom's push-to-start attract loop (the idle that sits AT this door). Best-
    # effort: a failure here never blocks the door itself.
    pts: Optional[Dict[str, object]] = None
    try:
        pts = build_attract_loop(bookmark_loop, loom_id=loom_id, bookmark_id=bookmark_id,
                                 club_dir=club_dir, boot_loop=boot_loop)
    except Exception:
        pts = None
    set_bookmark(club_dir, loom_id, bookmark_id)
    flush_door_cache(club_dir)
    return {"entry": entry, "exit": exit_, "pts": pts, "edge_key": edge_key,
            "bookmark": bookmark_id}
