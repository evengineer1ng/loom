from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "backtest.calibration.timeout_extension_evaluator",
    "kind": "calculator",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["backtest.sim_request.v1"],
    "outputs": ["backtest.sim_response.v1"],
    "requires": [],
    "provides": ["backtest.timeout_extension_summary"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["backtest", "timeout", "extension"],
    "description": "Summarize forward-return deltas from timeout exits across fixed horizons and trailing continuation.",
}


def timeout_extension_summary(rows: list[dict[str, Any]] | None, horizons: list[int] | None = None) -> dict[str, Any]:
    horizon_list = list(horizons or [1, 2, 4, 8])
    agg: dict[int, list[float]] = {h: [] for h in horizon_list}
    flips: dict[int, int] = {h: 0 for h in horizon_list}
    trail: list[float] = []
    n_ok = 0
    for row in list(rows or []):
        actual = float(row.get("actual_profit_ratio") or 0.0)
        forward = dict(row.get("horizons") or {})
        if not forward and "trail_final" not in row:
            continue
        n_ok += 1
        for horizon in horizon_list:
            if horizon not in forward and str(horizon) not in forward:
                continue
            value = forward.get(horizon, forward.get(str(horizon)))
            if value is None:
                continue
            delta = float(value) - actual
            agg[horizon].append(delta)
            if actual > 0 and float(value) <= 0:
                flips[horizon] += 1
        if row.get("trail_final") is not None:
            trail.append(float(row.get("trail_final")) - actual)
    horizon_summary = []
    for horizon in horizon_list:
        values = agg[horizon]
        if not values:
            continue
        improved = sum(1 for value in values if value > 0)
        horizon_summary.append({
            "horizon": horizon,
            "avg_delta_roi": sum(values) / len(values),
            "improved_pct": improved / len(values) * 100,
            "win_to_loss_flips": flips[horizon],
            "flip_pct": flips[horizon] / max(n_ok, 1) * 100,
        })
    return {
        "n_ok": n_ok,
        "horizons": horizon_summary,
        "trail_avg_delta_roi": (sum(trail) / len(trail)) if trail else None,
        "trail_improved_pct": (sum(1 for value in trail if value > 0) / len(trail) * 100) if trail else None,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = timeout_extension_summary(list(payload.get("rows") or []), list(payload.get("horizons") or [1, 2, 4, 8]))
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
        "receipt_id": "timeout-extension-summary",
        "brick_id": CONCEPT["id"],
        "kind": "simulation",
        "label": "Summarized timeout extension evaluation.",
        "refs": [],
        "data": {"n_ok": value.get("n_ok", 0), "horizons": len(value.get("horizons") or [])},
    }]
