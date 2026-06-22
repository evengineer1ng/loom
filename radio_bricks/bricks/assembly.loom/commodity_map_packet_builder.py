from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.loom.commodity_map_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📦",
    "deterministic": True,
    "inputs": ["assembly.loom_request.v1"],
    "outputs": ["assembly.loom_response.v1"],
    "requires": [],
    "provides": ["assembly.commodity_map_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "loom", "commodity", "map", "parse"],
    "description": "Package parsed or formatted commodity maps from compact text notation like name and quantity pairs.",
}


def build_commodity_map_packet(
    raw_text: str,
    items: dict[str, Any] | None,
    formatted_text: str,
) -> dict[str, Any]:
    return {
        "raw_text": str(raw_text),
        "items": dict(items or {}),
        "formatted_text": str(formatted_text),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_commodity_map_packet(
        raw_text=str(payload.get("raw_text") or ""),
        items=dict(payload.get("items") or {}),
        formatted_text=str(payload.get("formatted_text") or ""),
    )
    output_packet = {
        "packet_type": "assembly.loom_response.v1",
        "packet_version": "assembly.loom_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "commodity-map-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built commodity-map packet.",
        "refs": [],
        "data": {
            "item_count": len(value.get("items", {})),
            "formatted_text": value.get("formatted_text", ""),
        },
    }]
