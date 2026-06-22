from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.visual_activation_gate_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🔇",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.visual_activation_gate_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "visual", "activation", "interrupt"],
    "description": "Package visual-reader activation gating with host interruption, queue flush, manual session activation, and resume-on-deactivation behavior.",
}


def build_visual_activation_gate_packet(
    enabled: bool,
    active: bool,
    talk_over_video: bool,
    set_interrupt_flags: list[str] | None,
    cleared_interrupt_flags: list[str] | None,
    flushed_queues: list[str] | None,
    emitted_event_types: list[str] | None,
) -> dict[str, Any]:
    return {
        "enabled": bool(enabled),
        "active": bool(active),
        "talk_over_video": bool(talk_over_video),
        "set_interrupt_flags": [str(item) for item in (set_interrupt_flags or [])],
        "cleared_interrupt_flags": [str(item) for item in (cleared_interrupt_flags or [])],
        "flushed_queues": [str(item) for item in (flushed_queues or [])],
        "emitted_event_types": [str(item) for item in (emitted_event_types or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_visual_activation_gate_packet(
        enabled=bool(payload.get("enabled")),
        active=bool(payload.get("active")),
        talk_over_video=bool(payload.get("talk_over_video")),
        set_interrupt_flags=list(payload.get("set_interrupt_flags") or []),
        cleared_interrupt_flags=list(payload.get("cleared_interrupt_flags") or []),
        flushed_queues=list(payload.get("flushed_queues") or []),
        emitted_event_types=list(payload.get("emitted_event_types") or []),
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
        "receipt_id": "visual-activation-gate-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built visual-activation gate packet.",
        "refs": [],
        "data": {
            "active": value.get("active", False),
            "talk_over_video": value.get("talk_over_video", False),
            "event_count": len(value.get("emitted_event_types", [])),
        },
    }]
