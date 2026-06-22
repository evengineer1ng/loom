from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.save.visual_signature_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪞",
    "deterministic": True,
    "inputs": ["runtime.save_request.v1"],
    "outputs": ["runtime.save_response.v1"],
    "requires": [],
    "provides": ["runtime.visual_signature_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "save", "visual", "signature", "transition", "palette"],
    "description": "Package an oradio visual signature with family, palette, motion, density, texture, and anchor frames.",
}


def build_visual_signature_packet(
    oradio_id: str,
    family: str,
    palette: list[str] | None,
    motion_vector: str,
    density: float,
    texture: str,
    entry_anchor: str,
    exit_anchor: str,
    loop: str,
    transition_mask: str | None,
    version: str,
) -> dict[str, Any]:
    return {
        "oradio_id": str(oradio_id),
        "family": str(family),
        "palette": [str(item) for item in (palette or [])],
        "motion_vector": str(motion_vector),
        "density": float(density),
        "texture": str(texture),
        "entry_anchor": str(entry_anchor),
        "exit_anchor": str(exit_anchor),
        "loop": str(loop),
        "transition_mask": transition_mask,
        "version": str(version),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_visual_signature_packet(
        oradio_id=str(payload.get("oradio_id") or ""),
        family=str(payload.get("family") or ""),
        palette=list(payload.get("palette") or []),
        motion_vector=str(payload.get("motion_vector") or ""),
        density=float(payload.get("density") or 0.0),
        texture=str(payload.get("texture") or ""),
        entry_anchor=str(payload.get("entry_anchor") or ""),
        exit_anchor=str(payload.get("exit_anchor") or ""),
        loop=str(payload.get("loop") or ""),
        transition_mask=payload.get("transition_mask"),
        version=str(payload.get("version") or ""),
    )
    output_packet = {
        "packet_type": "runtime.save_response.v1",
        "packet_version": "runtime.save_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "visual-signature-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built visual signature packet.",
        "refs": [],
        "data": {
            "oradio_id": value.get("oradio_id", ""),
            "family": value.get("family", ""),
        },
    }]
