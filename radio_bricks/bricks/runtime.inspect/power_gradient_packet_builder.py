from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.power_gradient_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🌐",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.power_gradient_packet"],
    "side_effects": [],
    "ui_slots": ["inspection.power_gradient"],
    "tags": ["runtime", "inspect", "power", "gradient", "anchor"],
    "description": "Package neighbour power rankings with a ready-made anchor list for UI and archive readers.",
}


def build_power_gradient_packet(ranks: dict[str, dict[str, Any]] | None) -> dict[str, Any]:
    rank_map = {str(key): dict(value) for key, value in (ranks or {}).items()}
    anchors = [kingdom_id for kingdom_id, value in rank_map.items() if bool(value.get("is_regional_anchor", False))]
    return {"ranks": rank_map, "anchors": sorted(anchors)}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_power_gradient_packet(dict(payload.get("ranks") or {}))
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
        "receipt_id": "power-gradient-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built power-gradient inspection packet.",
        "refs": [],
        "data": {"anchor_count": len(value.get("anchors", []))},
    }]
