from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.save.game_state_save_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "💾",
    "deterministic": True,
    "inputs": ["runtime.save_request.v1"],
    "outputs": ["runtime.save_response.v1"],
    "requires": [],
    "provides": ["runtime.game_state_save_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "save", "state", "player_layer", "deterministic"],
    "description": "Package the mutable Neikos player-layer save surface while leaving deterministic island generation out of band.",
}


def build_game_state_save_packet(
    version: int,
    seed: int,
    tick: int,
    player_location: str,
    instance_counter: int,
    player_team: list[Any] | None,
    discovered_species: list[str] | None,
    discovered_fragments: list[str] | None,
    faction_standings: dict[str, Any] | None,
    current_tier: str,
    base_tier: str,
) -> dict[str, Any]:
    return {
        "version": int(version),
        "seed": int(seed),
        "tick": int(tick),
        "player_location": player_location,
        "instance_counter": int(instance_counter),
        "player_team": list(player_team or []),
        "discovered_species": list(discovered_species or []),
        "discovered_fragments": list(discovered_fragments or []),
        "faction_standings": dict(faction_standings or {}),
        "current_tier": current_tier,
        "base_tier": base_tier,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_game_state_save_packet(
        version=int(payload.get("version") or 0),
        seed=int(payload.get("seed") or 0),
        tick=int(payload.get("tick") or 0),
        player_location=str(payload.get("player_location") or ""),
        instance_counter=int(payload.get("instance_counter") or 0),
        player_team=list(payload.get("player_team") or []),
        discovered_species=list(payload.get("discovered_species") or []),
        discovered_fragments=list(payload.get("discovered_fragments") or []),
        faction_standings=dict(payload.get("faction_standings") or {}),
        current_tier=str(payload.get("current_tier") or ""),
        base_tier=str(payload.get("base_tier") or ""),
    )
    output_packet = {
        "packet_type": "runtime.save_response.v1",
        "packet_version": "runtime.save_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "game-state-save-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built game-state save packet.",
        "refs": [],
        "data": {"seed": value.get("seed", 0), "tick": value.get("tick", 0)},
    }]
