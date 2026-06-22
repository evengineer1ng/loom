from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.narration.social_reaction_prompt_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "💬",
    "deterministic": True,
    "inputs": ["runtime.narration_request.v1"],
    "outputs": ["runtime.narration_response.v1"],
    "requires": [],
    "provides": ["runtime.social_reaction_prompt_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "narration", "social", "reaction", "prompt"],
    "description": "Package a reusable social reaction prompt with angle, why-now framing, key points, and host hint across feed adapters.",
}


def build_social_reaction_prompt_packet(
    source: str,
    angle: str,
    why: str,
    key_points: list[str] | None,
    host_hint: str,
) -> dict[str, Any]:
    return {
        "source": str(source),
        "angle": str(angle),
        "why": str(why),
        "key_points": [str(item) for item in (key_points or [])],
        "host_hint": str(host_hint),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_social_reaction_prompt_packet(
        source=str(payload.get("source") or ""),
        angle=str(payload.get("angle") or ""),
        why=str(payload.get("why") or ""),
        key_points=list(payload.get("key_points") or []),
        host_hint=str(payload.get("host_hint") or ""),
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
        "receipt_id": "social-reaction-prompt-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built social reaction prompt packet.",
        "refs": [],
        "data": {
            "source": value.get("source", ""),
            "key_point_count": len(value.get("key_points", [])),
        },
    }]
