from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.delivery_capture_content_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📝",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.delivery_capture_content_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "delivery", "capture", "content", "device"],
    "description": "Build the canonical text line used to narrate a delivery capture against an artifact kind, target device, and status.",
}


def build_delivery_capture_content_packet(
    file_name: str,
    artifact_kind: str,
    device_id: str | None,
    status: str,
    note: str | None = None,
) -> dict[str, Any]:
    target = device_id or "unscoped-device"
    line = f"{str(artifact_kind).upper()} delivery {str(status)}: {str(file_name)} -> {target}"
    if note:
        line += f" ({note})"
    return {
        "file_name": str(file_name),
        "artifact_kind": str(artifact_kind),
        "device_id": device_id,
        "status": str(status),
        "note": note,
        "content": line,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_delivery_capture_content_packet(
        file_name=str(payload.get("file_name") or ""),
        artifact_kind=str(payload.get("artifact_kind") or ""),
        device_id=payload.get("device_id"),
        status=str(payload.get("status") or ""),
        note=payload.get("note"),
    )
    output_packet = {
        "packet_type": "runtime.binding_response.v1",
        "packet_version": "runtime.binding_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "delivery-capture-content-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built delivery capture-content packet.",
        "refs": [],
        "data": {
            "artifact_kind": value.get("artifact_kind", ""),
            "status": value.get("status", ""),
            "device_id": value.get("device_id"),
        },
    }]
