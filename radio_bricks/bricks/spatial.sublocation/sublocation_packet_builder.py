from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "spatial.sublocation.sublocation_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📍",
    "deterministic": True,
    "inputs": ["spatial.sublocation_request.v1"],
    "outputs": ["spatial.sublocation_response.v1"],
    "requires": [],
    "provides": ["spatial.sublocation_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["spatial", "sublocation", "puck", "layout", "node"],
    "description": "Package a single puck-addressable Neikos sublocation with rendered description and dynamic encounter, fragment, trainer, echo, and lock flags.",
}


def build_sublocation_packet(
    sublocation_id: str,
    boulder_code: str,
    mountain: str,
    label: str,
    description: str,
    page: int,
    slot: int,
    node_id: str,
    has_encounter: bool,
    has_fragment_hint: bool,
    has_trainer: bool,
    has_echo: bool,
    is_locked: bool,
) -> dict[str, Any]:
    return {
        "sublocation_id": sublocation_id,
        "boulder_code": boulder_code,
        "mountain": mountain,
        "label": label,
        "description": description,
        "page": int(page),
        "slot": int(slot),
        "node_id": node_id,
        "has_encounter": bool(has_encounter),
        "has_fragment_hint": bool(has_fragment_hint),
        "has_trainer": bool(has_trainer),
        "has_echo": bool(has_echo),
        "is_locked": bool(is_locked),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_sublocation_packet(
        sublocation_id=str(payload.get("sublocation_id") or ""),
        boulder_code=str(payload.get("boulder_code") or ""),
        mountain=str(payload.get("mountain") or ""),
        label=str(payload.get("label") or ""),
        description=str(payload.get("description") or ""),
        page=int(payload.get("page") or 0),
        slot=int(payload.get("slot") or 0),
        node_id=str(payload.get("node_id") or ""),
        has_encounter=bool(payload.get("has_encounter")),
        has_fragment_hint=bool(payload.get("has_fragment_hint")),
        has_trainer=bool(payload.get("has_trainer")),
        has_echo=bool(payload.get("has_echo")),
        is_locked=bool(payload.get("is_locked")),
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
        "receipt_id": "sublocation-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built sublocation packet.",
        "refs": [],
        "data": {"sublocation_id": value.get("sublocation_id", ""), "slot": value.get("slot", 0)},
    }]
