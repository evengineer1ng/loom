from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.loom.forkuniverse_organization_realization_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🏛️",
    "deterministic": True,
    "inputs": ["assembly.loom_request.v1"],
    "outputs": ["assembly.loom_response.v1"],
    "requires": [],
    "provides": ["assembly.forkuniverse_organization_realization_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "loom", "forkuniverse", "organization", "template"],
    "description": "Package the realized organization rows mapped onto generated districts with default power, wealth, policy, and tension surfaces.",
}


def build_forkuniverse_organization_realization_packet(
    organization_target: int,
    organization_templates: list[dict[str, Any]] | None,
    location_rows: list[dict[str, Any]] | None,
    organization_rows: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "organization_target": int(organization_target),
        "organization_templates": [dict(item) for item in (organization_templates or [])],
        "location_rows": [dict(item) for item in (location_rows or [])],
        "organization_rows": [dict(item) for item in (organization_rows or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_forkuniverse_organization_realization_packet(
        organization_target=int(payload.get("organization_target") or 0),
        organization_templates=list(payload.get("organization_templates") or []),
        location_rows=list(payload.get("location_rows") or []),
        organization_rows=list(payload.get("organization_rows") or []),
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
        "receipt_id": "forkuniverse-organization-realization-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built ForkUniverse organization-realization packet.",
        "refs": [],
        "data": {
            "organization_target": value.get("organization_target", 0),
            "location_count": len(value.get("location_rows", [])),
            "row_count": len(value.get("organization_rows", [])),
        },
    }]
