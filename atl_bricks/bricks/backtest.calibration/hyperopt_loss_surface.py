from __future__ import annotations

from math import exp
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "backtest.calibration.hyperopt_loss_surface",
    "kind": "calculator",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["backtest.sim_request.v1"],
    "outputs": ["backtest.sim_response.v1"],
    "requires": [],
    "provides": ["backtest.hyperopt_loss_surface"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["backtest", "hyperopt", "loss"],
    "description": "Compute a composite loss from trade count, total profit, and mean trade duration.",
}


def hyperopt_loss_surface(trade_count: int, total_profit: float, mean_trade_duration: float, target_trades: int = 600, expected_max_profit: float = 3.0, max_accepted_trade_duration: float = 300.0) -> float:
    trade_loss = 1 - 0.25 * exp(-((int(trade_count) - int(target_trades)) ** 2) / 10**5.8)
    profit_loss = max(0.0, 1 - float(total_profit) / float(expected_max_profit))
    duration_loss = 0.4 * min(float(mean_trade_duration) / float(max_accepted_trade_duration), 1.0)
    return float(trade_loss + profit_loss + duration_loss)


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = {
        "loss": hyperopt_loss_surface(
            trade_count=int(payload.get("trade_count") or 0),
            total_profit=float(payload.get("total_profit") or 0.0),
            mean_trade_duration=float(payload.get("mean_trade_duration") or 0.0),
            target_trades=int(payload.get("target_trades") or 600),
            expected_max_profit=float(payload.get("expected_max_profit") or 3.0),
            max_accepted_trade_duration=float(payload.get("max_accepted_trade_duration") or 300.0),
        )
    }
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
    return [{
        "receipt_id": "hyperopt-loss-surface",
        "brick_id": CONCEPT["id"],
        "kind": "calculation",
        "label": "Computed hyperopt loss surface.",
        "refs": [],
        "data": {"loss": value.get("loss", 0.0)},
    }]
