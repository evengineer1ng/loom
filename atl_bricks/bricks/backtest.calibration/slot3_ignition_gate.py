from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "backtest.calibration.slot3_ignition_gate",
    "kind": "gate",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["backtest.sim_request.v1"],
    "outputs": ["backtest.sim_response.v1"],
    "requires": [],
    "provides": ["backtest.slot3_ignition_allows"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["backtest", "ignition", "gate"],
    "description": "Apply macro or micro slot-3 ignition gating from baseline stake snapshots and side PnL movement.",
}


def slot3_ignition_allows(armed: bool, baseline_stake_abs: float, pnl_since: float, threshold: float, fail_open_when_unarmed: bool = True) -> bool:
    if not armed:
        return bool(fail_open_when_unarmed)
    move_ratio = float(pnl_since) / max(float(baseline_stake_abs), 1.0)
    return abs(move_ratio) >= float(threshold)


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = {"allowed": slot3_ignition_allows(bool(payload.get("armed", False)), float(payload.get("baseline_stake_abs") or 1.0), float(payload.get("pnl_since") or 0.0), float(payload.get("threshold") or 0.0), bool(payload.get("fail_open_when_unarmed", True)))}
    output_packet = {
        "packet_type": "backtest.sim_response.v1",
        "packet_version": "backtest.sim_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"receipt_id": "slot3-ignition-gate", "brick_id": CONCEPT["id"], "kind": "gate", "label": "Evaluated slot3 ignition gate.", "refs": [], "data": value}]
