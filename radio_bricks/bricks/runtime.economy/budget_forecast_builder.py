from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.economy.budget_forecast_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.economy_request.v1"],
    "outputs": ["runtime.economy_response.v1"],
    "requires": [],
    "provides": ["runtime.budget_forecast_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "economy", "budget", "forecast"],
    "description": "Forecast budget pressure from burn, payroll, commitments, and recurring income.",
}


def build_budget_forecast_packet(
    cash: float,
    burn_rate: float,
    payroll_per_tick: float,
    commitments: list[dict[str, Any]] | None = None,
    income_streams: list[dict[str, Any]] | None = None,
    current_tick: int = 0,
    ticks_ahead: int = 6,
    bankruptcy_threshold: float = -50000.0,
) -> dict[str, Any]:
    future_commitments = 0.0
    for item in commitments or []:
        tick_due = int(item.get("tick_due") or 0)
        if current_tick < tick_due <= current_tick + ticks_ahead:
            future_commitments += float(item.get("amount") or 0.0)

    monthly_income = 0.0
    for stream in income_streams or []:
        if str(stream.get("frequency") or "") == "monthly":
            monthly_income += float(stream.get("amount") or 0.0)

    projected_cash = float(cash) - (float(burn_rate) + float(payroll_per_tick)) * ticks_ahead
    projected_cash -= future_commitments
    projected_cash += monthly_income * (ticks_ahead / 30.0)
    return {
        "cash": float(cash),
        "ticks_ahead": int(ticks_ahead),
        "projected_cash": projected_cash,
        "burn_cost": float(burn_rate) * ticks_ahead,
        "payroll_cost": float(payroll_per_tick) * ticks_ahead,
        "future_commitments": future_commitments,
        "monthly_income_credit": monthly_income * (ticks_ahead / 30.0),
        "bankruptcy_threshold": float(bankruptcy_threshold),
        "will_cross_bankruptcy_threshold": projected_cash < float(bankruptcy_threshold),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_budget_forecast_packet(
        cash=float(payload.get("cash") or 0.0),
        burn_rate=float(payload.get("burn_rate") or 0.0),
        payroll_per_tick=float(payload.get("payroll_per_tick") or 0.0),
        commitments=list(payload.get("commitments") or []),
        income_streams=list(payload.get("income_streams") or []),
        current_tick=int(payload.get("current_tick") or 0),
        ticks_ahead=int(payload.get("ticks_ahead") or 6),
        bankruptcy_threshold=float(payload.get("bankruptcy_threshold") or -50000.0),
    )
    output_packet = {
        "packet_type": "runtime.economy_response.v1",
        "packet_version": "runtime.economy_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "budget-forecast-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built budget forecast packet.",
        "refs": [],
        "data": {"projected_cash": value.get("projected_cash", 0.0)},
    }]
