from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "backtest.calibration.scale_out_ladder_evaluator",
    "kind": "calculator",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["backtest.sim_request.v1"],
    "outputs": ["backtest.sim_response.v1"],
    "requires": [],
    "provides": ["backtest.scale_out_ladder_action"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["backtest", "management", "scale-out"],
    "description": "Evaluate a gradual scale-out ladder and return the next reduction action when a rung is earned.",
}


def scale_out_ladder_action(current_profit: float, rung: int, stake_amount: float, ladder: list[list[float]] | list[tuple[float, float]] | None, min_stake: float | None = None, min_partial_notional: float = 0.0) -> dict[str, Any] | None:
    if float(current_profit) <= 0:
        return None
    steps = list(ladder or [])
    if int(rung) >= len(steps):
        return None
    threshold, fraction = steps[int(rung)]
    if float(current_profit) < float(threshold):
        return None
    reduce_stake = float(stake_amount) * float(fraction)
    floor = max(float(min_partial_notional), float(min_stake) if min_stake is not None else 0.0)
    if reduce_stake < floor:
        return None
    return {"reduce_stake": -reduce_stake, "tag": f"scale_out_{int(rung) + 1}_{int(float(threshold) * 100)}pct"}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = scale_out_ladder_action(
        current_profit=float(payload.get("current_profit") or 0.0),
        rung=int(payload.get("rung") or 0),
        stake_amount=float(payload.get("stake_amount") or 0.0),
        ladder=payload.get("ladder"),
        min_stake=payload.get("min_stake"),
        min_partial_notional=float(payload.get("min_partial_notional") or 0.0),
    )
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


def receipts(value: dict[str, Any] | None) -> list[dict[str, Any]]:
    return [{"receipt_id": "scale-out-ladder", "brick_id": CONCEPT["id"], "kind": "management", "label": "Evaluated scale-out ladder.", "refs": [], "data": dict(value or {})}]
