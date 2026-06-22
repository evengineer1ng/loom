from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.save.oradio_manifest_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧿",
    "deterministic": True,
    "inputs": ["runtime.save_request.v1"],
    "outputs": ["runtime.save_response.v1"],
    "requires": [],
    "provides": ["runtime.oradio_manifest_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "save", "oradio", "manifest", "kernel", "lineage"],
    "description": "Package a minted `.oradio` manifest with kernel role, soulmates, bricks, open surface, and lineage block.",
}


def build_oradio_manifest_packet(
    oradio_id: str,
    title: str,
    declaration: str,
    kernel: bool,
    soulmates: dict[str, list[str]] | None,
    bricks: list[str] | None,
    open_payload: dict[str, Any] | None,
    loop: str,
    duration_s: float,
    visual_signature: dict[str, Any] | None,
    created_at: str,
    format_version: str,
    kernel_lineage: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "id": str(oradio_id),
        "title": str(title),
        "declaration": str(declaration),
        "kernel": bool(kernel),
        "soulmates": {str(key): [str(item) for item in value] for key, value in dict(soulmates or {}).items()},
        "bricks": [str(item) for item in (bricks or [])],
        "open": dict(open_payload or {}) if open_payload else None,
        "loop": str(loop),
        "duration_s": float(duration_s),
        "visual_signature": dict(visual_signature or {}) if visual_signature else None,
        "created_at": str(created_at),
        "format_version": str(format_version),
        "kernel_lineage": dict(kernel_lineage or {}) if kernel_lineage else None,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_oradio_manifest_packet(
        oradio_id=str(payload.get("id") or payload.get("oradio_id") or ""),
        title=str(payload.get("title") or ""),
        declaration=str(payload.get("declaration") or ""),
        kernel=bool(payload.get("kernel")),
        soulmates=dict(payload.get("soulmates") or {}),
        bricks=list(payload.get("bricks") or []),
        open_payload=dict(payload.get("open") or {}) if payload.get("open") else None,
        loop=str(payload.get("loop") or ""),
        duration_s=float(payload.get("duration_s") or 0.0),
        visual_signature=dict(payload.get("visual_signature") or {}) if payload.get("visual_signature") else None,
        created_at=str(payload.get("created_at") or ""),
        format_version=str(payload.get("format_version") or ""),
        kernel_lineage=dict(payload.get("kernel_lineage") or {}) if payload.get("kernel_lineage") else None,
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
        "receipt_id": "oradio-manifest-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built oradio manifest packet.",
        "refs": [],
        "data": {
            "id": value.get("id", ""),
            "kernel": value.get("kernel", False),
            "has_kernel_lineage": bool(value.get("kernel_lineage")),
        },
    }]
