from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.sessions.ignition_state_packet_builder",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.session_request.v1"],
    "outputs": ["runtime.session_response.v1"],
    "requires": [],
    "provides": ["runtime.ignition_state_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "session", "ignition", "state"],
    "description": "Build macro or micro ignition arming and rearming state packets for slot-3 gating.",
}


def build_ignition_state_packet(state: dict[str, Any] | None, count: int, last_open_count: int, baseline_stake_abs: float, now_iso: str, macro_threshold: float, micro_threshold: float) -> dict[str, Any]:
    current = dict(state or {})
    ever_had_3 = bool(current.get("ever_had_3", False)) or int(count) >= 3
    armed = bool(current.get("armed", False))
    threshold = float(current.get("threshold", macro_threshold) or macro_threshold)
    event = "none"
    if ever_had_3 and int(last_open_count) >= 3 and int(count) == 2:
        armed = True
        threshold = float(micro_threshold)
        event = "micro_rearm"
    elif int(count) == 2 and current.get("baseline_time") is None:
        armed = True
        threshold = float(macro_threshold)
        event = "macro_arm"
    return {
        "baseline_time": now_iso if event in {"micro_rearm", "macro_arm"} else current.get("baseline_time"),
        "baseline_stake_abs": max(float(baseline_stake_abs), 1.0) if event in {"micro_rearm", "macro_arm"} else float(current.get("baseline_stake_abs", 1.0) or 1.0),
        "threshold": threshold,
        "ever_had_3": ever_had_3,
        "last_open_count": int(count),
        "armed": armed,
        "event": event,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_ignition_state_packet(
        state=dict(payload.get("state") or {}),
        count=int(payload.get("count") or 0),
        last_open_count=int(payload.get("last_open_count") or 0),
        baseline_stake_abs=float(payload.get("baseline_stake_abs") or 1.0),
        now_iso=str(payload.get("now_iso") or ""),
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
    return [{"receipt_id": "ignition-state-packet", "brick_id": CONCEPT["id"], "kind": "state", "label": "Built ignition state packet.", "refs": [], "data": {"event": value.get("event", "none"), "armed": value.get("armed", False)}}]
