from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "narrative.profile.island_narrative_profile_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧵",
    "deterministic": True,
    "inputs": ["narrative.profile_request.v1"],
    "outputs": ["narrative.profile_response.v1"],
    "requires": [],
    "provides": ["narrative.island_narrative_profile_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["narrative", "profile", "island", "mystery", "conflict"],
    "description": "Package the deterministic island narrative profile with active mountains, mysteries, character arcs, league conflict, and founder framing.",
}


def build_island_narrative_profile_packet(
    primary_global_boulders: list[str] | None,
    secondary_global_boulders: list[str] | None,
    primary_mysteries: list[str] | None,
    secondary_mysteries: list[str] | None,
    active_character_arcs: list[str] | None,
    minor_roles: list[str] | None,
    primary_league_conflict: str,
    background_league_tension: str,
    founder_framing: dict[str, str] | None,
    resolved_mysteries: list[str] | None,
    unresolved_mysteries: list[str] | None,
) -> dict[str, Any]:
    return {
        "primary_global_boulders": list(primary_global_boulders or []),
        "secondary_global_boulders": list(secondary_global_boulders or []),
        "primary_mysteries": list(primary_mysteries or []),
        "secondary_mysteries": list(secondary_mysteries or []),
        "active_character_arcs": list(active_character_arcs or []),
        "minor_roles": list(minor_roles or []),
        "primary_league_conflict": primary_league_conflict,
        "background_league_tension": background_league_tension,
        "founder_framing": dict(founder_framing or {}),
        "resolved_mysteries": list(resolved_mysteries or []),
        "unresolved_mysteries": list(unresolved_mysteries or []),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_island_narrative_profile_packet(
        primary_global_boulders=list(payload.get("primary_global_boulders") or []),
        secondary_global_boulders=list(payload.get("secondary_global_boulders") or []),
        primary_mysteries=list(payload.get("primary_mysteries") or []),
        secondary_mysteries=list(payload.get("secondary_mysteries") or []),
        active_character_arcs=list(payload.get("active_character_arcs") or []),
        minor_roles=list(payload.get("minor_roles") or []),
        primary_league_conflict=str(payload.get("primary_league_conflict") or ""),
        background_league_tension=str(payload.get("background_league_tension") or ""),
        founder_framing=dict(payload.get("founder_framing") or {}),
        resolved_mysteries=list(payload.get("resolved_mysteries") or []),
        unresolved_mysteries=list(payload.get("unresolved_mysteries") or []),
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
        "receipt_id": "island-narrative-profile-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built island narrative-profile packet.",
        "refs": [],
        "data": {"primary_mystery_count": len(value.get("primary_mysteries", [])), "active_arc_count": len(value.get("active_character_arcs", []))},
    }]
