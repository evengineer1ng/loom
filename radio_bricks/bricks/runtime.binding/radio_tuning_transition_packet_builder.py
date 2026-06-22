from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.radio_tuning_transition_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📻",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.radio_tuning_transition_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "radio", "tuning", "transition"],
    "description": "Package radio-dial tuning transitions with scanned station, current station, delay before switch, and issued tune command.",
}


def build_radio_tuning_transition_packet(
    current_station: str,
    target_station: str,
    delay_ms: int,
    static_playing: bool,
    command_sent: str,
) -> dict[str, Any]:
    return {
        "current_station": str(current_station),
        "target_station": str(target_station),
        "delay_ms": int(delay_ms),
        "static_playing": bool(static_playing),
        "command_sent": str(command_sent),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_radio_tuning_transition_packet(
        current_station=str(payload.get("current_station") or ""),
        target_station=str(payload.get("target_station") or ""),
        delay_ms=int(payload.get("delay_ms") or 0),
        static_playing=bool(payload.get("static_playing")),
        command_sent=str(payload.get("command_sent") or ""),
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
        "receipt_id": "radio-tuning-transition-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built radio-tuning transition packet.",
        "refs": [],
        "data": {
            "current_station": value.get("current_station", ""),
            "target_station": value.get("target_station", ""),
            "delay_ms": value.get("delay_ms", 0),
        },
    }]
