from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "analytics.trades.attribution_score_builder",
    "kind": "analyzer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["analytics.trades_request.v1"],
    "outputs": ["analytics.trades_response.v1"],
    "requires": [],
    "provides": ["analytics.trade_attribution_scores"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["analytics", "trades", "attribution"],
    "description": "Build exit-damage, exit-alpha, entry-raw, force-dependence, churn, and custom-exit contribution scores from variant metrics.",
}


def trade_attribution_scores(metrics_by_variant: dict[str, dict[str, Any]] | None) -> dict[str, Any]:
    variants = dict(metrics_by_variant or {})
    baseline = variants.get("baseline")
    exit_off = variants.get("exit_off")
    profit_only = variants.get("profit_only")
    custom_exit_off = variants.get("custom_exit_off")
    out: dict[str, Any] = {}
    if baseline and exit_off:
        out["exit_damage"] = round(float(exit_off.get("pnl", 0.0)) - float(baseline.get("pnl", 0.0)), 1)
        out["exit_alpha"] = round(float(baseline.get("pnl", 0.0)) - float(exit_off.get("pnl", 0.0)), 1)
        exit_off_pnl = float(exit_off.get("pnl", 0.0))
        force_dep = abs(float(exit_off.get("force_pnl", 0.0))) / (abs(exit_off_pnl) + 1e-9) if exit_off_pnl else 0.0
        out["entry_raw"] = round(exit_off_pnl - 0.25 * float(exit_off.get("dd", 0.0)) - 30 * min(force_dep, 1.0), 1)
        out["force_dependence"] = round(force_dep, 2)
        exit_off_trades = float(exit_off.get("trades", 0) or 0)
        out["churn_amp"] = round(float(baseline.get("trades", 0) or 0) / exit_off_trades, 2) if exit_off_trades else float("inf")
    if baseline and profit_only:
        out["profit_only_sensitivity"] = round(float(profit_only.get("pnl", 0.0)) - float(baseline.get("pnl", 0.0)), 1)
    if baseline and custom_exit_off:
        out["custom_exit_contribution"] = round(float(baseline.get("pnl", 0.0)) - float(custom_exit_off.get("pnl", 0.0)), 1)
    return out


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    value = trade_attribution_scores(dict(input_packet.get("payload") or {}))
    output_packet = {
        "packet_type": "analytics.trades_response.v1",
        "packet_version": "analytics.trades_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "trade-attribution-scores",
        "brick_id": CONCEPT["id"],
        "kind": "analysis",
        "label": "Built trade attribution scores.",
        "refs": [],
        "data": {"exit_damage": value.get("exit_damage"), "entry_raw": value.get("entry_raw")},
    }]
