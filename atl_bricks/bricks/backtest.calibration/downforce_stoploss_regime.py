from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "backtest.calibration.downforce_stoploss_regime",
    "kind": "calculator",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["backtest.sim_request.v1"],
    "outputs": ["backtest.sim_response.v1"],
    "requires": [],
    "provides": ["backtest.downforce_stoploss_regime"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["backtest", "stoploss", "regime"],
    "description": "Choose a Downforce-style stoploss distance from profit zone, maturity, and exhaustion telemetry.",
}


def downforce_stoploss_regime(analytics: dict[str, Any], is_long: bool, current_profit: float) -> float | None:
    if not analytics:
        return None
    sign = -1.0 if is_long else 1.0
    dir_suff = "long" if is_long else "short"
    if current_profit < 0.015:
        return sign * 0.035
    if current_profit < 0.04:
        return sign * 0.015
    maturity = float(analytics.get(f"s_maturity_{dir_suff}") or 0.0)
    if maturity > 0.55:
        return sign * 0.008
    exhaustion = float(analytics.get(f"s_exhaustion_{dir_suff}") or 0.0)
    if exhaustion > 0.45:
        return sign * 0.005
    return None


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = {"stoploss": downforce_stoploss_regime(dict(payload.get("analytics") or {}), bool(payload.get("is_long", True)), float(payload.get("current_profit") or 0.0))}
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
    return [{"receipt_id": "downforce-stoploss-regime", "brick_id": CONCEPT["id"], "kind": "calculation", "label": "Evaluated Downforce stoploss regime.", "refs": [], "data": value}]
