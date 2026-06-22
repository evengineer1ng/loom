from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.signals.second_act_deadcat_labeler",
    "kind": "classifier",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.series_request.v1"],
    "outputs": ["math.series_response.v1"],
    "requires": [],
    "provides": ["math.second_act_deadcat_label"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "signals", "deadcat", "label"],
    "description": "Assign a Tier-1 deadcat subtype label from current state and excursion history.",
}


def second_act_deadcat_label(peak: float, current_profit: float, aligned: bool, adx: float, sep: float, atr_ratio: float, enter_tag: str, profit_activation: float, trend_adx: float, trend_separation: float, contraction_threshold: float) -> str:
    strong_trend = float(adx) > float(trend_adx) and float(sep) > float(trend_separation)
    if float(peak) >= float(profit_activation):
        return "deadcat_giveback"
    if strong_trend and not bool(aligned):
        return "deadcat_wrongside"
    if float(current_profit) <= -0.04:
        return "deadcat_failure"
    if str(enter_tag or "").startswith("base_building") and float(atr_ratio) < float(contraction_threshold):
        return "deadcat_invalidated"
    return "deadcat_chop"


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    label = second_act_deadcat_label(
        peak=float(payload.get("peak") or 0.0),
        current_profit=float(payload.get("current_profit") or 0.0),
        aligned=bool(payload.get("aligned", False)),
        adx=float(payload.get("adx") or 0.0),
        sep=float(payload.get("sep") or 0.0),
        atr_ratio=float(payload.get("atr_ratio") or 1.0),
        enter_tag=str(payload.get("enter_tag") or ""),
        profit_activation=float(payload.get("profit_activation") or 0.01),
        trend_adx=float(payload.get("trend_adx") or 28.0),
        trend_separation=float(payload.get("trend_separation") or 0.015),
        contraction_threshold=float(payload.get("contraction_threshold") or 1.05),
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
    return [{"receipt_id": "second-act-deadcat-label", "brick_id": CONCEPT["id"], "kind": "classification", "label": "Assigned second-act deadcat subtype.", "refs": [], "data": {"label": label}}]
