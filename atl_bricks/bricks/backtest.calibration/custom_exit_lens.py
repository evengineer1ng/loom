from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "backtest.calibration.custom_exit_lens",
    "kind": "world_operator",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["backtest.sim_request.v1"],
    "outputs": ["backtest.sim_response.v1"],
    "requires": [],
    "provides": ["backtest.custom_exit_allowed"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["backtest", "exit", "lens"],
    "description": "Apply custom-exit disabling and profit-only gating as portable evaluator-control lenses.",
}


def custom_exit_allowed(disable_custom_exit: bool = False, profit_only_custom: bool = False, current_profit: float | None = None, profit_offset: float = 0.0) -> bool:
    if disable_custom_exit:
        return False
    if profit_only_custom and current_profit is not None and float(current_profit) <= float(profit_offset):
        return False
    return True


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    allowed = custom_exit_allowed(
        disable_custom_exit=bool(payload.get("disable_custom_exit", False)),
        profit_only_custom=bool(payload.get("profit_only_custom", False)),
        current_profit=payload.get("current_profit"),
        profit_offset=float(payload.get("profit_offset") or 0.0),
    )
    output_packet = {
        "packet_type": "backtest.sim_response.v1",
        "packet_version": "backtest.sim_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"allowed": allowed},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(allowed), "issues": [], "meta": {}}


def receipts(allowed: bool) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "custom-exit-lens",
        "brick_id": CONCEPT["id"],
        "kind": "gate",
        "label": "Applied custom-exit lens.",
        "refs": [],
        "data": {"allowed": allowed},
    }]
