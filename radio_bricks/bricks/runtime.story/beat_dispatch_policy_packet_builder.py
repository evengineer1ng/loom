from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.story.beat_dispatch_policy_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🥁",
    "deterministic": True,
    "inputs": ["runtime.story_request.v1"],
    "outputs": ["runtime.story_response.v1"],
    "requires": [],
    "provides": ["runtime.beat_dispatch_policy_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "story", "beat", "dispatch", "silence"],
    "description": "Package beat-dispatch policy with min gaps, silence windows, late-race overrides, color-roll odds, and narration threshold.",
}


def build_beat_dispatch_policy_packet(
    min_gap_sec: float,
    silence_min: float,
    silence_max: float,
    max_beats_per_lap: int,
    late_race_lap_threshold: int,
    late_race_min_gap: float,
    late_race_max_beats: int,
    color_probability: float,
    late_race_color_probability: float,
    narration_threshold: float,
    final_lap_always: bool,
) -> dict[str, Any]:
    return {
        "min_gap_sec": float(min_gap_sec),
        "silence_min": float(silence_min),
        "silence_max": float(silence_max),
        "max_beats_per_lap": int(max_beats_per_lap),
        "late_race_lap_threshold": int(late_race_lap_threshold),
        "late_race_min_gap": float(late_race_min_gap),
        "late_race_max_beats": int(late_race_max_beats),
        "color_probability": float(color_probability),
        "late_race_color_probability": float(late_race_color_probability),
        "narration_threshold": float(narration_threshold),
        "final_lap_always": bool(final_lap_always),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_beat_dispatch_policy_packet(
        min_gap_sec=float(payload.get("min_gap_sec") or 0.0),
        silence_min=float(payload.get("silence_min") or 0.0),
        silence_max=float(payload.get("silence_max") or 0.0),
        max_beats_per_lap=int(payload.get("max_beats_per_lap") or 0),
        late_race_lap_threshold=int(payload.get("late_race_lap_threshold") or 0),
        late_race_min_gap=float(payload.get("late_race_min_gap") or 0.0),
        late_race_max_beats=int(payload.get("late_race_max_beats") or 0),
        color_probability=float(payload.get("color_probability") or 0.0),
        late_race_color_probability=float(payload.get("late_race_color_probability") or 0.0),
        narration_threshold=float(payload.get("narration_threshold") or 0.0),
        final_lap_always=bool(payload.get("final_lap_always")),
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
        "receipt_id": "beat-dispatch-policy-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built beat-dispatch policy packet.",
        "refs": [],
        "data": {
            "max_beats_per_lap": value.get("max_beats_per_lap", 0),
            "late_race_lap_threshold": value.get("late_race_lap_threshold", 0),
            "narration_threshold": value.get("narration_threshold", 0.0),
        },
    }]
