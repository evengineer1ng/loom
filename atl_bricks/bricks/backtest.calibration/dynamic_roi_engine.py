from __future__ import annotations

import math
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "backtest.calibration.dynamic_roi_engine",
    "kind": "calculator",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["backtest.sim_request.v1"],
    "outputs": ["backtest.sim_response.v1"],
    "requires": [],
    "provides": ["backtest.dynamic_roi_value"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["backtest", "roi", "dynamic"],
    "description": "Compute a side-aware dynamic ROI target from holding time, ADX, DI spread, and volume change.",
}


def dynamic_roi_value(side: str, holding_minutes: float, base_roi: float, time_decay_factor: float, adx: float, plus_di: float, minus_di: float, volume_change: float, adx_high_roi_boost: float, adx_low_roi_penalty: float, trend_confirmation_boost: float, trend_confirmation_penalty: float, volume_boost_factor: float, floor: float) -> float:
    dyn = float(base_roi) + float(time_decay_factor) * math.log1p(float(holding_minutes))
    dyn += float(adx_high_roi_boost) * (float(adx) / 100.0)
    dyn -= float(adx_low_roi_penalty) * (1.0 - (float(adx) / 100.0))
    if str(side).lower() == "short":
        di_strength = (float(minus_di) - float(plus_di)) / 100.0
        dyn += float(trend_confirmation_boost) * max(di_strength, 0.0)
        dyn -= float(trend_confirmation_penalty) * max(-di_strength, 0.0)
    else:
        di_strength = (float(plus_di) - float(minus_di)) / 100.0
        dyn += float(trend_confirmation_boost) * di_strength
        dyn -= float(trend_confirmation_penalty) * (-di_strength)
    dyn += float(volume_boost_factor) * math.tanh(float(volume_change))
    return max(dyn, float(floor))


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = {
        "roi": dynamic_roi_value(
            side=str(payload.get("side") or "long"),
            holding_minutes=float(payload.get("holding_minutes") or 0.0),
            base_roi=float(payload.get("base_roi") or 0.0),
            time_decay_factor=float(payload.get("time_decay_factor") or 0.0),
            adx=float(payload.get("adx") or 0.0),
            plus_di=float(payload.get("plus_di") or 0.0),
            minus_di=float(payload.get("minus_di") or 0.0),
            volume_change=float(payload.get("volume_change") or 0.0),
            adx_high_roi_boost=float(payload.get("adx_high_roi_boost") or 0.0),
            adx_low_roi_penalty=float(payload.get("adx_low_roi_penalty") or 0.0),
            trend_confirmation_boost=float(payload.get("trend_confirmation_boost") or 0.0),
            trend_confirmation_penalty=float(payload.get("trend_confirmation_penalty") or 0.0),
            volume_boost_factor=float(payload.get("volume_boost_factor") or 0.0),
            floor=float(payload.get("floor") or 0.0),
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
    return [{"receipt_id": "dynamic-roi-engine", "brick_id": CONCEPT["id"], "kind": "calculation", "label": "Computed dynamic ROI value.", "refs": [], "data": value}]
