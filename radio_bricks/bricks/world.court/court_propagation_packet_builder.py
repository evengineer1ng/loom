from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.court.court_propagation_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["world.court_request.v1"],
    "outputs": ["world.court_response.v1"],
    "requires": [],
    "provides": ["world.court_propagation_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "court", "propagation", "decree"],
    "description": "Package the court-to-world decree propagation seam, including silence handling and multiplied policy vectors.",
}


def build_court_propagation_packet(
    is_silence: bool,
    speech_option_id: str,
    policy_vector: dict[str, float] | None,
    location_multipliers: dict[str, float] | None,
) -> dict[str, Any]:
    base = dict(policy_vector or {})
    multipliers = dict(location_multipliers or {})
    modified = {axis: float(value) * float(multipliers.get(axis, 1.0)) for axis, value in base.items()}
    return {
        "is_silence": bool(is_silence),
        "speech_option_id": speech_option_id,
        "base_policy_vector": base,
        "modified_policy_vector": modified,
        "sacred_silence_increment": 2.0 if is_silence else 0.0,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_court_propagation_packet(
        is_silence=bool(payload.get("is_silence", False)),
        speech_option_id=str(payload.get("speech_option_id") or ""),
        policy_vector=dict(payload.get("policy_vector") or {}),
        location_multipliers=dict(payload.get("location_multipliers") or {}),
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
        "receipt_id": "court-propagation-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built court propagation packet.",
        "refs": [],
        "data": {"is_silence": value.get("is_silence", False)},
    }]
