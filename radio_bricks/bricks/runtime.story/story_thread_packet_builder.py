from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.story.story_thread_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪢",
    "deterministic": True,
    "inputs": ["runtime.story_request.v1"],
    "outputs": ["runtime.story_response.v1"],
    "requires": [],
    "provides": ["runtime.story_thread_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "story", "thread", "forkuniverse"],
    "description": "Package a first-class ForkUniverse story thread with heat, urgency, confidence, participants, and resolution state.",
}


def build_story_thread_packet(
    thread_id: str,
    title: str,
    domain: str,
    participant_ids: list[str] | None,
    status: str,
    confidence: float,
    urgency: float,
    heat: float,
    opened_tick: int,
    predicted_resolution_tick: int,
    resolved_tick: int | None,
    resolution_outcome: str | None,
    source_event_ids: list[str] | None,
) -> dict[str, Any]:
    packet = {
        "thread_id": thread_id,
        "title": title,
        "domain": domain,
        "participant_ids": list(participant_ids or []),
        "status": status,
        "confidence": float(confidence),
        "urgency": float(urgency),
        "heat": float(heat),
        "opened_tick": int(opened_tick),
        "predicted_resolution_tick": int(predicted_resolution_tick),
        "source_event_ids": list(source_event_ids or []),
    }
    if resolved_tick is not None:
        packet["resolved_tick"] = int(resolved_tick)
    if resolution_outcome is not None:
        packet["resolution_outcome"] = resolution_outcome
    return packet


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_story_thread_packet(
        thread_id=str(payload.get("thread_id") or ""),
        title=str(payload.get("title") or ""),
        domain=str(payload.get("domain") or ""),
        participant_ids=list(payload.get("participant_ids") or []),
        status=str(payload.get("status") or ""),
        confidence=float(payload.get("confidence") or 0.0),
        urgency=float(payload.get("urgency") or 0.0),
        heat=float(payload.get("heat") or 0.0),
        opened_tick=int(payload.get("opened_tick") or 0),
        predicted_resolution_tick=int(payload.get("predicted_resolution_tick") or 0),
        resolved_tick=payload.get("resolved_tick"),
        resolution_outcome=payload.get("resolution_outcome"),
        source_event_ids=list(payload.get("source_event_ids") or []),
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
        "receipt_id": "story-thread-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built story-thread packet.",
        "refs": [],
        "data": {"thread_id": value.get("thread_id", ""), "status": value.get("status", "")},
    }]
