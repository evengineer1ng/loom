"""Build the 'start-here' tutorial loom: 30 gifs -> 30 oradios (titled with the tutorial lines, in
a seeded-shuffle so the gif<->line pairing is a surprise), + node 0 = the existing kernel.oradio,
wired into a mostly-linear chain with ONE fork at node 15 (16 + 17 both orbit 15). The 'earth'
gif is pinned LAST (node 30). No mint-gate fuss: each .oradio is assembled directly (loop.mp4 +
first/last anchors + manifest), like the kernel rebuild.

    python bench/build_tutorial_loom.py --gifs "D:/New folder/gifs" --earth "giphy (31).gif"

Crossovers/doors are NOT baked here (slow) — run sync_crossovers after (see --print-bake-hint).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import random
import subprocess
import zipfile
from pathlib import Path

import cv2  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(ROOT))   # so `oradio_engine` imports when run as `python bench/...`
EXPORTS = ROOT / "exports"

# nodes 1..30 (node 0 is the existing kernel). 15 forks -> 16 (main, continues to 18) + 17 (leaf).
TITLES = [
    "Ribbon OS is a simulation engine.",                    # 1
    "A .oradio is an Oracle Radio.",                        # 2
    "A .oradio is made of bricks.",                         # 3
    "Every oradio is a living loop.",                       # 4
    "The loop is its face — always moving.",                # 5
    "Each one carries a declaration.",                      # 6
    "A declaration is why you return.",                     # 7
    "Oradios are never alone.",                             # 8
    "A bonded pair are soulmates.",                         # 9
    "A soulmate stays beside its partner, always.",         # 10
    "Between them runs a crossover.",                       # 11
    "The crossover carries you across.",                   # 12
    "Any clip can meet any other.",                        # 13
    "It never cuts to black — it flows.",                  # 14
    "And every crossing has a personality.",               # 15  (fork)
    "Some drift, like an aurora.",                          # 16  (orbits 15)
    "Some turn, like a whirlpool.",                         # 17  (orbits 15)
    "Same engine — different weather.",                    # 18
    "A .loom is a universe of oradios.",                   # 19
    "The loom maps who belongs beside whom.",              # 20
    "The galaxy is that universe, in light.",              # 21
    "Each star an oradio, each line a bond.",              # 22
    "Reach for a far star, and time bends.",               # 23
    "You fly the whole path — skipping none.",             # 24
    "Somewhere a kernel mints them all.",                  # 25
    "Only a kernel may mint a kernel.",                    # 26
    "Every oradio remembers where it came from.",          # 27
    "This kernel is your bookmark —",                      # 28
    "your door home, when you're lost.",                   # 29
    "So take the door. Step into the next world.",         # 30  (earth, last)
]


def nid(n: int) -> str:
    return "kernel" if n == 0 else f"{n:02d}"


def soulmate_of(n: int) -> str:
    # mostly linear; the fork: 16 & 17 both orbit 15, then 18 continues from 16 (17 is the leaf).
    if n == 1:
        return "kernel"
    if n in (16, 17):
        return nid(15)
    if n == 18:
        return nid(16)
    return nid(n - 1)


def build_oradio(gif: Path, node: int, title: str, out: Path) -> None:
    work = out.parent / f".tut_{node:02d}"
    work.mkdir(parents=True, exist_ok=True)
    loop = work / "loop.mp4"
    # gif -> mp4: cap 12s, even dims, <=854 wide, yuv420p (portable + cv2-friendly)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", str(gif), "-t", "12",
        "-vf", "scale='trunc(min(854,iw)/2)*2':-2:flags=lanczos,format=yuv420p", "-an",
        "-c:v", "libx264", "-crf", "20", "-movflags", "+faststart", str(loop),
    ], check=True)
    cap = cv2.VideoCapture(str(loop))
    ok, first = cap.read()
    nframes = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, nframes - 1))
    ok2, last = cap.read()
    cap.release()
    cv2.imwrite(str(work / "entry.png"), first)
    cv2.imwrite(str(work / "exit.png"), last if ok2 else first)
    manifest = {
        "format_version": "oradio.v1", "id": nid(node), "title": title, "declaration": title,
        "kernel": False, "soulmates": {"start-here": [soulmate_of(node)]}, "bricks": [],
        "open": None, "loop": "loop.mp4", "duration_s": round(nframes / fps, 3) if fps else 0.0,
        "visual_signature": {
            "version": "loom.visual_signature.v1", "oradio_id": nid(node), "family": "ribbon",
            "palette": ["#908c8e"], "motion_vector": "drift", "density": 0.5, "texture": "glass",
            "entry_anchor": "entry.png", "exit_anchor": "exit.png", "loop": "loop.mp4",
            "transition_mask": None},
    }
    (work / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(work / "manifest.json", "manifest.json")
        z.write(loop, "loop.mp4")
        z.write(work / "entry.png", "entry.png")
        z.write(work / "exit.png", "exit.png")
    import shutil
    shutil.rmtree(work, ignore_errors=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gifs", required=True)
    ap.add_argument("--earth", required=True, help="filename of the gif to pin LAST (node 30)")
    ap.add_argument("--universe", default="start-here")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    gifs_dir = Path(args.gifs)
    all_gifs = sorted(glob.glob(str(gifs_dir / "*.gif")))
    earth = next((g for g in all_gifs if Path(g).name == args.earth), None)
    if earth is None:
        raise SystemExit(f"earth gif {args.earth!r} not found in {gifs_dir}")
    pool = [g for g in all_gifs if g != earth]
    random.Random(args.seed).shuffle(pool)
    if len(pool) < 29:
        raise SystemExit(f"need >=29 non-earth gifs, found {len(pool)}")

    EXPORTS.mkdir(parents=True, exist_ok=True)
    assign = {n: pool[n - 1] for n in range(1, 30)}   # nodes 1..29 = shuffled
    assign[30] = earth                                # node 30 = earth, last
    for n in range(1, 31):
        out = EXPORTS / f"{nid(n)}.oradio"
        print(f"[{n:02d}/30] {Path(assign[n]).name:18s} -> {out.name}  «{TITLES[n-1]}»")
        build_oradio(Path(assign[n]), n, TITLES[n - 1], out)

    # ---- assemble the loom ----
    from oradio_engine.loom_graph import declaration_text
    kernel_o = EXPORTS / "kernel.oradio"
    nodes = []
    # paths are relative to the LOOM's own dir (it's written into exports/, alongside the oradios)
    if kernel_o.exists():
        nodes.append({"id": "kernel", "label": "kernel", "oradio": "kernel.oradio",
                      "soulmate": "", "soulmates": []})
    for n in range(1, 31):
        sm = soulmate_of(n)
        nodes.append({"id": nid(n), "label": TITLES[n - 1], "oradio": f"{nid(n)}.oradio",
                      "soulmate": sm, "soulmates": [sm]})
    loom_path = EXPORTS / f"{args.universe}.loom"
    loom_path.write_text(declaration_text(args.universe, nodes), encoding="utf-8")
    print(f"\nwrote {loom_path}  ({len(nodes)} nodes)")
    print("NEXT: set fork styles + bake crossovers + kernel door (slow, run in background):")
    print("  python bench/build_tutorial_loom.py is done; run the bake step separately.")


if __name__ == "__main__":
    main()
