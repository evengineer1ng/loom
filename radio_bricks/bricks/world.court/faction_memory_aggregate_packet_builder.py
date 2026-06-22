from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.court.faction_memory_aggregate_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧠",
    "deterministic": True,
    "inputs": ["world.court_request.v1"],
    "outputs": ["world.court_response.v1"],
    "requires": [],
    "provides": ["world.faction_memory_aggregate_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "court", "faction", "memory", "aggregate"],
    "description": "Package faction-level inherited memory with collective trust, resentment, label, and retained narrative-memory count.",
}


def build_faction_memory_aggregate_packet(
    faction_id: str,
    collective_trust: float,
    collective_resentment: float,
    collective_label: str,
    memory_count: int,
) -> dict[str, Any]:
    return {
        "faction_id": str(faction_id),
        "collective_trust": float(collective_trust),
        "collective_resentment": float(collective_resentment),
        "collective_label": str(collective_label),
        "memory_count": int(memory_count),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_faction_memory_aggregate_packet(
        faction_id=str(payload.get("faction_id") or ""),
        collective_trust=float(payload.get("collective_trust") or 0.0),
        collective_resentment=float(payload.get("collective_resentment") or 0.0),
        collective_label=str(payload.get("collective_label") or ""),
        memory_count=int(payload.get("memory_count") or 0),
    )
    output_packet = {
        "packet_type": "world.court_response.v1",
        "packet_version": "world.court_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "faction-memory-aggregate-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built faction-memory aggregate packet.",
        "refs": [],
        "data": {
            "faction_id": value.get("faction_id", ""),
            "collective_trust": value.get("collective_trust", 0.0),
            "memory_count": value.get("memory_count", 0),
        },
    }]
