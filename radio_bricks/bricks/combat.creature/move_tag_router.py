from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "combat.creature.move_tag_router",
    "kind": "router",
    "version": "0.1.0",
    "emoji": "🎛️",
    "deterministic": True,
    "inputs": ["combat.creature_request.v1"],
    "outputs": ["combat.creature_response.v1"],
    "requires": [],
    "provides": ["combat.move_tag_route"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["combat", "creature", "move", "tag", "routing"],
    "description": "Route a Neikos move by its encoded tag suffix, distinguishing damage, status, field, and passive actions.",
}


def route_move_tag(move_name: str) -> dict[str, Any]:
    tag = "D"
    if " [" in move_name:
        parsed = move_name.rsplit(" [", 1)[-1].rstrip("]").upper()
        if parsed in {"D", "S", "F", "P"}:
            tag = parsed
    return {
        "move_name": move_name,
        "tag": tag,
        "action_family": {
            "D": "damage",
            "S": "status",
            "F": "field",
            "P": "passive",
        }[tag],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    value = route_move_tag(str((input_packet.get("payload") or {}).get("move_name") or ""))
    output_packet = {
        "packet_type": "combat.creature_response.v1",
        "packet_version": "combat.creature_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "move-tag-route",
        "brick_id": CONCEPT["id"],
        "kind": "route",
        "label": "Routed Neikos move tag.",
        "refs": [],
        "data": {"tag": value.get("tag", "D"), "action_family": value.get("action_family", "damage")},
    }]
