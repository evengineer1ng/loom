from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "narrative.secret.knower_profile_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "👤",
    "deterministic": True,
    "inputs": ["narrative.secret_request.v1"],
    "outputs": ["narrative.secret_response.v1"],
    "requires": [],
    "provides": ["narrative.knower_profile_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["narrative", "secret", "knower", "profile", "masking"],
    "description": "Package a public Hidden Knower profile, including unlock state and optional location masking before reveal.",
}


def build_knower_profile_packet(
    archetype: str,
    name: str,
    location_node_id: str,
    unlock_thresholds: dict[str, float] | None,
    fragment_count: int,
    is_unlocked: bool,
    hide_location_until_unlocked: bool,
) -> dict[str, Any]:
    location = location_node_id
    if hide_location_until_unlocked and not is_unlocked:
        location = "???"
    return {
        "archetype": archetype,
        "name": name,
        "location_node_id": location,
        "unlock_thresholds": {str(key): float(value) for key, value in (unlock_thresholds or {}).items()},
        "fragment_count": int(fragment_count),
        "is_unlocked": bool(is_unlocked),
        "hide_location_until_unlocked": bool(hide_location_until_unlocked),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_knower_profile_packet(
        archetype=str(payload.get("archetype") or ""),
        name=str(payload.get("name") or ""),
        location_node_id=str(payload.get("location_node_id") or ""),
        unlock_thresholds=dict(payload.get("unlock_thresholds") or {}),
        fragment_count=int(payload.get("fragment_count") or 0),
        is_unlocked=bool(payload.get("is_unlocked")),
        hide_location_until_unlocked=bool(payload.get("hide_location_until_unlocked", True)),
    )
    output_packet = {
        "packet_type": "narrative.secret_response.v1",
        "packet_version": "narrative.secret_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "knower-profile-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built Hidden Knower profile packet.",
        "refs": [],
        "data": {"is_unlocked": value.get("is_unlocked", False), "location_node_id": value.get("location_node_id", "")},
    }]
