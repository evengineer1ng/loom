from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.decision.game_state_delta_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "⚔️",
    "deterministic": True,
    "inputs": ["runtime.decision_request.v1"],
    "outputs": ["runtime.decision_response.v1"],
    "requires": [],
    "provides": ["runtime.game_state_delta_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "decision", "game", "state", "delta"],
    "description": "Package detected CP2077 state deltas such as combat shifts, health thresholds, wanted changes, quest updates, and vehicle transitions.",
}


def build_game_state_delta_packet(
    previous_state: dict[str, Any] | None,
    current_state: dict[str, Any] | None,
    detected_events: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "previous_state": dict(previous_state or {}),
        "current_state": dict(current_state or {}),
        "detected_events": [dict(item) for item in (detected_events or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_game_state_delta_packet(
        previous_state=dict(payload.get("previous_state") or {}),
        current_state=dict(payload.get("current_state") or {}),
        detected_events=list(payload.get("detected_events") or []),
    )
    output_packet = {
        "packet_type": "runtime.decision_response.v1",
        "packet_version": "runtime.decision_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "game-state-delta-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built game-state delta packet.",
        "refs": [],
        "data": {
            "detected_event_count": len(value.get("detected_events", [])),
        },
    }]
