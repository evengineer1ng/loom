from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.narration.commentary_prompt_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🗒️",
    "deterministic": True,
    "inputs": ["runtime.narration_request.v1"],
    "outputs": ["runtime.narration_response.v1"],
    "requires": [],
    "provides": ["runtime.commentary_prompt_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "narration", "commentary", "prompt", "llm"],
    "description": "Package a commentary prompt for generation with speaker role, event type, token budget, prompt text, and priority.",
}


def build_commentary_prompt_packet(
    speaker: str,
    prompt: str,
    event_type: str,
    max_tokens: int,
    priority: int,
) -> dict[str, Any]:
    return {
        "speaker": str(speaker),
        "prompt": str(prompt),
        "event_type": str(event_type),
        "max_tokens": int(max_tokens),
        "priority": int(priority),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_commentary_prompt_packet(
        speaker=str(payload.get("speaker") or ""),
        prompt=str(payload.get("prompt") or ""),
        event_type=str(payload.get("event_type") or ""),
        max_tokens=int(payload.get("max_tokens") or 0),
        priority=int(payload.get("priority") or 0),
    )
    output_packet = {
        "packet_type": "runtime.narration_response.v1",
        "packet_version": "runtime.narration_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "commentary-prompt-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built commentary-prompt packet.",
        "refs": [],
        "data": {
            "speaker": value.get("speaker", ""),
            "event_type": value.get("event_type", ""),
            "max_tokens": value.get("max_tokens", 0),
        },
    }]
