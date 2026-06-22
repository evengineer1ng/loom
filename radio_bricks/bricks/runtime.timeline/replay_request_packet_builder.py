from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.timeline.replay_request_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "⏪",
    "deterministic": True,
    "inputs": ["runtime.timeline_request.v1"],
    "outputs": ["runtime.timeline_response.v1"],
    "requires": [],
    "provides": ["runtime.replay_request_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "timeline", "replay", "request", "command"],
    "description": "Package a timeline replay request with target segment id and replay command channel.",
}


def build_replay_request_packet(
    command_name: str,
    seg_id: str,
) -> dict[str, Any]:
    return {
        "command_name": str(command_name),
        "seg_id": str(seg_id),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_replay_request_packet(
        command_name=str(payload.get("command_name") or ""),
        seg_id=str(payload.get("seg_id") or ""),
    )
    output_packet = {
        "packet_type": "runtime.timeline_response.v1",
        "packet_version": "runtime.timeline_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "replay-request-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built replay-request packet.",
        "refs": [],
        "data": {
            "command_name": value.get("command_name", ""),
            "seg_id": value.get("seg_id", ""),
        },
    }]
