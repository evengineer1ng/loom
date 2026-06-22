from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.faction.faction_status_board_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🏛️",
    "deterministic": True,
    "inputs": ["world.faction_request.v1"],
    "outputs": ["world.faction_response.v1"],
    "requires": [],
    "provides": ["world.faction_status_board_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "faction", "status", "standing", "board"],
    "description": "Package the island faction board with player standing, influence score, territory count, public sentiment, and ideology.",
}


def build_faction_status_board_packet(
    factions: list[dict[str, Any]] | None,
    tick: int,
) -> dict[str, Any]:
    return {
        "factions": [dict(item) for item in (factions or [])],
        "tick": int(tick),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_faction_status_board_packet(
        factions=list(payload.get("factions") or []),
        tick=int(payload.get("tick") or 0),
    )
    output_packet = {
        "packet_type": "world.faction_response.v1",
        "packet_version": "world.faction_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "faction-status-board-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built faction-status board packet.",
        "refs": [],
        "data": {"faction_count": len(value.get("factions", [])), "tick": value.get("tick", 0)},
    }]
