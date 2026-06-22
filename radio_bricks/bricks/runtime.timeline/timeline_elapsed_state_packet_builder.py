from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.timeline.timeline_elapsed_state_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "⏳",
    "deterministic": True,
    "inputs": ["runtime.timeline_request.v1"],
    "outputs": ["runtime.timeline_response.v1"],
    "requires": [],
    "provides": ["runtime.timeline_elapsed_state_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "timeline", "elapsed", "state", "pause"],
    "description": "Package timeline elapsed-state math with running, paused, started time, pause accumulation, and fired item ids.",
}


def build_timeline_elapsed_state_packet(
    running: bool,
    paused: bool,
    started_ts: float,
    pause_started_ts: float,
    pause_accum_sec: float,
    elapsed_sec: float,
    fired_ids: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "running": bool(running),
        "paused": bool(paused),
        "started_ts": float(started_ts),
        "pause_started_ts": float(pause_started_ts),
        "pause_accum_sec": float(pause_accum_sec),
        "elapsed_sec": float(elapsed_sec),
        "fired_ids": dict(fired_ids or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_timeline_elapsed_state_packet(
        running=bool(payload.get("running")),
        paused=bool(payload.get("paused")),
        started_ts=float(payload.get("started_ts") or 0.0),
        pause_started_ts=float(payload.get("pause_started_ts") or 0.0),
        pause_accum_sec=float(payload.get("pause_accum_sec") or 0.0),
        elapsed_sec=float(payload.get("elapsed_sec") or 0.0),
        fired_ids=dict(payload.get("fired_ids") or {}),
    )
    output_packet = {
        "packet_type": "runtime.timeline_response.v1",
        "packet_version": "runtime.timeline_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "timeline-elapsed-state-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built timeline-elapsed state packet.",
        "refs": [],
        "data": {
            "running": value.get("running", False),
            "paused": value.get("paused", False),
            "elapsed_sec": value.get("elapsed_sec", 0.0),
        },
    }]
