from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.loom.forkuniverse_location_realization_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📍",
    "deterministic": True,
    "inputs": ["assembly.loom_request.v1"],
    "outputs": ["assembly.loom_response.v1"],
    "requires": [],
    "provides": ["assembly.forkuniverse_location_realization_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "loom", "forkuniverse", "location", "template"],
    "description": "Package the realized location rows derived from location templates, district targets, and fallback world-core defaults.",
}


def build_forkuniverse_location_realization_packet(
    district_target: int,
    location_templates: list[dict[str, Any]] | None,
    location_rows: list[dict[str, Any]] | None,
    used_fallback_core_district: bool,
) -> dict[str, Any]:
    return {
        "district_target": int(district_target),
        "location_templates": [dict(item) for item in (location_templates or [])],
        "location_rows": [dict(item) for item in (location_rows or [])],
        "used_fallback_core_district": bool(used_fallback_core_district),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_forkuniverse_location_realization_packet(
        district_target=int(payload.get("district_target") or 0),
        location_templates=list(payload.get("location_templates") or []),
        location_rows=list(payload.get("location_rows") or []),
        used_fallback_core_district=bool(payload.get("used_fallback_core_district")),
    )
    output_packet = {
        "packet_type": "assembly.loom_response.v1",
        "packet_version": "assembly.loom_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "forkuniverse-location-realization-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built ForkUniverse location-realization packet.",
        "refs": [],
        "data": {
            "district_target": value.get("district_target", 0),
            "row_count": len(value.get("location_rows", [])),
            "used_fallback_core_district": value.get("used_fallback_core_district", False),
        },
    }]
