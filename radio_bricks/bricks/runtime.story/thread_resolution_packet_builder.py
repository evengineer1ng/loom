from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.story.thread_resolution_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎭",
    "deterministic": True,
    "inputs": ["runtime.story_request.v1"],
    "outputs": ["runtime.story_response.v1"],
    "requires": [],
    "provides": ["runtime.thread_resolution_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "story", "thread", "resolution", "myth"],
    "description": "Package thread resolution outcomes, mythology promotion, participant ledger touches, and the event that closes the open question.",
}


def build_thread_resolution_packet(
    tick: int,
    thread_id: str,
    outcome: str,
    final_status: str,
    heat: float,
    participant_ids: list[str] | None,
    emitted_event: dict[str, Any] | None,
    memory_record: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "tick": int(tick),
        "thread_id": str(thread_id),
        "outcome": str(outcome),
        "final_status": str(final_status),
        "heat": float(heat),
        "participant_ids": [str(item) for item in (participant_ids or [])],
        "emitted_event": dict(emitted_event or {}),
        "memory_record": dict(memory_record or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_thread_resolution_packet(
        tick=int(payload.get("tick") or 0),
        thread_id=str(payload.get("thread_id") or ""),
        outcome=str(payload.get("outcome") or ""),
        final_status=str(payload.get("final_status") or ""),
        heat=float(payload.get("heat") or 0.0),
        participant_ids=list(payload.get("participant_ids") or []),
        emitted_event=dict(payload.get("emitted_event") or {}),
        memory_record=dict(payload.get("memory_record") or {}),
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
        "receipt_id": "thread-resolution-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built thread-resolution packet.",
        "refs": [],
        "data": {
            "thread_id": value.get("thread_id", ""),
            "outcome": value.get("outcome", ""),
            "mythologized": value.get("final_status", "") == "mythologized",
        },
    }]
