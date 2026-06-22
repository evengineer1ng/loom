from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.story.thread_temperature_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🌡️",
    "deterministic": True,
    "inputs": ["runtime.story_request.v1"],
    "outputs": ["runtime.story_response.v1"],
    "requires": [],
    "provides": ["runtime.thread_temperature_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "story", "thread", "heat", "urgency"],
    "description": "Package per-tick thread heat and urgency evolution under macro pressure, natural decay, and resolution-horizon progress.",
}


def build_thread_temperature_packet(
    tick: int,
    thread_id: str,
    domain: str,
    axis_id: str,
    prior_heat: float,
    current_heat: float,
    urgency: float,
    progress_ratio: float,
    status_transition: str,
) -> dict[str, Any]:
    return {
        "tick": int(tick),
        "thread_id": str(thread_id),
        "domain": str(domain),
        "axis_id": str(axis_id),
        "prior_heat": float(prior_heat),
        "current_heat": float(current_heat),
        "urgency": float(urgency),
        "progress_ratio": float(progress_ratio),
        "status_transition": str(status_transition),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_thread_temperature_packet(
        tick=int(payload.get("tick") or 0),
        thread_id=str(payload.get("thread_id") or ""),
        domain=str(payload.get("domain") or ""),
        axis_id=str(payload.get("axis_id") or ""),
        prior_heat=float(payload.get("prior_heat") or 0.0),
        current_heat=float(payload.get("current_heat") or 0.0),
        urgency=float(payload.get("urgency") or 0.0),
        progress_ratio=float(payload.get("progress_ratio") or 0.0),
        status_transition=str(payload.get("status_transition") or ""),
    )
    output_packet = {
        "packet_type": "runtime.story_response.v1",
        "packet_version": "runtime.story_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "thread-temperature-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built thread-temperature packet.",
        "refs": [],
        "data": {
            "thread_id": value.get("thread_id", ""),
            "current_heat": value.get("current_heat", 0.0),
            "status_transition": value.get("status_transition", ""),
        },
    }]
