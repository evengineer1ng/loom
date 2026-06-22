from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.pressure.location_profile_reader",
    "kind": "reader",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["world.pressure_request.v1"],
    "outputs": ["world.pressure_response.v1"],
    "requires": [],
    "provides": ["world.location_pressure_profile"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "pressure", "location", "profile"],
    "description": "Read a location pressure profile into decree multipliers, faction density, emotional texture, legitimacy bias, and visibility.",
}


def read_location_profile(profile: dict[str, Any] | None) -> dict[str, Any]:
    row = dict(profile or {})
    return {
        "location_id": row.get("location_id") or "",
        "name": row.get("name") or "",
        "description": row.get("description") or "",
        "decree_multipliers": dict(row.get("decree_multipliers") or {}),
        "faction_density": dict(row.get("faction_density") or {}),
        "emotional_texture": dict(row.get("emotional_texture") or {}),
        "legitimacy_bias": float(row.get("legitimacy_bias") or 0.0),
        "visibility": float(row.get("visibility") or 0.0),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    value = read_location_profile(dict(input_packet.get("payload") or {}))
    output_packet = {
        "packet_type": "world.pressure_response.v1",
        "packet_version": "world.pressure_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "location-profile-reader",
        "brick_id": CONCEPT["id"],
        "kind": "read",
        "label": "Read location pressure profile.",
        "refs": [],
        "data": {"location_id": value.get("location_id", ""), "visibility": value.get("visibility", 0.0)},
    }]
