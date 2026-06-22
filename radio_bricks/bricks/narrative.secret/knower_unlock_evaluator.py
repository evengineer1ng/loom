from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "narrative.secret.knower_unlock_evaluator",
    "kind": "evaluator",
    "version": "0.1.0",
    "emoji": "🕯️",
    "deterministic": True,
    "inputs": ["narrative.secret_request.v1"],
    "outputs": ["narrative.secret_response.v1"],
    "requires": [],
    "provides": ["narrative.knower_unlock_decision"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["narrative", "secret", "knower", "unlock", "trajectory"],
    "description": "Evaluate Hidden Knower availability from trajectory values against required unlock thresholds.",
}


def evaluate_knower_unlock(
    unlock_thresholds: dict[str, float] | None,
    trajectory: dict[str, float] | None,
) -> dict[str, Any]:
    thresholds = {str(key): float(value) for key, value in (unlock_thresholds or {}).items()}
    trajectory_map = {str(key): float(value) for key, value in (trajectory or {}).items()}
    missing = [
        {"key": key, "required": value, "actual": trajectory_map.get(key, 0.0)}
        for key, value in thresholds.items()
        if trajectory_map.get(key, 0.0) < value
    ]
    return {
        "unlock_thresholds": thresholds,
        "trajectory": trajectory_map,
        "missing_requirements": missing,
        "is_unlocked": not missing,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = evaluate_knower_unlock(
        unlock_thresholds=dict(payload.get("unlock_thresholds") or {}),
        trajectory=dict(payload.get("trajectory") or {}),
    )
    output_packet = {
        "packet_type": "narrative.secret_response.v1",
        "packet_version": "narrative.secret_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "knower-unlock-decision",
        "brick_id": CONCEPT["id"],
        "kind": "evaluate",
        "label": "Evaluated Hidden Knower unlock decision.",
        "refs": [],
        "data": {"is_unlocked": value.get("is_unlocked", False), "missing_count": len(value.get("missing_requirements", []))},
    }]
