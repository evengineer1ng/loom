"""Open an .oradio — the double-click launcher.

An oradio opens to its **ribbon loop** by default. If the author set the manifest `open` field to
an html surface, opening serves that page locally instead (the html-as-oradio surface). This is
the resolver side of the polyglot brick work: `open = {"kind":"html","brick":"<id>"}` (resolved
via the brick registry) or `{"kind":"html","asset":"<path>"}` (a direct file).

`resolve_open_plan()` is the SINGLE source of truth for "what does this oradio open to" — shared by
BOTH entry points (the file-manager double-click via oradio_player.py AND the RibbonOS
carousel/galaxy via ribbon_os_shell.py) so an oradio always opens to the same thing no matter how
you reach it. It reads the manifest and returns an OPEN PLAN; the caller executes it in its own
context. The ladder (additive; the `open` field stays a free-form dict — nothing in the frozen
format changes):

  open.kind == "shortcut"  -> {"mode":"shortcut", ...}     run a target (game/exe/url)
  open.kind == "html"      -> {"mode":"html", ...}         serve a brick/asset page
  bricks: [<id>, ...]      -> {"mode":"app", ...}          run the first brick's asset (kernel ->
                                                           bookmark.py), RESOLVED from the installed
                                                           brick registry; if it isn't installed,
                                                           degrades to "loop" with `unresolved_brick`
  (non-zip descriptor)     -> {"mode":"descriptor", ...}   the legacy YAML loom-player path
  else                     -> {"mode":"loop", ...}         the visual loop (RibbonOS plays loop.mp4)

Design decisions (user, 2026-06-21): oradios stay LIGHTWEIGHT — brick code is referenced by id and
resolved from the install, never bundled; a missing brick never dead-ends (falls to the loop). A
pure-loop oradio opened from the file manager is "empty" -> prompt "open in RibbonOS?" (the caller
owns that prompt; there is deliberately NO separate standalone visual player — a player would be a
brick the author chose not to add).
"""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Any, Dict, Optional

from .brick_kernel import Brick, BrickRegistry, serve_brick
from .mint import read_manifest


def default_bricks_root() -> Path:
    """The installed RadioOS brick trove (sibling `bricks/` of this package's repo root)."""
    return Path(__file__).resolve().parent.parent / "bricks"


def resolve_open_plan(
    oradio_path: str | Path,
    *,
    registry: Optional[BrickRegistry] = None,
    bricks_root: Optional[str | Path] = None,
) -> Dict[str, Any]:
    """Decide HOW an oradio opens (see module docstring for the ladder). Pure: never launches
    anything, never raises — it only returns a plan dict with a `mode`. The caller executes it.

    `registry`/`bricks_root` let a caller reuse an already-loaded catalog (the shell has one) or
    point at a non-default install; by default the local `bricks/` trove is discovered."""
    oradio_path = Path(oradio_path)

    # A descriptor-style .oradio (the Loom authoring path) is a plain YAML file, not a zip; route
    # those to the legacy loom-player path unchanged.
    if oradio_path.is_file() and not zipfile.is_zipfile(oradio_path):
        return {"mode": "descriptor", "oradio": str(oradio_path)}

    try:
        manifest = read_manifest(oradio_path)
    except Exception as exc:
        return {"mode": "error", "oradio": str(oradio_path), "error": f"unreadable manifest: {exc}"}

    opn = manifest.get("open")
    if isinstance(opn, dict) and opn.get("kind") == "shortcut":
        return {"mode": "shortcut", "oradio": str(oradio_path), **opn}
    if isinstance(opn, dict) and opn.get("kind") == "html":
        return {"mode": "html", "oradio": str(oradio_path), "open": opn}

    loop_name = str(manifest.get("loop") or "loop.mp4")

    # An authored brick-app (incl. the kernel). Resolve the FIRST brick from the install; run its
    # asset. Referenced-but-not-installed degrades to the loop so it never dead-ends.
    bricks = manifest.get("bricks") or []
    if bricks:
        reg = registry
        if reg is None:
            reg = BrickRegistry.from_path(Path(bricks_root) if bricks_root else default_bricks_root())
        brick_id = str(bricks[0])
        brick = reg.get(brick_id)
        if brick is not None and getattr(brick, "available", False) and getattr(brick, "asset", None):
            return {
                "mode": "app",
                "oradio": str(oradio_path),
                "brick_id": brick_id,
                "lang": brick.lang,
                "asset": str(brick.asset),
                "kind": (brick.concept or {}).get("kind", brick.kind),
                "is_kernel": bool(manifest.get("kernel")),
                "loop": loop_name,
            }
        return {
            "mode": "loop",
            "oradio": str(oradio_path),
            "loop": loop_name,
            "unresolved_brick": brick_id,
            "reason": (brick.error if brick is not None else "brick not found in this install"),
        }

    return {"mode": "loop", "oradio": str(oradio_path), "loop": loop_name}


def open_oradio(oradio_path: str | Path, registry: Optional[BrickRegistry] = None,
                *, open_browser: bool = True) -> Dict[str, Any]:
    """Open an oradio. Returns a descriptor:
      html  -> {"mode":"html", "url":..., "httpd":..., ...}  (caller owns httpd.shutdown())
      loop  -> {"mode":"loop", "loop":"loop.mp4", "oradio":<path>}  (RibbonOS plays the loop)
    """
    oradio_path = Path(oradio_path)
    manifest = read_manifest(oradio_path)
    opn = manifest.get("open")

    if isinstance(opn, dict) and opn.get("kind") == "html":
        brick: Optional[Brick] = None
        if opn.get("brick") and registry is not None:
            brick = registry.get(str(opn["brick"]))
        if brick is None and opn.get("asset"):
            asset = Path(str(opn["asset"]))
            brick = Brick(id="oradio.open", path=asset, lang="html", asset=asset,
                          available=asset.exists())
        if brick is None:
            return {"mode": "html", "error": "open.html could not resolve a brick or asset",
                    "open": opn}
        served = serve_brick(brick, open_browser=open_browser)
        return {"mode": "html", **served}

    # default: the ribbon loop (RibbonOS renders it from the bundled loop.mp4)
    return {"mode": "loop", "loop": manifest.get("loop", "loop.mp4"), "oradio": str(oradio_path)}
