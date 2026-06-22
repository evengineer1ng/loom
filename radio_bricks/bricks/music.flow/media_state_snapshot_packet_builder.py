from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "music.flow.media_state_snapshot_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎵",
    "deterministic": True,
    "inputs": ["music.flow_request.v1"],
    "outputs": ["music.flow_response.v1"],
    "requires": [],
    "provides": ["music.media_state_snapshot_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["music", "flow", "media", "state", "snapshot"],
    "description": "Package now-playing media state with backend identity, playback flags, metadata, timeline fields, and track signature.",
}


def build_media_state_snapshot_packet(
    backend: str,
    ok: bool,
    playing: bool,
    title: str,
    artist: str,
    album: str,
    source_app: str,
    track_sig: str,
    position_sec: float | None,
    duration_sec: float | None,
    remaining_sec: float | None,
) -> dict[str, Any]:
    return {
        "backend": str(backend),
        "ok": bool(ok),
        "playing": bool(playing),
        "title": str(title),
        "artist": str(artist),
        "album": str(album),
        "source_app": str(source_app),
        "track_sig": str(track_sig),
        "position_sec": None if position_sec is None else float(position_sec),
        "duration_sec": None if duration_sec is None else float(duration_sec),
        "remaining_sec": None if remaining_sec is None else float(remaining_sec),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_media_state_snapshot_packet(
        backend=str(payload.get("backend") or ""),
        ok=bool(payload.get("ok")),
        playing=bool(payload.get("playing")),
        title=str(payload.get("title") or ""),
        artist=str(payload.get("artist") or ""),
        album=str(payload.get("album") or ""),
        source_app=str(payload.get("source_app") or ""),
        track_sig=str(payload.get("track_sig") or ""),
        position_sec=payload.get("position_sec"),
        duration_sec=payload.get("duration_sec"),
        remaining_sec=payload.get("remaining_sec"),
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
        "receipt_id": "media-state-snapshot-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built media-state snapshot packet.",
        "refs": [],
        "data": {
            "backend": value.get("backend", ""),
            "playing": value.get("playing", False),
            "track_sig": value.get("track_sig", ""),
        },
    }]
