from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.terminal.terminal_resolution_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🔥",
    "deterministic": True,
    "inputs": ["runtime.terminal_request.v1"],
    "outputs": ["runtime.terminal_response.v1"],
    "requires": [],
    "provides": ["runtime.terminal_resolution_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "terminal", "resolution", "transformation", "packet"],
    "description": "Package a terminal transformation record with outcome, snapshot, era transition, and layer resets.",
}


def build_terminal_resolution_packet(
    outcome: str,
    triggered_tick: int,
    collapse_duration_ticks: int,
    health_at_trigger: float,
    conditions_snapshot: dict[str, float] | None,
    description: str,
    new_era: str,
    layer_resets: dict[str, float] | None,
) -> dict[str, Any]:
    return {
        "outcome": outcome,
        "triggered_tick": int(triggered_tick),
        "collapse_duration_ticks": int(collapse_duration_ticks),
        "health_at_trigger": float(health_at_trigger),
        "conditions_snapshot": {str(key): float(value) for key, value in (conditions_snapshot or {}).items()},
        "description": description,
        "new_era": new_era,
        "layer_resets": {str(key): float(value) for key, value in (layer_resets or {}).items()},
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_terminal_resolution_packet(
        outcome=str(payload.get("outcome") or ""),
        triggered_tick=int(payload.get("triggered_tick") or 0),
        collapse_duration_ticks=int(payload.get("collapse_duration_ticks") or 0),
        health_at_trigger=float(payload.get("health_at_trigger") or 0.0),
        conditions_snapshot=dict(payload.get("conditions_snapshot") or {}),
        description=str(payload.get("description") or ""),
        new_era=str(payload.get("new_era") or ""),
        layer_resets=dict(payload.get("layer_resets") or {}),
    )
    output_packet = {
        "packet_type": "runtime.terminal_response.v1",
        "packet_version": "runtime.terminal_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "terminal-resolution-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built terminal-resolution packet.",
        "refs": [],
        "data": {"outcome": value.get("outcome", ""), "new_era": value.get("new_era", "")},
    }]
