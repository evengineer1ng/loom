from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "narrative.fragment.island_mystery_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "❓",
    "deterministic": True,
    "inputs": ["narrative.fragment_request.v1"],
    "outputs": ["narrative.fragment_response.v1"],
    "requires": [],
    "provides": ["narrative.island_mystery_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["narrative", "fragment", "mystery", "tier", "island"],
    "description": "Package an island-specific mystery with tier-sensitive descriptions and local narrative pressure.",
}


def build_island_mystery_packet(code: str, label: str, tier_descriptions: dict[str, str] | dict[int, str] | None) -> dict[str, Any]:
    return {
        "code": code,
        "label": label,
        "tier_descriptions": {str(key): str(value) for key, value in (tier_descriptions or {}).items()},
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_island_mystery_packet(
        code=str(payload.get("code") or ""),
        label=str(payload.get("label") or ""),
        tier_descriptions=dict(payload.get("tier_descriptions") or {}),
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
        "receipt_id": "island-mystery-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built island-mystery packet.",
        "refs": [],
        "data": {"code": value.get("code", ""), "label": value.get("label", "")},
    }]
