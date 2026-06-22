from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "backtest.calibration.deadcat_subtype_classifier",
    "kind": "classifier",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["backtest.sim_request.v1"],
    "outputs": ["backtest.sim_response.v1"],
    "requires": [],
    "provides": ["backtest.deadcat_subtype"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["backtest", "deadcat", "classification"],
    "description": "Classify deadcat exits into deterministic subtypes using excursion shape and exit-state telemetry.",
}


def deadcat_subtype(mfe: float, mae: float, aligned: bool, adx: float, sep: float, atr_ratio: float, trend_adx: float = 28.0, trend_separation: float = 0.015, contraction_threshold: float = 1.05) -> str:
    strong_trend = float(adx) > float(trend_adx) and float(sep) > float(trend_separation)
    if float(mfe) >= 0.01 and float(mae) > -0.01:
        return "never_adverse_winner_gaveback"
    if strong_trend and not bool(aligned):
        return "wrong_side_strong_trend"
    if strong_trend and bool(aligned):
        return "should_be_regime_change"
    if float(mae) <= -0.04:
        return "confirmed_failure_deep"
    if float(atr_ratio) < float(contraction_threshold):
        return "invalidated_base"
    return "mild_chop_ambiguous"


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    label = deadcat_subtype(
        mfe=float(payload.get("mfe") or 0.0),
        mae=float(payload.get("mae") or 0.0),
        aligned=bool(payload.get("aligned", False)),
        adx=float(payload.get("adx") or 0.0),
        sep=float(payload.get("sep") or 0.0),
        atr_ratio=float(payload.get("atr_ratio") or 0.0),
        trend_adx=float(payload.get("trend_adx") or 28.0),
        trend_separation=float(payload.get("trend_separation") or 0.015),
        contraction_threshold=float(payload.get("contraction_threshold") or 1.05),
    )
    output_packet = {
        "packet_type": "backtest.sim_response.v1",
        "packet_version": "backtest.sim_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"label": label},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(label), "issues": [], "meta": {}}


def receipts(label: str) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "deadcat-subtype",
        "brick_id": CONCEPT["id"],
        "kind": "classification",
        "label": "Classified deadcat subtype.",
        "refs": [],
        "data": {"label": label},
    }]
