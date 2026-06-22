from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.save.restore_state_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧳",
    "deterministic": True,
    "inputs": ["runtime.save_request.v1"],
    "outputs": ["runtime.save_response.v1"],
    "requires": [],
    "provides": ["runtime.restore_state_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "save", "restore", "trajectory", "creatures"],
    "description": "Package the detailed restore overlay applied from a Neikos save onto regenerated state, including creatures, team, tiers, trainers, and trajectory.",
}


def build_restore_state_packet(
    tick: int,
    player_location: str,
    player_team_count: int,
    restored_creature_count: int,
    discovered_species_count: int,
    discovered_fragment_count: int,
    current_tier: str,
    base_tier: str,
    trainer_count_restored: int,
    trajectory_snapshot: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "tick": int(tick),
        "player_location": player_location,
        "player_team_count": int(player_team_count),
        "restored_creature_count": int(restored_creature_count),
        "discovered_species_count": int(discovered_species_count),
        "discovered_fragment_count": int(discovered_fragment_count),
        "current_tier": current_tier,
        "base_tier": base_tier,
        "trainer_count_restored": int(trainer_count_restored),
        "trajectory_snapshot": dict(trajectory_snapshot or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_restore_state_packet(
        tick=int(payload.get("tick") or 0),
        player_location=str(payload.get("player_location") or ""),
        player_team_count=int(payload.get("player_team_count") or 0),
        restored_creature_count=int(payload.get("restored_creature_count") or 0),
        discovered_species_count=int(payload.get("discovered_species_count") or 0),
        discovered_fragment_count=int(payload.get("discovered_fragment_count") or 0),
        current_tier=str(payload.get("current_tier") or ""),
        base_tier=str(payload.get("base_tier") or ""),
        trainer_count_restored=int(payload.get("trainer_count_restored") or 0),
        trajectory_snapshot=dict(payload.get("trajectory_snapshot") or {}),
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
        "receipt_id": "restore-state-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built restore-state packet.",
        "refs": [],
        "data": {"tick": value.get("tick", 0), "player_team_count": value.get("player_team_count", 0)},
    }]
