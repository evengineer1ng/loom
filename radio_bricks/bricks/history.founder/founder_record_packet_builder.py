from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "history.founder.founder_record_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧾",
    "deterministic": True,
    "inputs": ["history.founder_request.v1"],
    "outputs": ["history.founder_response.v1"],
    "requires": [],
    "provides": ["history.founder_record_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["history", "founder", "canon", "record", "project_hundred"],
    "description": "Package a canonical PROJECT HUNDRED founder record with name, role, thesis, and fate note.",
}


def build_founder_record_packet(founder_key: str, name: str, role: str, thesis: str, fate_note: str) -> dict[str, Any]:
    return {
        "founder_key": founder_key,
        "name": name,
        "role": role,
        "thesis": thesis,
        "fate_note": fate_note,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_founder_record_packet(
        founder_key=str(payload.get("founder_key") or ""),
        name=str(payload.get("name") or ""),
        role=str(payload.get("role") or ""),
        thesis=str(payload.get("thesis") or ""),
        fate_note=str(payload.get("fate_note") or ""),
    )
    output_packet = {
        "packet_type": "history.founder_response.v1",
        "packet_version": "history.founder_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "founder-record-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built founder record packet.",
        "refs": [],
        "data": {"founder_key": value.get("founder_key", ""), "name": value.get("name", "")},
    }]
