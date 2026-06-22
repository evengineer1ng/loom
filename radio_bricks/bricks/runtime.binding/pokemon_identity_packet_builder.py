from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.pokemon_identity_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧬",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.pokemon_identity_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "pokemon", "identity", "bridge"],
    "description": "Package inferred Pokemon runtime identity with profile name and game name derived from the active window title.",
}


def build_pokemon_identity_packet(profile_name: str, game_name: str) -> dict[str, Any]:
    return {
        "profile_name": str(profile_name),
        "game_name": str(game_name),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_pokemon_identity_packet(
        profile_name=str(payload.get("profile_name") or ""),
        game_name=str(payload.get("game_name") or ""),
    )
    output_packet = {
        "packet_type": "runtime.binding_response.v1",
        "packet_version": "runtime.binding_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "pokemon-identity-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built Pokemon identity packet.",
        "refs": [],
        "data": {
            "profile_name": value.get("profile_name", ""),
            "game_name": value.get("game_name", ""),
        },
    }]
