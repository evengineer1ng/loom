from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.story.commentary_line_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎤",
    "deterministic": True,
    "inputs": ["runtime.story_request.v1"],
    "outputs": ["runtime.story_response.v1"],
    "requires": [],
    "provides": ["runtime.commentary_line_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "story", "commentary", "broadcast", "line"],
    "description": "Package a broadcast commentary line with speaker role, timing bucket, text, and dispatch priority.",
}


def build_commentary_line_packet(
    speaker: str,
    text: str,
    timing: str,
    priority: int,
) -> dict[str, Any]:
    return {
        "speaker": str(speaker),
        "text": str(text),
        "timing": str(timing),
        "priority": int(priority),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_commentary_line_packet(
        speaker=str(payload.get("speaker") or ""),
        text=str(payload.get("text") or ""),
        timing=str(payload.get("timing") or ""),
        priority=int(payload.get("priority") or 0),
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
        "receipt_id": "commentary-line-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built commentary-line packet.",
        "refs": [],
        "data": {
            "speaker": value.get("speaker", ""),
            "timing": value.get("timing", ""),
            "priority": value.get("priority", 0),
        },
    }]
