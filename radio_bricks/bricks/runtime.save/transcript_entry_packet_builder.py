from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.save.transcript_entry_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📝",
    "deterministic": True,
    "inputs": ["runtime.save_request.v1"],
    "outputs": ["runtime.save_response.v1"],
    "requires": [],
    "provides": ["runtime.transcript_entry_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "save", "transcript", "speech", "entry"],
    "description": "Package a transcript entry with timestamp, display speaker, normalized text, and rolling-history placement.",
}


def build_transcript_entry_packet(
    timestamp: float,
    time_str: str,
    speaker: str,
    text: str,
    history_size: int,
) -> dict[str, Any]:
    return {
        "timestamp": float(timestamp),
        "time_str": str(time_str),
        "speaker": str(speaker),
        "text": str(text),
        "history_size": int(history_size),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_transcript_entry_packet(
        timestamp=float(payload.get("timestamp") or 0.0),
        time_str=str(payload.get("time_str") or ""),
        speaker=str(payload.get("speaker") or ""),
        text=str(payload.get("text") or ""),
        history_size=int(payload.get("history_size") or 0),
    )
    output_packet = {
        "packet_type": "runtime.save_response.v1",
        "packet_version": "runtime.save_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "transcript-entry-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built transcript entry packet.",
        "refs": [],
        "data": {
            "speaker": value.get("speaker", ""),
            "time_str": value.get("time_str", ""),
            "history_size": value.get("history_size", 0),
        },
    }]
