from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.brick_catalog_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🗃️",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.brick_catalog_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "brick", "catalog", "registry", "emoji"],
    "description": "Package the kernel brick registry as a catalog with roots, counts, availability, and emoji mappings.",
}


def build_brick_catalog_packet(
    roots: list[str] | None,
    count: int,
    available: int,
    broken: int,
    emoji_of: dict[str, str] | None,
) -> dict[str, Any]:
    return {
        "roots": [str(item) for item in (roots or [])],
        "count": int(count),
        "available": int(available),
        "broken": int(broken),
        "emoji_of": {str(key): str(value) for key, value in dict(emoji_of or {}).items()},
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_brick_catalog_packet(
        roots=list(payload.get("roots") or []),
        count=int(payload.get("count") or 0),
        available=int(payload.get("available") or 0),
        broken=int(payload.get("broken") or 0),
        emoji_of=dict(payload.get("emoji_of") or {}),
    )
    output_packet = {
        "packet_type": "runtime.state_response.v1",
        "packet_version": "runtime.state_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "brick-catalog-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built brick catalog packet.",
        "refs": [],
        "data": {
            "count": value.get("count", 0),
            "available": value.get("available", 0),
            "broken": value.get("broken", 0),
        },
    }]
