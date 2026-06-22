from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "narrative.profile.narrative_profile_selection_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🗺️",
    "deterministic": True,
    "inputs": ["narrative.profile_request.v1"],
    "outputs": ["narrative.profile_response.v1"],
    "requires": [],
    "provides": ["narrative.profile_selection_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["narrative", "profile", "selection", "mountains", "mysteries"],
    "description": "Package the deterministic island narrative selection counts and forced-arc choices used to assemble an island profile.",
}


def build_narrative_profile_selection_packet(
    base_tier: str,
    primary_global_count: int,
    secondary_global_count: int,
    primary_mystery_count: int,
    secondary_mystery_count: int,
    active_arc_count: int,
    minor_role_count: int,
    forced_active_arc_codes: list[str] | None,
    primary_league_conflict: str,
    background_league_tension: str,
) -> dict[str, Any]:
    return {
        "base_tier": base_tier,
        "primary_global_count": int(primary_global_count),
        "secondary_global_count": int(secondary_global_count),
        "primary_mystery_count": int(primary_mystery_count),
        "secondary_mystery_count": int(secondary_mystery_count),
        "active_arc_count": int(active_arc_count),
        "minor_role_count": int(minor_role_count),
        "forced_active_arc_codes": list(forced_active_arc_codes or []),
        "primary_league_conflict": primary_league_conflict,
        "background_league_tension": background_league_tension,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_narrative_profile_selection_packet(
        base_tier=str(payload.get("base_tier") or ""),
        primary_global_count=int(payload.get("primary_global_count") or 0),
        secondary_global_count=int(payload.get("secondary_global_count") or 0),
        primary_mystery_count=int(payload.get("primary_mystery_count") or 0),
        secondary_mystery_count=int(payload.get("secondary_mystery_count") or 0),
        active_arc_count=int(payload.get("active_arc_count") or 0),
        minor_role_count=int(payload.get("minor_role_count") or 0),
        forced_active_arc_codes=list(payload.get("forced_active_arc_codes") or []),
        primary_league_conflict=str(payload.get("primary_league_conflict") or ""),
        background_league_tension=str(payload.get("background_league_tension") or ""),
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
        "receipt_id": "narrative-profile-selection-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built narrative-profile selection packet.",
        "refs": [],
        "data": {"base_tier": value.get("base_tier", ""), "forced_active_arc_codes": value.get("forced_active_arc_codes", [])},
    }]
