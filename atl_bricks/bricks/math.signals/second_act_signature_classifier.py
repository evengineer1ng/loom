from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.signals.second_act_signature_classifier",
    "kind": "classifier",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.series_request.v1"],
    "outputs": ["math.series_response.v1"],
    "requires": [],
    "provides": ["math.second_act_signature"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "signals", "second-act", "classification"],
    "description": "Classify the live second-act outcome signature from indicator state.",
}


def second_act_signature(close: float, ema_fast: float, ema_slow: float, sma_mid: float, atr_ratio: float, adx: float, window_range: float, contraction_threshold: float, move_threshold: float, trend_adx: float, trend_separation: float, reversion_band: float, is_short: bool) -> str:
    sep = abs(float(ema_fast) - float(ema_slow)) / float(close) if float(close) else 0.0
    if float(atr_ratio) < float(contraction_threshold) and float(window_range) < float(move_threshold):
        return "base_building_exit"
    if float(adx) > float(trend_adx) and sep > float(trend_separation):
        return "regime_change_exit"
    if float(sma_mid) and abs(float(close) - float(sma_mid)) / float(sma_mid) < float(reversion_band):
        return "mean_reversion_exit"
    trend_up = float(ema_fast) >= float(ema_slow)
    if trend_up == (not bool(is_short)):
        return "continuation_exit"
    return "deadcat_exit"


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    label = second_act_signature(
        close=float(payload.get("close") or 0.0),
        ema_fast=float(payload.get("ema_fast") or 0.0),
        ema_slow=float(payload.get("ema_slow") or 0.0),
        sma_mid=float(payload.get("sma_mid") or 0.0),
        atr_ratio=float(payload.get("atr_ratio") or 1.0),
        adx=float(payload.get("adx") or 0.0),
        window_range=float(payload.get("window_range") or 0.0),
        contraction_threshold=float(payload.get("contraction_threshold") or 1.05),
        move_threshold=float(payload.get("move_threshold") or 0.06),
        trend_adx=float(payload.get("trend_adx") or 28.0),
        trend_separation=float(payload.get("trend_separation") or 0.015),
        reversion_band=float(payload.get("reversion_band") or 0.02),
        is_short=bool(payload.get("is_short", False)),
    )
    output_packet = {
        "packet_type": "math.series_response.v1",
        "packet_version": "math.series_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"label": label},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(label), "issues": [], "meta": {}}


def receipts(label: str) -> list[dict[str, Any]]:
    return [{"receipt_id": "second-act-signature", "brick_id": CONCEPT["id"], "kind": "classification", "label": "Classified second-act signature.", "refs": [], "data": {"label": label}}]
