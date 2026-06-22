from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.sessions.ignition_gate_proof_builder",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.session_request.v1"],
    "outputs": ["runtime.session_response.v1"],
    "requires": [],
    "provides": ["runtime.ignition_gate_proof"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "session", "ignition", "gate", "proof"],
    "description": "Build move-ratio proof packets for delayed ignition gating decisions.",
}


def build_ignition_gate_proof(armed: bool, baseline_time: str | None, baseline_stake_abs: float, threshold: float, pnl_since: float) -> dict[str, Any]:
    baseline = max(float(baseline_stake_abs), 1.0)
    move_ratio = float(pnl_since) / baseline
    proof_ready = bool(armed) and bool(baseline_time)
    allowed = True if not proof_ready else abs(move_ratio) >= float(threshold)
    return {
        "armed": bool(armed),
        "baseline_time": baseline_time,
        "baseline_stake_abs": baseline,
        "threshold": float(threshold),
        "pnl_since": float(pnl_since),
        "move_ratio": move_ratio,
        "abs_move_ratio": abs(move_ratio),
        "proof_ready": proof_ready,
        "allowed": allowed,
        "gate_mode": "pass_through" if not proof_ready else "threshold_check",
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_ignition_gate_proof(
        armed=bool(payload.get("armed", False)),
        baseline_time=payload.get("baseline_time"),
        baseline_stake_abs=float(payload.get("baseline_stake_abs") or 1.0),
        threshold=float(payload.get("threshold") or 0.0),
        pnl_since=float(payload.get("pnl_since") or 0.0),
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
        "receipt_id": "ignition-gate-proof",
        "brick_id": CONCEPT["id"],
        "kind": "report",
        "label": "Built ignition gate proof packet.",
        "refs": [],
        "data": {"allowed": value.get("allowed", True), "move_ratio": value.get("move_ratio", 0.0)},
    }]
