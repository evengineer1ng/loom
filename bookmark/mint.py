"""The .oradio minter — Bookmark's export pipeline.

An `.oradio` is a **zip container** (extension kept as `.oradio`) holding a JSON `manifest.json`
plus the baked `loop.mp4`. Minting:

  1. ffprobe duration gate: the source must be in range (tighter for ping-pong, which doubles).
  2. Loop baker (`loop_mode`): "pingpong" = clip + its reverse (a palindrome that forces any clip
     to loop) OR "as_is" = the clip already loops, transcode it verbatim (don't mangle a real loop
     like a ribbon or a clean corner exit). Baked INTO the .oradio.
  3. Soulmate check: every oradio needs >=1 soulmate, EXCEPT a kernel (`is_kernel=True`) — the
     bootstrap exception that can stand alone. (See memory: radio-os-bootstrap-plan.)
  4. Bundle write: manifest.json + loop.mp4 zipped to <id>.oradio.

Crossover clips are also CREATED at mint (when a soulmate exists) but NOT bundled — they're
relationship-specific, so they live in the Club keyed by loom:
  club/crossovers/<loom_id>/<from>__<to>.entry.mp4  (the flip, forward)
                                       .exit.mp4    (its reverse)
The crossover interpolation is ffmpeg xfade for v0; swap in RIFE/FILM later via `interpolate=`.

Pure/headless and importable by the Bookmark UI (no tkinter here).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional

FORMAT_VERSION = "oradio.v1"
MIN_LOOP_SECONDS = 2.5
MAX_LOOP_SECONDS = 5.0          # ping-pong source gate (it DOUBLES, so the baked loop is ~2x this)
MAX_NATURAL_LOOP_SECONDS = 20.0  # as-is gate: a clip that ALREADY loops can be a bit longer
ALLOWED_SOURCE_SUFFIXES = {".mp4", ".ogv", ".mov", ".webm", ".mkv"}

# How the source becomes the baked loop.mp4:
#   "pingpong" — forward + reversed = a seamless palindrome (forces ANY clip to loop).
#   "as_is"    — the clip ALREADY loops (a ribbon, a clean corner exit) — don't mangle it; just
#                transcode to the canonical container. First==last is the author's responsibility.
LOOP_MODES = ("pingpong", "as_is")


class MintError(Exception):
    """A mint precondition failed (bad duration, missing soulmate, ffmpeg error)."""


# ---------------------------------------------------------------------------
# ffmpeg / ffprobe resolution
# ---------------------------------------------------------------------------

_KNOWN_FFMPEG_DIRS = [
    r"C:\Users\evana\Documents\radio_os\voices\ffmpeg-n8.0-latest-win64-gpl-8.0\bin",
]


def _tool(name: str) -> str:
    found = shutil.which(name)
    if found:
        return found
    for d in _KNOWN_FFMPEG_DIRS:
        cand = Path(d) / (name + (".exe" if not name.endswith(".exe") else ""))
        if cand.exists():
            return str(cand)
    raise MintError(f"{name} not found on PATH or known locations; install ffmpeg.")


def _run(cmd: List[str]) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        tail = (proc.stderr or "").strip().splitlines()[-6:]
        raise MintError(f"{Path(cmd[0]).name} failed:\n" + "\n".join(tail))
    return proc.stdout


def probe_duration(path: str | Path) -> float:
    out = _run([
        _tool("ffprobe"), "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(path),
    ])
    try:
        return float(out.strip())
    except ValueError:
        raise MintError(f"could not read duration of {path}")


# ---------------------------------------------------------------------------
# loop baker (palindrome)
# ---------------------------------------------------------------------------

def bake_loop(src: str | Path, dst: str | Path, *, mode: str = "pingpong") -> Path:
    """Bake the loop.mp4 (video-only).

    mode "pingpong" -> a seamless palindrome [clip][reversed clip] (forces any clip to loop).
    mode "as_is"    -> the clip already loops; transcode it verbatim, no reversing (don't mangle a
                       clip that's already a clean loop — a ribbon, a corner exit out of frame)."""
    if mode not in LOOP_MODES:
        raise MintError(f"unknown loop mode {mode!r}; expected one of {LOOP_MODES}")
    src, dst = Path(src), Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if mode == "as_is":
        _run([
            _tool("ffmpeg"), "-y", "-i", str(src),
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(dst),
        ])
        return dst
    _run([
        _tool("ffmpeg"), "-y", "-i", str(src),
        "-filter_complex",
        "[0:v]split=2[a][b];[b]reverse[rb];[a][rb]concat=n=2:v=1:a=0[v]",
        "-map", "[v]", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
        str(dst),
    ])
    return dst


# ---------------------------------------------------------------------------
# manifest + bundle
# ---------------------------------------------------------------------------

@dataclass
class OradioManifest:
    id: str
    title: str
    declaration: str = ""
    kernel: bool = False
    # soulmates tracked PER loom: {loom_id: [oradio_id, ...]}. Empty {} for a kernel.
    soulmates: Dict[str, List[str]] = field(default_factory=dict)
    bricks: List[str] = field(default_factory=list)   # authored brick-app; may be empty
    # How the oradio opens on double-click. None -> the ribbon loop (default). For an authored
    # surface: {"kind": "html", "brick": "<brick_id>"} (or {"kind":"html","asset":"..."}).
    open: Optional[Dict[str, object]] = None
    loop: str = "loop.mp4"
    duration_s: float = 0.0
    # The deterministic transition fingerprint (bundled anchors + palette/family/motion). Lets
    # RibbonOS derive a bridge to any other oradio without an LLM. See bookmark/transitions.py.
    signature: Optional[Dict[str, object]] = None
    # Provenance stamp: {name, seed, identity_version} from the author's one-time identity. With
    # soulmate lineage this makes the chain traceable (kernel by X -> RadioOS by X). See
    # bookmark/identity.py. Optional + additive — older readers ignore it.
    author: Optional[Dict[str, object]] = None
    format_version: str = FORMAT_VERSION
    created_at: str = ""

    def to_json(self) -> str:
        data = {
            "format_version": self.format_version,
            "id": self.id,
            "title": self.title,
            "declaration": self.declaration,
            "kernel": self.kernel,
            "soulmates": self.soulmates,
            "bricks": self.bricks,
            "open": self.open,
            "loop": self.loop,
            "duration_s": round(self.duration_s, 3),
            "visual_signature": self.signature,
            "author": self.author,
            "created_at": self.created_at or datetime.now(timezone.utc).isoformat(),
        }
        return json.dumps(data, indent=2, ensure_ascii=False)


def _all_soulmate_ids(soulmates: Dict[str, List[str]]) -> List[str]:
    out: List[str] = []
    for ids in (soulmates or {}).values():
        out.extend(ids)
    return out


def mint_oradio(
    source_video: str | Path,
    *,
    oradio_id: str,
    title: str,
    out_dir: str | Path,
    declaration: str = "",
    soulmates: Optional[Dict[str, List[str]]] = None,
    bricks: Optional[List[str]] = None,
    open_with: Optional[Dict[str, object]] = None,
    is_kernel: bool = False,
    author: Optional[Dict[str, object]] = None,
    loop_mode: str = "pingpong",
    family: str = "ribbon",
    motion_vector: str = "static",
    texture: str = "glass",
    density: float = 0.5,
    derive_signature_anchors: bool = True,
) -> Path:
    """Mint one `.oradio` (zip) from a source loop video. Returns the written .oradio path.

    `open_with` sets how the oradio opens on double-click (None -> ribbon loop; or
    {"kind":"html","brick":"<id>"} for an authored html surface).

    `family`/`motion_vector`/`texture`/`density` are visual-signature authoring hints; the engine
    derives the entry/exit anchors + dominant palette from the baked loop and bundles them so the
    oradio can take part in deterministic transitions (see bookmark/transitions.py). Signature
    derivation is best-effort: a failure there never fails the mint."""
    source_video = Path(source_video)
    if not source_video.exists():
        raise MintError(f"source video not found: {source_video}")
    if source_video.suffix.lower() not in ALLOWED_SOURCE_SUFFIXES:
        raise MintError(f"unsupported source type {source_video.suffix}; need one of "
                        f"{sorted(ALLOWED_SOURCE_SUFFIXES)}")
    if loop_mode not in LOOP_MODES:
        raise MintError(f"unknown loop mode {loop_mode!r}; expected one of {LOOP_MODES}")

    # Ping-pong DOUBLES the clip, so its source gate is tighter; an as-is clip already loops, so it
    # may be longer (you supply the whole loop, we don't add to it).
    max_s = MAX_NATURAL_LOOP_SECONDS if loop_mode == "as_is" else MAX_LOOP_SECONDS
    duration = probe_duration(source_video)
    if not (MIN_LOOP_SECONDS <= duration <= max_s):
        raise MintError(
            f"loop source ({loop_mode}) must be {MIN_LOOP_SECONDS}-{max_s}s; "
            f"{source_video.name} is {duration:.2f}s"
        )

    soulmates = soulmates or {}
    if not is_kernel and not _all_soulmate_ids(soulmates):
        raise MintError(
            "a non-kernel oradio needs at least one soulmate; pass soulmates={loom_id: [id,...]} "
            "or is_kernel=True for the bootstrap exception"
        )
    if is_kernel and _all_soulmate_ids(soulmates):
        # allowed, but the kernel's defining trait is it needs none — keep it clean
        pass

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    work = out_dir / f".{oradio_id}.mint"
    work.mkdir(parents=True, exist_ok=True)
    try:
        loop_path = bake_loop(source_video, work / "loop.mp4", mode=loop_mode)
        loop_duration = probe_duration(loop_path)

        # Derive the visual signature (best-effort) and bundle its anchors. The anchors are
        # referenced by their in-bundle names so a reader can extract them deterministically.
        signature_dict: Optional[Dict[str, object]] = None
        entry_anchor_src: Optional[Path] = None
        exit_anchor_src: Optional[Path] = None
        if derive_signature_anchors:
            try:
                from .transitions import derive_signature
                sig = derive_signature(
                    loop_path, oradio_id=oradio_id, out_dir=work,
                    family=family, motion_vector=motion_vector,
                    texture=texture, density=density,
                )
                entry_anchor_src = Path(sig.entry_anchor)
                exit_anchor_src = Path(sig.exit_anchor)
                # store bundle-relative anchor names in the manifest
                sig.entry_anchor = "entry.png"
                sig.exit_anchor = "exit.png"
                sig.loop = "loop.mp4"
                signature_dict = sig.to_dict()
            except Exception:
                signature_dict = None  # let it cook: a missing signature never fails the mint

        manifest = OradioManifest(
            id=oradio_id,
            title=title,
            declaration=declaration,
            kernel=is_kernel,
            soulmates=soulmates,
            bricks=bricks or [],
            open=open_with,
            loop="loop.mp4",
            duration_s=loop_duration,
            signature=signature_dict,
            author=author,
        )
        (work / "manifest.json").write_text(manifest.to_json(), encoding="utf-8")

        out_path = out_dir / f"{oradio_id}.oradio"
        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(work / "manifest.json", "manifest.json")
            zf.write(loop_path, "loop.mp4")
            if signature_dict and entry_anchor_src and entry_anchor_src.exists():
                zf.write(entry_anchor_src, "entry.png")
            if signature_dict and exit_anchor_src and exit_anchor_src.exists():
                zf.write(exit_anchor_src, "exit.png")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return out_path


# ---------------------------------------------------------------------------
# reading minted bundles
# ---------------------------------------------------------------------------

def read_manifest(oradio_path: str | Path) -> Dict:
    with zipfile.ZipFile(oradio_path) as zf:
        return json.loads(zf.read("manifest.json").decode("utf-8"))


def patch_manifest(oradio_path: str | Path, updates: Dict[str, object]) -> Dict:
    """Merge `updates` into a minted .oradio's manifest.json IN PLACE (loop.mp4 / anchors copied
    verbatim). Additive metadata on the mint bundle — e.g. setting `open` to a shortcut so the
    oradio launches a game on double-click. Returns the new manifest. (Pass a key with value None
    to clear it.)"""
    oradio_path = Path(oradio_path)
    with zipfile.ZipFile(oradio_path) as zf:
        names = zf.namelist()
        manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
        others = {n: zf.read(n) for n in names if n != "manifest.json"}
    for k, v in updates.items():
        if v is None:
            manifest.pop(k, None)
        else:
            manifest[k] = v
    tmp = oradio_path.with_suffix(".oradio.tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))
        for n, data in others.items():
            zf.writestr(n, data)
    tmp.replace(oradio_path)
    return manifest


def set_bundle_asset(
    oradio_path: str | Path,
    *,
    src: Optional[str | Path],
    bundle_name: str,
    manifest_key: Optional[str] = None,
    manifest_value: Optional[object] = None,
) -> Dict:
    """Add / replace / remove a bundled FILE inside a minted .oradio zip (e.g. an mp3 soundtrack or
    a png thumbnail), keeping loop.mp4 / anchors / manifest intact. `src` is the file to inject;
    `src=None` REMOVES `bundle_name`. When `manifest_key` is given it's set to `manifest_value`
    (default = `bundle_name`) so a reader can find the asset — and cleared when removing. Mirrors
    patch_manifest's read-all-then-rewrite (zips can't edit in place). Returns the new manifest."""
    oradio_path = Path(oradio_path)
    with zipfile.ZipFile(oradio_path) as zf:
        names = zf.namelist()
        manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
        others = {n: zf.read(n) for n in names if n not in ("manifest.json", bundle_name)}
    if src is not None:
        others[bundle_name] = Path(src).read_bytes()
        if manifest_key:
            manifest[manifest_key] = bundle_name if manifest_value is None else manifest_value
    else:
        others.pop(bundle_name, None)
        if manifest_key:
            manifest.pop(manifest_key, None)
    tmp = oradio_path.with_suffix(".oradio.tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))
        for n, data in others.items():
            zf.writestr(n, data)
    tmp.replace(oradio_path)
    return manifest


def extract_loop(oradio_path: str | Path, dst: str | Path) -> Path:
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(oradio_path) as zf:
        dst.write_bytes(zf.read("loop.mp4"))
    return dst


# ---------------------------------------------------------------------------
# crossovers (created at mint, stored Club-side keyed by loom)
# ---------------------------------------------------------------------------

def _ffmpeg_xfade(loop_a: Path, loop_b: Path, dst: Path, *, dur: float = 0.6) -> Path:
    """v0 interpolation: an xfade 'flip' from the tail of A into the head of B.

    Replace with a RIFE/FILM backend later (same signature) for true frame interpolation.
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    _run([
        _tool("ffmpeg"), "-y", "-i", str(loop_a), "-i", str(loop_b),
        "-filter_complex",
        # normalize to a common size/fps so xfade can splice, then crossfade.
        f"[0:v]scale=640:360,fps=30,format=yuv420p[a];"
        f"[1:v]scale=640:360,fps=30,format=yuv420p[b];"
        f"[a][b]xfade=transition=fade:duration={dur}:offset=0[v]",
        "-map", "[v]", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
        str(dst),
    ])
    return dst


def _reverse_clip(src: Path, dst: Path) -> Path:
    dst.parent.mkdir(parents=True, exist_ok=True)
    _run([
        _tool("ffmpeg"), "-y", "-i", str(src),
        "-vf", "reverse", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(dst),
    ])
    return dst


CrossoverFn = Callable[[Path, Path, Path], Path]


def mint_crossover(
    loop_from: str | Path,
    loop_to: str | Path,
    *,
    from_id: str,
    to_id: str,
    loom_id: str,
    club_dir: str | Path,
    interpolate: Optional[CrossoverFn] = None,
    family_from: str = "ribbon",
    family_to: str = "ribbon",
    custom: Optional[str] = None,
    logo: Optional[str] = None,
    vigor: float = 0.7,
    profile: Optional[str] = None,
) -> Dict[str, object]:
    """Create the entry + exit crossover for a soulmate pair and store them Club-side keyed by
    loom. Returns {'entry', 'exit', 'rung'}.

    `profile` selects the carrier transition PERSONALITY for this edge (see
    bookmark.transitions.CARRIER_PROFILES; None = the default ribbon-drift).

    By default this uses the HERO carrier (bookmark/transitions.py): both loops play live under a
    deterministic, seeded swirling color-storm, dissolving A->B at the middle; the exit is the
    entry reversed. The storm is seeded by `loom_id:from__to`, so every traversal of this edge
    replays the identical morph. If the carrier can't run (no opencv), it falls back to the
    anchor LADDER (morph/neutral/hardcut) and finally a plain xfade ("let it cook" -- a crossover
    is always produced). Pass `interpolate=` to override with a custom backend (e.g. RIFE/FILM)."""
    loop_from, loop_to = Path(loop_from), Path(loop_to)
    store = Path(club_dir) / "crossovers" / loom_id
    store.mkdir(parents=True, exist_ok=True)
    entry = store / f"{from_id}__{to_id}.entry.mp4"
    exit_ = store / f"{from_id}__{to_id}.exit.mp4"
    edge_key = f"{loom_id}:{from_id}__{to_id}"

    if interpolate is not None:
        interpolate(loop_from, loop_to, entry)
        _reverse_clip(entry, exit_)
        return {"entry": entry, "exit": exit_, "rung": "interpolate"}

    # Preferred: the deterministic fluid carrier (entry + exit from one render).
    try:
        from .transitions import carrier_transition
        carrier_transition(loop_from, loop_to, entry, exit_, edge_key=edge_key, vigor=vigor,
                           profile=profile)
        return {"entry": entry, "exit": exit_, "rung": ("carrier:" + profile if profile else "carrier")}
    except Exception:
        pass  # fall through to the anchor ladder

    rung = "xfade_v0"
    work = store / ".xwork"
    try:
        from .transitions import derive_signature, bridge
        sig_from = derive_signature(loop_from, oradio_id=from_id, out_dir=work, family=family_from)
        sig_to = derive_signature(loop_to, oradio_id=to_id, out_dir=work, family=family_to)
        res = bridge(sig_from, sig_to, entry, custom=custom, logo=logo, edge_key=edge_key, vigor=vigor)
        rung = res.rung
    except Exception:
        _ffmpeg_xfade(loop_from, loop_to, entry)
        rung = "xfade_v0"
    finally:
        shutil.rmtree(work, ignore_errors=True)

    _reverse_clip(entry, exit_)
    return {"entry": entry, "exit": exit_, "rung": rung}
