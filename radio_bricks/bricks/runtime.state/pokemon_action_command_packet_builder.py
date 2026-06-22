from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.pokemon_action_command_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎮",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.pokemon_action_command_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "pokemon", "action", "command"],
    "description": "Package a selected Pokemon runtime action command with output id and normalized button list.",
}


def build_pokemon_action_command_packet(output_id: str, buttons: list[str] | None) -> dict[str, Any]:
    return {
        "output_id": str(output_id),
        "buttons": [str(item) for item in (buttons or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_pokemon_action_command_packet(
        output_id=str(payload.get("output_id") or ""),
        buttons=list(payload.get("buttons") or []),
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
        "receipt_id": "pokemon-action-command-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built Pokemon action-command packet.",
        "refs": [],
        "data": {
            "output_id": value.get("output_id", ""),
            "button_count": len(value.get("buttons", [])),
        },
    }]
