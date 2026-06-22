from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.meta_tick_driver_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "⏱️",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.meta_tick_driver_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "meta", "tick", "driver"],
    "description": "Package meta-plugin tick-driver state with tick cadence, startup delay, session-start gate, emitted segment count, and controller presence.",
}


def build_meta_tick_driver_packet(
    tick_sec: float,
    startup_delay: float,
    session_started: bool,
    controller_found: bool,
    meta_plugin_found: bool,
    emitted_segments: int,
) -> dict[str, Any]:
    return {
        "tick_sec": float(tick_sec),
        "startup_delay": float(startup_delay),
        "session_started": bool(session_started),
        "controller_found": bool(controller_found),
        "meta_plugin_found": bool(meta_plugin_found),
        "emitted_segments": int(emitted_segments),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_meta_tick_driver_packet(
        tick_sec=float(payload.get("tick_sec") or 0.0),
        startup_delay=float(payload.get("startup_delay") or 0.0),
        session_started=bool(payload.get("session_started")),
        controller_found=bool(payload.get("controller_found")),
        meta_plugin_found=bool(payload.get("meta_plugin_found")),
        emitted_segments=int(payload.get("emitted_segments") or 0),
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
        "receipt_id": "meta-tick-driver-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built meta tick-driver packet.",
        "refs": [],
        "data": {
            "tick_sec": value.get("tick_sec", 0.0),
            "session_started": value.get("session_started", False),
            "emitted_segments": value.get("emitted_segments", 0),
        },
    }]
