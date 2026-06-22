from __future__ import annotations

from typing import Any


TYPE_STATUS_MAP = {
    "EMBER": "OVERCLOCKED",
    "FROST": "ENTRENCHED",
    "VOLT": "OVERCLOCKED",
    "VENOM": "FRACTURED",
    "SHADE": "DISRUPTED",
    "RIFT": "FLUXED",
    "ALLOY": "ENTRENCHED",
    "PULSE": "DISRUPTED",
    "GALE": "FLUXED",
    "STONE": "ENTRENCHED",
    "TIDE": "FRACTURED",
    "VERDANT": "ENTRENCHED",
    "RADIANT": "OVERCLOCKED",
    "THORN": "FRACTURED",
    "BLOOM": "FLUXED",
    "TORRENT": "FRACTURED",
    "ECHO": "DISRUPTED",
    "DUNE": "DISRUPTED",
}


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "combat.creature.status_effect_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧪",
    "deterministic": True,
    "inputs": ["combat.creature_request.v1"],
    "outputs": ["combat.creature_response.v1"],
    "requires": [],
    "provides": ["combat.status_effect_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["combat", "creature", "status", "type", "effect"],
    "description": "Package the attacker-type to status-effect mapping used by Neikos status moves and per-turn consequences.",
}


def build_status_effect_packet(primary_type: str, existing_stacks: int = 0) -> dict[str, Any]:
    status = TYPE_STATUS_MAP.get(primary_type.upper(), "")
    return {
        "primary_type": primary_type.upper(),
        "status_effect": status,
        "existing_stacks": int(existing_stacks),
        "can_apply": bool(status) and int(existing_stacks) < 2,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_status_effect_packet(
        primary_type=str(payload.get("primary_type") or ""),
        existing_stacks=int(payload.get("existing_stacks") or 0),
    )
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
        "receipt_id": "status-effect-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built status-effect packet.",
        "refs": [],
        "data": {"primary_type": value.get("primary_type", ""), "status_effect": value.get("status_effect", "")},
    }]
