from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "spatial.sublocation.fragment_hint_surface_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪧",
    "deterministic": True,
    "inputs": ["spatial.sublocation_request.v1"],
    "outputs": ["spatial.sublocation_response.v1"],
    "requires": [],
    "provides": ["spatial.fragment_hint_surface_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["spatial", "sublocation", "fragment", "hint", "surface"],
    "description": "Package the boulder-code surfaces that act as fragment hint points inside the sublocation model.",
}


def build_fragment_hint_surface_packet(
    fragment_hint_codes: list[str] | None,
    matching_boulder_code: str,
    has_fragment_hint: bool,
) -> dict[str, Any]:
    return {
        "fragment_hint_codes": list(fragment_hint_codes or []),
        "matching_boulder_code": matching_boulder_code,
        "has_fragment_hint": bool(has_fragment_hint),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    matching_boulder_code = str(payload.get("matching_boulder_code") or "")
    fragment_hint_codes = list(payload.get("fragment_hint_codes") or [])
    value = build_fragment_hint_surface_packet(
        fragment_hint_codes=fragment_hint_codes,
        matching_boulder_code=matching_boulder_code,
        has_fragment_hint=matching_boulder_code in fragment_hint_codes,
    )
    output_packet = {
        "packet_type": "spatial.sublocation_response.v1",
        "packet_version": "spatial.sublocation_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "fragment-hint-surface-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built fragment-hint surface packet.",
        "refs": [],
        "data": {"matching_boulder_code": value.get("matching_boulder_code", ""), "has_fragment_hint": value.get("has_fragment_hint", False)},
    }]
