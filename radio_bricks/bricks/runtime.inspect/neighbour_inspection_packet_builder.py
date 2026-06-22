from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.neighbour_inspection_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧭",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.neighbour_inspection_packet"],
    "side_effects": [],
    "ui_slots": ["inspection.neighbour"],
    "tags": ["runtime", "inspect", "neighbour", "checkpoint", "materialise"],
    "description": "Package a materialised neighbour read model alongside its seed and checkpoint provenance.",
}


def build_neighbour_inspection_packet(
    kingdom_id: str,
    seed: int,
    used_checkpoint: bool,
    neighbour_state: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "kingdom_id": kingdom_id,
        "seed": int(seed),
        "used_checkpoint": bool(used_checkpoint),
        "neighbour_state": dict(neighbour_state or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_neighbour_inspection_packet(
        kingdom_id=str(payload.get("kingdom_id") or ""),
        seed=int(payload.get("seed") or 0),
        used_checkpoint=bool(payload.get("used_checkpoint", False)),
        neighbour_state=dict(payload.get("neighbour_state") or {}),
    )
    output_packet = {
        "packet_type": "runtime.inspect_response.v1",
        "packet_version": "runtime.inspect_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "neighbour-inspection-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built neighbour inspection packet.",
        "refs": [],
        "data": {"kingdom_id": value.get("kingdom_id", ""), "used_checkpoint": value.get("used_checkpoint", False)},
    }]
