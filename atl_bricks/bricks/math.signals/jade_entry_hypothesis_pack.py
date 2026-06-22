from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.signals.jade_entry_hypothesis_pack",
    "kind": "gate",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.series_request.v1"],
    "outputs": ["math.series_response.v1"],
    "requires": [],
    "provides": ["math.jade_entry_hypotheses"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "signals", "jade", "entry"],
    "description": "Evaluate Jade-style entry hypotheses across divergence, breadth, regime, and breakout state.",
}


def jade_entry_hypotheses(row: dict[str, Any], is_btc: bool) -> dict[str, Any]:
    volume_strong = bool(row.get("volume_strong", False))
    adx_gate = bool(row.get("adx_gate", False))
    breakout_high_ok = bool(row.get("breakout_high_ok", False))
    breakout_low_ok = bool(row.get("breakout_low_ok", False))
    rsi = float(row.get("rsi") or 0.0)
    divergence = float(row.get("divergence") or 0.0)
    divergence_z = float(row.get("divergence_z") or 0.0)
    bearish_ok = bool(row.get("regime_bearish", False))
    strong_trend = bool(row.get("strong_trend", False))
    ranging_prev = bool(row.get("ranging_prev", False))
    trending = bool(row.get("trending", False))
    vol_ratio = float(row.get("vol_ratio") or 0.0)
    lead_lag_score = float(row.get("lead_lag_score") or 0.0)
    basket_breadth = float(row.get("basket_breadth") or 0.0)
    lead_lag_corr = float(row.get("lead_lag_corr") or 0.0)
    basket_vol = float(row.get("basket_vol") or 0.0)
    volatility = float(row.get("volatility") or 0.0)

    base_long = breakout_high_ok and adx_gate and volume_strong and 30 < rsi < 80
    base_short = breakout_low_ok and adx_gate and volume_strong and 20 < rsi < 70

    out = {
        "h1_breakout_divergence_long": base_long and divergence > 0,
        "h2_divergence_revert_long": base_long and divergence_z < -2.0 and rsi > 35,
        "h3_regime_ignition_long": base_long and ranging_prev and trending and vol_ratio > 1.0,
        "h4_breakdown_divergence_short": base_short and divergence < 0 and bearish_ok,
        "h5_divergence_fade_short": base_short and divergence_z > 2.0 and rsi < 65 and bearish_ok,
        "h6_vol_climax_short": base_short and vol_ratio > 1.5 and strong_trend and rsi > 50 and bearish_ok,
    }
    if is_btc:
        out.update({
            "h7_btc_leads_breadth_long": base_long and lead_lag_score > 0.1 and basket_breadth > 0.55,
            "h8_basket_leads_catchup_long": base_long and lead_lag_score < -0.1 and divergence_z < -0.5,
            "h9_low_corr_solo_long": base_long and lead_lag_corr < 0.3 and vol_ratio > 1.2,
            "h10_high_corr_ignition_long": base_long and lead_lag_corr > 0.7 and bool(row.get("low_dispersion", False)),
            "h11_alt_vol_favor_short": base_short and basket_vol > volatility * 1.3 and divergence < 0 and bearish_ok,
            "h12_btc_vol_expansion_long": base_long and strong_trend and vol_ratio > 1.2 and bool(row.get("volatility_rising", False)),
            "h13_breadth_expansion_long": base_long and basket_breadth > 0.6 and bool(row.get("breadth_rising", False)),
            "h14_breadth_contraction_short": base_short and basket_breadth < 0.4 and bool(row.get("breadth_falling", False)) and bearish_ok,
        })
    else:
        out.update({
            "hA_alt_catchup_long": base_long and divergence_z < -1.0,
            "hA_alt_premium_short": base_short and divergence_z > 1.0 and bearish_ok,
        })
    return out


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = jade_entry_hypotheses(dict(payload.get("row") or {}), bool(payload.get("is_btc", False)))
    output_packet = {
        "packet_type": "math.series_response.v1",
        "packet_version": "math.series_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"receipt_id": "jade-entry-hypotheses", "brick_id": CONCEPT["id"], "kind": "gate", "label": "Evaluated Jade entry hypotheses.", "refs": [], "data": {"hypotheses": len(value)}}]
