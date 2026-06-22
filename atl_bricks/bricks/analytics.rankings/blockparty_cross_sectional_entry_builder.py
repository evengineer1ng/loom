from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "analytics.rankings.blockparty_cross_sectional_entry_builder",
    "kind": "analyzer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["analytics.rankings_request.v1"],
    "outputs": ["analytics.rankings_response.v1"],
    "requires": [],
    "provides": ["analytics.blockparty_cross_sectional_entries"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["analytics", "rankings", "blockparty", "cross-sectional"],
    "description": "Evaluate Block Party laggard, deep-value, ignition, and scout entry tracks from group move and own-gap state.",
}


def blockparty_cross_sectional_entries(row: dict[str, Any], group: float, breadth: float, n: int, group_fast: float | None, min_breadth: float, group_move_min: float, group_move_fast_min: float, group_move_strong: float, laggard_gap: float, soft_laggard_gap: float, deep_laggard_gap: float) -> dict[str, Any]:
    breadth_ok = float(breadth) >= float(min_breadth)
    lit_up = float(group) >= float(group_move_min) or (group_fast is not None and float(group_fast) >= float(group_move_fast_min))
    lit_down = float(group) <= -float(group_move_min) or (group_fast is not None and float(group_fast) <= -float(group_move_fast_min))
    strong_up = float(group) >= float(group_move_strong) or (group_fast is not None and float(group_fast) >= float(group_move_strong))
    strong_down = float(group) <= -float(group_move_strong) or (group_fast is not None and float(group_fast) <= -float(group_move_strong))
    own = float(row.get("ret_window") or 0.0)
    gap = own - float(group)

    result = {"enter_long": False, "enter_short": False, "gap": gap, "breadth_ok": breadth_ok, "n": n}
    if not breadth_ok:
        return result

    if lit_up:
        is_laggard = gap <= -float(laggard_gap)
        is_soft = strong_up and gap <= -float(soft_laggard_gap)
        is_deep = gap <= -float(deep_laggard_gap)
        score_long = int(row.get("score_long") or 0)
        vol_ok = bool(row.get("vol_ok", False))
        sig_not_extreme_long = bool(row.get("sig_not_extreme_long", False))
        sig_rsi_long = bool(row.get("sig_rsi_long", False))
        sig_macd_long = bool(row.get("sig_macd_long", False))
        sig_ema_long = bool(row.get("sig_ema_long", False))
        ret_current = float(row.get("ret_current") or 0.0)
        cond_core = (is_laggard or is_soft) and score_long >= 1 and vol_ok and sig_not_extreme_long
        cond_deep = is_deep and vol_ok and sig_not_extreme_long and (score_long >= 1 or (sig_rsi_long and sig_macd_long))
        cond_ignition = is_laggard and vol_ok and sig_ema_long and sig_rsi_long and ret_current > 0
        cond_scout = strong_up and gap <= -float(soft_laggard_gap) and vol_ok and sig_not_extreme_long and ret_current > 0 and sig_ema_long
        result["enter_long"] = cond_core or cond_deep or cond_ignition or cond_scout

    if lit_down:
        is_laggard = gap >= float(laggard_gap)
        is_soft = strong_down and gap >= float(soft_laggard_gap)
        is_deep = gap >= float(deep_laggard_gap)
        score_short = int(row.get("score_short") or 0)
        vol_ok = bool(row.get("vol_ok", False))
        sig_not_extreme_short = bool(row.get("sig_not_extreme_short", False))
        sig_rsi_short = bool(row.get("sig_rsi_short", False))
        sig_macd_short = bool(row.get("sig_macd_short", False))
        sig_ema_short = bool(row.get("sig_ema_short", False))
        ret_current = float(row.get("ret_current") or 0.0)
        cond_core = (is_laggard or is_soft) and score_short >= 1 and vol_ok and sig_not_extreme_short
        cond_deep = is_deep and vol_ok and sig_not_extreme_short and (score_short >= 1 or (sig_rsi_short and sig_macd_short))
        cond_ignition = is_laggard and vol_ok and sig_ema_short and sig_rsi_short and ret_current < 0
        cond_scout = strong_down and gap >= float(soft_laggard_gap) and vol_ok and sig_not_extreme_short and ret_current < 0 and sig_ema_short
        result["enter_short"] = cond_core or cond_deep or cond_ignition or cond_scout

    return result


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = blockparty_cross_sectional_entries(
        row=dict(payload.get("row") or {}),
        group=float(payload.get("group") or 0.0),
        breadth=float(payload.get("breadth") or 0.0),
        n=int(payload.get("n") or 0),
        group_fast=payload.get("group_fast"),
        min_breadth=float(payload.get("min_breadth") or 0.0),
        group_move_min=float(payload.get("group_move_min") or 0.0),
        group_move_fast_min=float(payload.get("group_move_fast_min") or 0.0),
        group_move_strong=float(payload.get("group_move_strong") or 0.0),
        laggard_gap=float(payload.get("laggard_gap") or 0.0),
        soft_laggard_gap=float(payload.get("soft_laggard_gap") or 0.0),
        deep_laggard_gap=float(payload.get("deep_laggard_gap") or 0.0),
    )
    output_packet = {
        "packet_type": "analytics.rankings_response.v1",
        "packet_version": "analytics.rankings_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"receipt_id": "blockparty-cross-sectional-entry", "brick_id": CONCEPT["id"], "kind": "analysis", "label": "Evaluated Block Party cross-sectional entry tracks.", "refs": [], "data": {"enter_long": value.get("enter_long", False), "enter_short": value.get("enter_short", False)}}]
