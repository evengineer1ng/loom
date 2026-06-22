from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.signals.dany_ignition_lifecycle_evaluator",
    "kind": "classifier",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.series_request.v1"],
    "outputs": ["math.series_response.v1"],
    "requires": [],
    "provides": ["math.dany_ignition_lifecycle"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "signals", "dany", "ignition", "lifecycle"],
    "description": "Evaluate Dany-style ignition harvest, runner, fade, and stale-thesis exits from duration, profit, and expansion persistence.",
}


def evaluate_dany_ignition_lifecycle(duration_minutes: float, current_profit: float, is_expanded: bool) -> dict[str, Any]:
    exit_label = None
    if float(current_profit) > 0.012 and float(duration_minutes) <= 5.0:
        exit_label = "ignition_scalp"
    elif float(current_profit) > 0.025 and float(duration_minutes) > 5.0:
        exit_label = "ignition_runner"
    elif float(duration_minutes) >= 20.0:
        exit_label = "ignition_time"
    elif float(duration_minutes) <= 4.0 and float(current_profit) < -0.005 and not bool(is_expanded):
        exit_label = "ignition_fade"
    elif float(duration_minutes) >= 8.0 and abs(float(current_profit)) < 0.003 and not bool(is_expanded):
        exit_label = "ignition_time"
    return {
        "exit_label": exit_label,
        "is_expanded": bool(is_expanded),
        "duration_minutes": float(duration_minutes),
        "current_profit": float(current_profit),
        "stale_thesis": float(duration_minutes) >= 20.0 or (float(duration_minutes) >= 8.0 and abs(float(current_profit)) < 0.003 and not bool(is_expanded)),
        "burst_paid": float(current_profit) > 0.012,
        "runner_paid": float(current_profit) > 0.025,
        "early_fade": float(duration_minutes) <= 4.0 and float(current_profit) < -0.005 and not bool(is_expanded),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = evaluate_dany_ignition_lifecycle(
        duration_minutes=float(payload.get("duration_minutes") or 0.0),
        current_profit=float(payload.get("current_profit") or 0.0),
        is_expanded=bool(payload.get("is_expanded", False)),
    )
    output_packet = {
        "packet_type": "math.series_response.v1",
        "packet_version": "math.series_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "dany-ignition-lifecycle",
        "brick_id": CONCEPT["id"],
        "kind": "classification",
        "label": "Evaluated Dany ignition lifecycle.",
        "refs": [],
        "data": {"exit_label": value.get("exit_label"), "stale_thesis": value.get("stale_thesis", False)},
    }]
