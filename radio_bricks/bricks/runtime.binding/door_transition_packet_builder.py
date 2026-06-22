from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.door_transition_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🚪",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.door_transition_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "door", "bookmark", "loom", "transition"],
    "description": "Package a loom boot-door transition pair with bookmark target, edge key, and Club storage paths.",
}


def build_door_transition_packet(
    loom_id: str,
    bookmark_id: str,
    entry: str,
    exit_path: str,
    edge_key: str,
) -> dict[str, Any]:
    return {
        "loom_id": str(loom_id),
        "bookmark_id": str(bookmark_id),
        "entry": str(entry),
        "exit": str(exit_path),
        "edge_key": str(edge_key),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_door_transition_packet(
        loom_id=str(payload.get("loom_id") or ""),
        bookmark_id=str(payload.get("bookmark_id") or payload.get("bookmark") or ""),
        entry=str(payload.get("entry") or ""),
        exit_path=str(payload.get("exit") or ""),
        edge_key=str(payload.get("edge_key") or ""),
    )
    output_packet = {
        "packet_type": "runtime.binding_response.v1",
        "packet_version": "runtime.binding_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "door-transition-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built door transition packet.",
        "refs": [],
        "data": {
            "loom_id": value.get("loom_id", ""),
            "bookmark_id": value.get("bookmark_id", ""),
        },
    }]
