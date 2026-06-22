from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "narrative.fragment.fragment_unlock_evaluator",
    "kind": "evaluator",
    "version": "0.1.0",
    "emoji": "🔓",
    "deterministic": True,
    "inputs": ["narrative.fragment_request.v1"],
    "outputs": ["narrative.fragment_response.v1"],
    "requires": [],
    "provides": ["narrative.fragment_unlock_decision"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["narrative", "fragment", "unlock", "trajectory", "node"],
    "description": "Evaluate whether a fragment can surface at a node from trajectory thresholds plus relay-only mountain gating.",
}


def evaluate_fragment_unlock(
    unlock_condition: dict[str, float] | None,
    trajectory: dict[str, float] | None,
    mountain_code: str,
    is_relay_node: bool,
) -> dict[str, Any]:
    trajectory_map = {str(key): float(value) for key, value in (trajectory or {}).items()}
    thresholds = {str(key): float(value) for key, value in (unlock_condition or {}).items()}
    threshold_pass = all(trajectory_map.get(key, 0.0) >= value for key, value in thresholds.items())
    relay_compatible = (is_relay_node and mountain_code == "M15") or ((not is_relay_node) and mountain_code != "M15")
    return {
        "unlock_condition": thresholds,
        "trajectory": trajectory_map,
        "mountain_code": mountain_code,
        "is_relay_node": bool(is_relay_node),
        "threshold_pass": threshold_pass,
        "relay_compatible": relay_compatible,
        "is_unlocked": bool(threshold_pass and relay_compatible),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = evaluate_fragment_unlock(
        unlock_condition=dict(payload.get("unlock_condition") or {}),
        trajectory=dict(payload.get("trajectory") or {}),
        mountain_code=str(payload.get("mountain_code") or ""),
        is_relay_node=bool(payload.get("is_relay_node")),
    )
    output_packet = {
        "packet_type": "narrative.fragment_response.v1",
        "packet_version": "narrative.fragment_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "fragment-unlock-decision",
        "brick_id": CONCEPT["id"],
        "kind": "evaluate",
        "label": "Evaluated fragment unlock decision.",
        "refs": [],
        "data": {"is_unlocked": value.get("is_unlocked", False), "relay_compatible": value.get("relay_compatible", False)},
    }]
