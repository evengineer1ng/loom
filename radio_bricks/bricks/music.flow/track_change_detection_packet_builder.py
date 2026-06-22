from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "music.flow.track_change_detection_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪄",
    "deterministic": True,
    "inputs": ["music.flow_request.v1"],
    "outputs": ["music.flow_response.v1"],
    "requires": [],
    "provides": ["music.track_change_detection_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["music", "flow", "track", "change", "timeline"],
    "description": "Package track-change detection using signature drift, position resets, backward jumps, and refresh escalation decisions.",
}


def build_track_change_detection_packet(
    prior_track_sig: str,
    current_track_sig: str,
    prior_position_sec: float | None,
    current_position_sec: float | None,
    track_changed: bool,
    change_reasons: list[str] | None,
    refresh_mode: str,
) -> dict[str, Any]:
    return {
        "prior_track_sig": str(prior_track_sig),
        "current_track_sig": str(current_track_sig),
        "prior_position_sec": None if prior_position_sec is None else float(prior_position_sec),
        "current_position_sec": None if current_position_sec is None else float(current_position_sec),
        "track_changed": bool(track_changed),
        "change_reasons": [str(item) for item in (change_reasons or [])],
        "refresh_mode": str(refresh_mode),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_track_change_detection_packet(
        prior_track_sig=str(payload.get("prior_track_sig") or ""),
        current_track_sig=str(payload.get("current_track_sig") or ""),
        prior_position_sec=payload.get("prior_position_sec"),
        current_position_sec=payload.get("current_position_sec"),
        track_changed=bool(payload.get("track_changed")),
        change_reasons=list(payload.get("change_reasons") or []),
        refresh_mode=str(payload.get("refresh_mode") or ""),
    )
    output_packet = {
        "packet_type": "music.flow_response.v1",
        "packet_version": "music.flow_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "track-change-detection-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built track-change detection packet.",
        "refs": [],
        "data": {
            "track_changed": value.get("track_changed", False),
            "reason_count": len(value.get("change_reasons", [])),
            "refresh_mode": value.get("refresh_mode", ""),
        },
    }]
