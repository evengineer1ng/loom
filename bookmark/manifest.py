"""Brick manifest — the kernel's local, queryable catalog of its brick registry.

Two artifacts, both generated from a live :class:`BrickRegistry`:

  * **manifest** (`build_brick_manifest` / `write_brick_manifest`) — a JSON catalog: every brick's
    id, family, kind, lang, I/O packet types, capabilities, emoji, description, availability.
  * **tape** (`brick_tape_rows` / `write_brick_tape`) — one row per brick (ndjson), each carrying a
    flattened `text` blob. This is the **brick manifest tape** the kernel.oradio ships and loads
    into its OpenCloset/courtroom instance, so the informant can answer a coder's fuzzy prompt with
    a *brick synthesis* (which bricks already cover this) instead of the model writing fresh code.

Pure/headless. The kernel ships this by default so an LLM gets acquainted with the bricks without
spending tokens rediscovering them every session.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator

from .brick_kernel import BrickRegistry

MANIFEST_FORMAT = "loom.brick_manifest.v1"
TAPE_FORMAT = "loom.brick_tape.v1"


def _brick_row(b: Any) -> Dict[str, Any]:
    return {
        "id": b.id,
        "family": b.family,
        "kind": b.kind,
        "lang": b.lang,
        "emoji": b.emoji,
        "deterministic": b.deterministic,
        "inputs": list(b.inputs),
        "outputs": list(b.outputs),
        "requires": list(b.requires),
        "provides": list(b.provides),
        "side_effects": list(b.side_effects),
        "tags": list(b.tags),
        "description": b.description,
        "available": b.available,
    }


def build_brick_manifest(registry: BrickRegistry) -> Dict[str, Any]:
    bricks = [_brick_row(b) for b in sorted(registry, key=lambda b: b.id)]
    return {
        "format": MANIFEST_FORMAT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(bricks),
        "available": sum(1 for b in bricks if b["available"]),
        "bricks": bricks,
    }


def write_brick_manifest(registry: BrickRegistry, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(build_brick_manifest(registry), indent=2, ensure_ascii=False),
                    encoding="utf-8")
    return path


def _row_text(row: Dict[str, Any]) -> str:
    """The flattened, queryable blob for retrieval (id + tags + io + description)."""
    parts = [row["id"], row["family"], row["kind"], row["lang"]]
    parts.extend(row["tags"])
    if row["inputs"]:
        parts.append("in:" + ",".join(row["inputs"]))
    if row["outputs"]:
        parts.append("out:" + ",".join(row["outputs"]))
    if row["provides"]:
        parts.append("provides:" + ",".join(row["provides"]))
    if row["description"]:
        parts.append(row["description"])
    return "  ".join(p for p in parts if p)


def brick_tape_rows(registry: BrickRegistry) -> Iterator[Dict[str, Any]]:
    """Yield one tape row per brick — the courtroom/informant retrieves over these."""
    for b in sorted(registry, key=lambda b: b.id):
        row = _brick_row(b)
        yield {
            "kind": "brick",
            "id": row["id"],
            "emoji": row["emoji"],
            "lang": row["lang"],
            "text": _row_text(row),
            "brick": row,
        }


def write_brick_tape(registry: BrickRegistry, path: str | Path) -> Path:
    """Write the brick manifest tape (ndjson, one brick per line)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        fh.write(json.dumps({"kind": "tape_header", "format": TAPE_FORMAT,
                             "generated_at": datetime.now(timezone.utc).isoformat()},
                            ensure_ascii=False) + "\n")
        for row in brick_tape_rows(registry):
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return path
