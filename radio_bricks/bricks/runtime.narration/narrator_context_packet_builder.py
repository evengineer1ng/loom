from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.narration.narrator_context_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.narration_request.v1"],
    "outputs": ["runtime.narration_response.v1"],
    "requires": [],
    "provides": ["runtime.narrator_context_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "narration", "context", "show-bible"],
    "description": "Package persistent narrator context including motifs, open loops, streaks, and claim tags.",
}


def build_narrator_context_packet(context: dict[str, Any] | None) -> dict[str, Any]:
    source = dict(context or {})
    return {
        "last_commentary_time": source.get("last_commentary_time", 0),
        "last_topics_discussed": list(source.get("last_topics_discussed", [])),
        "active_themes": list(source.get("active_themes", [])),
        "player_streak_data": dict(source.get("player_streak_data", {})),
        "segment_history": dict(source.get("segment_history", {})),
        "player_team": str(source.get("player_team", "")),
        "save_timestamp": source.get("save_timestamp", 0),
        "current_motif": str(source.get("current_motif", "quiet climb")),
        "open_loop": str(source.get("open_loop", "")),
        "named_focus": str(source.get("named_focus", "")),
        "stakes_axis": str(source.get("stakes_axis", "budget")),
        "tone": str(source.get("tone", "wry")),
        "last_generated_spine": str(source.get("last_generated_spine", "")),
        "last_generated_beat": str(source.get("last_generated_beat", "")),
        "claim_tags": list(source.get("claim_tags", [])),
        "segments_since_motif_change": int(source.get("segments_since_motif_change", 0)),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_narrator_context_packet(dict(payload.get("context") or {}))
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
        "receipt_id": "narrator-context-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built narrator context packet.",
        "refs": [],
        "data": {"player_team": value.get("player_team", ""), "theme_count": len(value.get("active_themes", []))},
    }]
