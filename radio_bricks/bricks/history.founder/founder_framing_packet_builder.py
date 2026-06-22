from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "history.founder.founder_framing_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🏛️",
    "deterministic": True,
    "inputs": ["history.founder_request.v1"],
    "outputs": ["history.founder_response.v1"],
    "requires": [],
    "provides": ["history.founder_framing_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["history", "founder", "framing", "traitor", "martyr", "protector"],
    "description": "Package per-seed founder interpretation framing across traitor, martyr, and protector roles.",
}


def build_founder_framing_packet(traitor: str, martyr: str, protector: str) -> dict[str, Any]:
    return {"traitor": traitor, "martyr": martyr, "protector": protector}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_founder_framing_packet(
        traitor=str(payload.get("traitor") or ""),
        martyr=str(payload.get("martyr") or ""),
        protector=str(payload.get("protector") or ""),
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
        "receipt_id": "founder-framing-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built founder framing packet.",
        "refs": [],
        "data": value,
    }]
