from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.sessions.ignition_transition_packet_builder",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.session_request.v1"],
    "outputs": ["runtime.session_response.v1"],
    "requires": [],
    "provides": ["runtime.ignition_transition_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "session", "ignition", "transition"],
    "description": "Build explicit macro-arm and micro-rearm transition packets for delayed ignition state.",
}


def build_ignition_transition_packet(state: dict[str, Any] | None, count: int, now_iso: str, baseline_stake_abs: float, macro_threshold: float, micro_threshold: float) -> dict[str, Any]:
    current = dict(state or {})
    last_open_count = int(current.get("last_open_count", 0) or 0)
    ever_had_3 = bool(current.get("ever_had_3", False)) or int(count) >= 3
    event = "none"
    threshold = float(current.get("threshold", macro_threshold) or macro_threshold)
    baseline_time = current.get("baseline_time")
    next_baseline_stake = float(current.get("baseline_stake_abs", 1.0) or 1.0)
    transitioned = False

    if ever_had_3 and last_open_count >= 3 and int(count) == 2:
        event = "micro_rearm"
        threshold = float(micro_threshold)
        baseline_time = now_iso
        next_baseline_stake = max(float(baseline_stake_abs), 1.0)
        transitioned = True
    elif int(count) == 2 and current.get("baseline_time") is None:
        event = "macro_arm"
        threshold = float(macro_threshold)
        baseline_time = now_iso
        next_baseline_stake = max(float(baseline_stake_abs), 1.0)
        transitioned = True

    return {
        "event": event,
        "transitioned": transitioned,
        "count": int(count),
        "last_open_count": last_open_count,
        "ever_had_3": ever_had_3,
        "baseline_time": baseline_time,
        "baseline_stake_abs": next_baseline_stake,
        "threshold": threshold,
        "armed_after": bool(current.get("armed", False)) or transitioned,
        "reason": {
            "macro_arm_ready": int(count) == 2 and current.get("baseline_time") is None,
            "micro_rearm_ready": ever_had_3 and last_open_count >= 3 and int(count) == 2,
        },
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_ignition_transition_packet(
        state=dict(payload.get("state") or {}),
        count=int(payload.get("count") or 0),
        now_iso=str(payload.get("now_iso") or ""),
        baseline_stake_abs=float(payload.get("baseline_stake_abs") or 1.0),
        macro_threshold=float(payload.get("macro_threshold") or 0.0),
        micro_threshold=float(payload.get("micro_threshold") or 0.0),
    )
    output_packet = {
        "packet_type": "runtime.session_response.v1",
        "packet_version": "runtime.session_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "ignition-transition-packet",
        "brick_id": CONCEPT["id"],
        "kind": "state",
        "label": "Built ignition transition packet.",
        "refs": [],
        "data": {"event": value.get("event", "none"), "transitioned": value.get("transitioned", False)},
    }]
