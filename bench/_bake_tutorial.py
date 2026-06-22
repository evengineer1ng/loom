"""Bake the start-here tutorial loom's relationship media (run in the background — it's slow):
fork styles (aurora @ 15-16, whirlpool @ 15-17), all crossovers, and the kernel bookmark door
(so the recording's ending — take kernel's door into the next loom — works)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from oradio_engine.loom_graph import load_declaration_text
from oradio_engine.loom_runtime import set_edge_style, sync_crossovers

CLUB = ROOT / "club"
loom = ROOT / "exports" / "start-here.loom"
universe, nodes = load_declaration_text(loom.read_text(encoding="utf-8"))

# the fork shows off the personality engine: 16 drifts (aurora), 17 turns (whirlpool)
set_edge_style(CLUB, "start-here", "15", "16", "aurora")
set_edge_style(CLUB, "start-here", "15", "17", "whirlpool")
print("styles set: 15-16 aurora, 15-17 whirlpool", flush=True)

def prog(done, total, label):
    print(f"  crossover {done}/{total}  {label}", flush=True)

built, failed = sync_crossovers(ROOT, loom, universe, nodes, on_progress=prog)
print(f"crossovers: built {built} files, {failed} failed", flush=True)

# kernel door (for the ending: scroll to kernel -> take door into the next loom)
try:
    from bookmark import door
    from bookmark.mint import extract_loop
    import tempfile
    _env = __import__("os").environ.get("RIBBON_OS_MEDIA_ROOT")
    media = Path(_env) if _env else Path(r"C:\Users\evana\OneDrive\Documents\ribbon-os-(4.5)\videos")
    boot_src = media / "boot_carrier_src.mp4"
    tmp = Path(tempfile.mkdtemp())
    kloop = extract_loop(ROOT / "exports" / "kernel.oradio", tmp / "kernel.mp4")
    boot = boot_src if boot_src.exists() else kloop  # degrade if media absent
    door.build_boot_door(boot, kloop, loom_id="start-here", bookmark_id="kernel", club_dir=str(CLUB))
    print("kernel door built for start-here", flush=True)
except Exception as e:
    print(f"kernel door skipped: {e}", flush=True)

print("DONE — tutorial loom is baked and ready to record.", flush=True)
