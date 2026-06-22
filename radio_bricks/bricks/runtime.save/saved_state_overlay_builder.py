from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.save.saved_state_overlay_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🩹",
    "deterministic": True,
    "inputs": ["runtime.save_request.v1"],
    "outputs": ["runtime.save_response.v1"],
    "requires": [],
    "provides": ["runtime.saved_state_overlay_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "save", "overlay", "restore", "seed_match"],
    "description": "Package how a saved Neikos player-layer overlays onto a freshly regenerated deterministic island state.",
}


def build_saved_state_overlay_packet(
    save_seed: int,
    state_seed: int,
    applied: bool,
    restored_player_team_count: int,
    restored_creature_count: int,
    restored_discovered_species_count: int,
    restored_fragment_count: int,
) -> dict[str, Any]:
    return {
        "save_seed": int(save_seed),
        "state_seed": int(state_seed),
        "applied": bool(applied),
        "seed_match": int(save_seed) == int(state_seed),
        "restored_player_team_count": int(restored_player_team_count),
        "restored_creature_count": int(restored_creature_count),
        "restored_discovered_species_count": int(restored_discovered_species_count),
        "restored_fragment_count": int(restored_fragment_count),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_saved_state_overlay_packet(
        save_seed=int(payload.get("save_seed") or 0),
        state_seed=int(payload.get("state_seed") or 0),
        applied=bool(payload.get("applied", False)),
        restored_player_team_count=int(payload.get("restored_player_team_count") or 0),
        restored_creature_count=int(payload.get("restored_creature_count") or 0),
        restored_discovered_species_count=int(payload.get("restored_discovered_species_count") or 0),
        restored_fragment_count=int(payload.get("restored_fragment_count") or 0),
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
        "receipt_id": "saved-state-overlay-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built saved-state overlay packet.",
        "refs": [],
        "data": {"applied": value.get("applied", False), "seed_match": value.get("seed_match", False)},
    }]
