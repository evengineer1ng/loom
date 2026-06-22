from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.narration.visual_reaction_throttle_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "⏱️",
    "deterministic": True,
    "inputs": ["runtime.narration_request.v1"],
    "outputs": ["runtime.narration_response.v1"],
    "requires": [],
    "provides": ["runtime.visual_reaction_throttle_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "narration", "visual", "reaction", "throttle"],
    "description": "Package visual live-commentary throttling with reaction frequency, last reaction time, pending summaries, and next eligible speak window.",
}


def build_visual_reaction_throttle_packet(
    talk_over_video: bool,
    reaction_frequency: float,
    last_reaction_time: float,
    next_reaction_time: float,
    pending_reaction_count: int,
    emitted_live_commentary: bool,
) -> dict[str, Any]:
    return {
        "talk_over_video": bool(talk_over_video),
        "reaction_frequency": float(reaction_frequency),
        "last_reaction_time": float(last_reaction_time),
        "next_reaction_time": float(next_reaction_time),
        "pending_reaction_count": int(pending_reaction_count),
        "emitted_live_commentary": bool(emitted_live_commentary),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_visual_reaction_throttle_packet(
        talk_over_video=bool(payload.get("talk_over_video")),
        reaction_frequency=float(payload.get("reaction_frequency") or 0.0),
        last_reaction_time=float(payload.get("last_reaction_time") or 0.0),
        next_reaction_time=float(payload.get("next_reaction_time") or 0.0),
        pending_reaction_count=int(payload.get("pending_reaction_count") or 0),
        emitted_live_commentary=bool(payload.get("emitted_live_commentary")),
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
        "receipt_id": "visual-reaction-throttle-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built visual-reaction throttle packet.",
        "refs": [],
        "data": {
            "talk_over_video": value.get("talk_over_video", False),
            "pending_reaction_count": value.get("pending_reaction_count", 0),
            "emitted_live_commentary": value.get("emitted_live_commentary", False),
        },
    }]
