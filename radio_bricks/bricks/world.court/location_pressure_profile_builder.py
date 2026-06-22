from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.court.location_pressure_profile_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["world.court_request.v1"],
    "outputs": ["world.court_response.v1"],
    "requires": [],
    "provides": ["world.location_pressure_profile"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "court", "location", "pressure"],
    "description": "Package a court location's decree multipliers and faction densities into a portable pressure profile.",
}


def build_location_pressure_profile(
    location_id: str,
    name: str,
    decree_multipliers: dict[str, float] | None,
    faction_density: dict[str, float] | None,
) -> dict[str, Any]:
    return {
        "location_id": location_id,
        "name": name,
        "decree_multipliers": dict(decree_multipliers or {}),
        "faction_density": dict(faction_density or {}),
        "dominant_axes": [axis for axis, mult in sorted(dict(decree_multipliers or {}).items(), key=lambda item: item[1], reverse=True)[:3]],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_location_pressure_profile(
        location_id=str(payload.get("location_id") or ""),
        name=str(payload.get("name") or ""),
        decree_multipliers=dict(payload.get("decree_multipliers") or {}),
        faction_density=dict(payload.get("faction_density") or {}),
    )
    output_packet = {
        "packet_type": "world.court_response.v1",
        "packet_version": "world.court_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "location-pressure-profile",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built court location pressure profile.",
        "refs": [],
        "data": {"location_id": value.get("location_id", "")},
    }]
