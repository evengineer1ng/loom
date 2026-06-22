from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.oradio_open_request_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🚪",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.oradio_open_request_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "open", "club", "gate", "consent"],
    "description": "Package the front-door open request for an oradio, including gate mode and sensitive-consent intent.",
}


def build_oradio_open_request_packet(
    spec_ref: str,
    gate: bool,
    allow_sensitive: bool,
    club_present: bool,
) -> dict[str, Any]:
    return {
        "spec_ref": str(spec_ref),
        "gate": bool(gate),
        "allow_sensitive": bool(allow_sensitive),
        "club_present": bool(club_present),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_oradio_open_request_packet(
        spec_ref=str(payload.get("spec_ref") or ""),
        gate=bool(payload.get("gate", True)),
        allow_sensitive=bool(payload.get("allow_sensitive", False)),
        club_present=bool(payload.get("club_present", False)),
    )
    output_packet = {
        "packet_type": "runtime.binding_response.v1",
        "packet_version": "runtime.binding_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "oradio-open-request-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built oradio open request packet.",
        "refs": [],
        "data": {
            "spec_ref": value.get("spec_ref", ""),
            "gate": value.get("gate", False),
            "allow_sensitive": value.get("allow_sensitive", False),
        },
    }]
