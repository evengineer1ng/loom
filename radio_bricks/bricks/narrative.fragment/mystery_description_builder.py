from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "narrative.fragment.mystery_description_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🔍",
    "deterministic": True,
    "inputs": ["narrative.fragment_request.v1"],
    "outputs": ["narrative.fragment_response.v1"],
    "requires": [],
    "provides": ["narrative.mystery_description_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["narrative", "fragment", "mystery", "description", "tier"],
    "description": "Package a tier-sensitive mystery description lookup result for either an island mystery or global mountain.",
}


def build_mystery_description_packet(mystery_code: str, tier: str, description: str) -> dict[str, Any]:
    return {"mystery_code": mystery_code, "tier": tier, "description": description}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_mystery_description_packet(
        mystery_code=str(payload.get("mystery_code") or ""),
        tier=str(payload.get("tier") or ""),
        description=str(payload.get("description") or ""),
    )
    output_packet = {
        "packet_type": "narrative.fragment_response.v1",
        "packet_version": "narrative.fragment_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "mystery-description-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built mystery-description packet.",
        "refs": [],
        "data": {"mystery_code": value.get("mystery_code", ""), "tier": value.get("tier", "")},
    }]
