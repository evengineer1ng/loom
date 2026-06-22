from __future__ import annotations

import hashlib
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "music.flow.track_signature_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["music.flow_request.v1"],
    "outputs": ["music.flow_response.v1"],
    "requires": [],
    "provides": ["music.track_signature"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["music", "flow", "track", "signature"],
    "description": "Build a stable track signature from title, artist, album, and source application.",
}


def build_track_signature(title: str, artist: str, album: str, source_app: str) -> dict[str, Any]:
    joined = "|".join([str(title or ""), str(artist or ""), str(album or ""), str(source_app or "")])
    return {"track_sig": hashlib.sha1(joined.encode("utf-8", errors="ignore")).hexdigest(), "composite": joined}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_track_signature(
        title=str(payload.get("title") or ""),
        artist=str(payload.get("artist") or ""),
        album=str(payload.get("album") or ""),
        source_app=str(payload.get("source_app") or ""),
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
        "receipt_id": "track-signature-builder",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built track signature.",
        "refs": [],
        "data": {"track_sig": str(value.get("track_sig", ""))[:12]},
    }]
