from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "narrative.profile.character_arc_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎭",
    "deterministic": True,
    "inputs": ["narrative.profile_request.v1"],
    "outputs": ["narrative.profile_response.v1"],
    "requires": [],
    "provides": ["narrative.character_arc_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["narrative", "profile", "character", "arc", "role"],
    "description": "Package a fixed island character arc archetype with code, label, role hint, and thematic description.",
}


def build_character_arc_packet(
    code: str,
    label: str,
    role_hint: str,
    description: str,
) -> dict[str, Any]:
    return {
        "code": code,
        "label": label,
        "role_hint": role_hint,
        "description": description,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_character_arc_packet(
        code=str(payload.get("code") or ""),
        label=str(payload.get("label") or ""),
        role_hint=str(payload.get("role_hint") or ""),
        description=str(payload.get("description") or ""),
    )
    output_packet = {
        "packet_type": "narrative.profile_response.v1",
        "packet_version": "narrative.profile_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "character-arc-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built character-arc packet.",
        "refs": [],
        "data": {"code": value.get("code", ""), "role_hint": value.get("role_hint", "")},
    }]
