"""picture_frame — apply + store decorative picture frames for carousel app icons.

A buzzer-beater subsystem (2026-06-21): in carousel mode every app icon has a border. This brick
lets each oradio carry a DISTINCT frame overlay — a picture frame around its icon. It both STORES
the per-oradio assignment and APPLIES the frame (composites a transparent-center frame over an
icon). Frames are procedural-by-id (so it ships usable with zero assets) and can be overridden by
dropping a `<frame_id>.png` into the library dir.

Contract: loom.concept.v1 (in-file CONCEPT + inspect/validate/run/receipts), like the mined bricks.
Pure compositing (deterministic); the only side effect is reading/writing the small assignment
store + the framed PNG output.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from PIL import Image, ImageDraw, ImageFilter
    HAS_PIL = True
except Exception:  # pragma: no cover
    Image = None  # type: ignore
    HAS_PIL = False

CONCEPT: Dict[str, Any] = {
    "api_version": "loom.concept.v1",
    "id": "ui.frame.picture_frame",
    "kind": "decorator",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["ui.frame_request.v1"],
    "outputs": ["ui.framed_icon.v1"],
    "requires": [],
    "provides": ["picture_frame", "carousel.frame"],
    "side_effects": ["file_read", "file_write"],
    "ui_slots": ["carousel.icon.overlay"],
    "params": [
        {"name": "frame_id", "label": "Frame", "type": "enum",
         "options": ["none", "gold", "neon", "double", "embers", "glass"], "default": "none"},
        {"name": "size", "label": "Icon size (px)", "type": "int", "default": 256}
    ],
    "tags": ["ui", "carousel", "frame", "overlay", "decoration", "kernel"],
    "emoji": "🖼️",
    "description": "Apply + store a distinct decorative picture frame around an oradio's carousel "
                   "icon. Procedural frames by id (gold/neon/double/embers/glass) + optional PNG "
                   "overrides; per-oradio assignment is remembered.",
}

# Built-in procedural frame ids (always available, no assets needed).
BUILTIN_FRAMES = ["none", "gold", "neon", "double", "embers", "glass"]


# ---------------------------------------------------------------------------
# storage
# ---------------------------------------------------------------------------

def _data_dir(context: Optional[Dict[str, Any]] = None) -> Path:
    if context and context.get("frames_dir"):
        d = Path(context["frames_dir"])
    else:
        d = Path(__file__).resolve().parent / "_frames"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _store_path(context: Optional[Dict[str, Any]] = None) -> Path:
    return _data_dir(context) / "assignments.json"


def _load_store(context=None) -> Dict[str, str]:
    p = _store_path(context)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_store(store: Dict[str, str], context=None) -> None:
    _store_path(context).write_text(json.dumps(store, indent=2, ensure_ascii=False), encoding="utf-8")


def assign(oradio_id: str, frame_id: str, context=None) -> str:
    store = _load_store(context)
    store[oradio_id] = frame_id
    _save_store(store, context)
    return frame_id


def get_assignment(oradio_id: str, context=None) -> str:
    return _load_store(context).get(oradio_id, "none")


def list_frames(context=None) -> List[str]:
    """Built-in frames + any <id>.png dropped into the library dir."""
    extra = sorted(p.stem for p in _data_dir(context).glob("*.png"))
    out = list(BUILTIN_FRAMES)
    for e in extra:
        if e not in out:
            out.append(e)
    return out


# ---------------------------------------------------------------------------
# the frame overlay (procedural-by-id, transparent center)
# ---------------------------------------------------------------------------

def _builtin_overlay(frame_id: str, size: int):
    """Draw a transparent-center frame overlay (RGBA) at `size`x`size` for a built-in id."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    if frame_id == "gold":
        for i, (w, col) in enumerate([(0.06, (244, 198, 107, 255)), (0.09, (160, 120, 40, 230))]):
            pad = int(s * 0.02) + i
            d.rounded_rectangle([pad, pad, s - 1 - pad, s - 1 - pad], radius=int(s * 0.12),
                                outline=col, width=max(2, int(s * (w - i * 0.03))))
    elif frame_id == "neon":
        glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.rounded_rectangle([int(s * .05)] * 1 + [int(s * .05), s - int(s * .05), s - int(s * .05)],
                             radius=int(s * .14), outline=(111, 140, 255, 255), width=max(3, int(s * .05)))
        glow = glow.filter(ImageFilter.GaussianBlur(s * 0.03))
        img = Image.alpha_composite(img, glow)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([int(s * .05), int(s * .05), s - int(s * .05), s - int(s * .05)],
                            radius=int(s * .14), outline=(180, 200, 255, 255), width=max(2, int(s * .02)))
    elif frame_id == "double":
        for pad_f in (0.04, 0.10):
            pad = int(s * pad_f)
            d.rounded_rectangle([pad, pad, s - 1 - pad, s - 1 - pad], radius=int(s * 0.10),
                                outline=(232, 236, 248, 235), width=max(1, int(s * 0.012)))
    elif frame_id == "embers":
        for pad_f, col in ((0.03, (255, 140, 66, 255)), (0.07, (255, 61, 104, 220))):
            pad = int(s * pad_f)
            d.rounded_rectangle([pad, pad, s - 1 - pad, s - 1 - pad], radius=int(s * 0.13),
                                outline=col, width=max(2, int(s * 0.03)))
        img = img.filter(ImageFilter.GaussianBlur(s * 0.004))
    elif frame_id == "glass":
        pad = int(s * 0.04)
        d.rounded_rectangle([pad, pad, s - 1 - pad, s - 1 - pad], radius=int(s * 0.16),
                            outline=(210, 225, 255, 180), width=max(2, int(s * 0.02)))
        d.line([int(s * 0.12), int(s * 0.12), int(s * 0.42), int(s * 0.12)],
               fill=(255, 255, 255, 150), width=max(1, int(s * 0.012)))
    return img


def frame_overlay(frame_id: str, size: int, context=None):
    """Return an RGBA frame overlay: a dropped-in <id>.png (resized) if present, else procedural."""
    if not HAS_PIL:
        raise RuntimeError("picture_frame needs Pillow (PIL)")
    png = _data_dir(context) / f"{frame_id}.png"
    if png.exists():
        return Image.open(png).convert("RGBA").resize((size, size), Image.LANCZOS)
    if frame_id == "none":
        return Image.new("RGBA", (size, size), (0, 0, 0, 0))
    return _builtin_overlay(frame_id if frame_id in BUILTIN_FRAMES else "gold", size)


def apply_frame(icon, frame_id: str, size: int = 256, context=None):
    """Composite `frame_id` over an icon (path or PIL.Image). Returns an RGBA PIL.Image."""
    if not HAS_PIL:
        raise RuntimeError("picture_frame needs Pillow (PIL)")
    base = Image.open(icon).convert("RGBA") if isinstance(icon, (str, Path)) else icon.convert("RGBA")
    base = base.resize((size, size), Image.LANCZOS)
    return Image.alpha_composite(base, frame_overlay(frame_id, size, context))


# ---------------------------------------------------------------------------
# loom.concept.v1 contract
# ---------------------------------------------------------------------------

def inspect() -> Dict[str, Any]:
    return CONCEPT


def validate(input_packet: Dict[str, Any], context=None) -> List[Dict[str, str]]:
    issues: List[Dict[str, str]] = []
    payload = (input_packet or {}).get("payload", {})
    if not payload.get("oradio_id"):
        issues.append({"code": "missing_oradio_id", "message": "payload.oradio_id is required"})
    fid = payload.get("frame_id")
    if fid is not None and fid not in list_frames(context):
        issues.append({"code": "unknown_frame", "message": f"frame_id {fid!r} not in library"})
    return issues


def run(input_packet: Dict[str, Any], context=None) -> Dict[str, Any]:
    payload = (input_packet or {}).get("payload", {})
    oradio_id = payload.get("oradio_id", "")
    frame_id = payload.get("frame_id")
    icon = payload.get("icon")
    if frame_id:                       # assigning a frame to this oradio
        assign(oradio_id, frame_id, context)
    chosen = frame_id or get_assignment(oradio_id, context)

    out_path = None
    if icon and HAS_PIL:
        size = int(payload.get("size", 256))
        framed = apply_frame(icon, chosen, size=size, context=context)
        out_path = payload.get("out") or str(_data_dir(context) / f"{oradio_id}.framed.png")
        framed.save(out_path)

    output = {
        "packet_type": "ui.framed_icon.v1",
        "payload": {"oradio_id": oradio_id, "frame_id": chosen, "path": out_path},
    }
    return {"ok": True, "output_packet": output, "receipts": receipts(output),
            "issues": [], "meta": {"frames_available": list_frames(context)}}


def receipts(output_packet: Dict[str, Any]) -> List[Dict[str, Any]]:
    p = (output_packet or {}).get("payload", {})
    return [{
        "receipt_id": f"frame:{p.get('oradio_id', '')}",
        "brick_id": CONCEPT["id"],
        "kind": "assignment",
        "label": f"{p.get('oradio_id', '')} -> {p.get('frame_id', 'none')}",
        "refs": [p.get("path")] if p.get("path") else [],
        "data": {"frame_id": p.get("frame_id")},
    }]
