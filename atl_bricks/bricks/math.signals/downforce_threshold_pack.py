from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.signals.downforce_threshold_pack",
    "kind": "gate",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.series_request.v1"],
    "outputs": ["math.series_response.v1"],
    "requires": [],
    "provides": ["math.downforce_threshold_pack"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "signals", "breakout", "confirmation"],
    "description": "Evaluate Downforce breakout, confirmation, and higher-timeframe threshold packs for long and short entries.",
}


def downforce_threshold_pack(row: dict[str, Any], comp_floor: float, expand_floor: float, breakout_floor: float, confirm_floor: float, entry_threshold: float, htf_rsi_long_max: float, htf_rsi_short_min: float) -> dict[str, bool]:
    htf_long = (
        float(row.get("ema_fast_15m") or 0.0) > float(row.get("ema_slow_15m") or 0.0)
        and float(row.get("ema_fast_1h") or 0.0) > float(row.get("ema_slow_1h") or 0.0)
        and float(row.get("rsi_15m", 50.0) or 50.0) < float(htf_rsi_long_max)
    )
    htf_short = (
        float(row.get("ema_fast_15m") or 0.0) < float(row.get("ema_slow_15m") or 0.0)
        and float(row.get("ema_fast_1h") or 0.0) < float(row.get("ema_slow_1h") or 0.0)
        and float(row.get("rsi_15m", 50.0) or 50.0) > float(htf_rsi_short_min)
    )
    return {
        "qualify_long": (
            float(row.get("comp_seen") or 0.0) >= comp_floor
            and float(row.get("expand_seen") or 0.0) >= expand_floor
            and bool(row.get("seq_comp_before_expand", False))
            and bool(row.get("seq_expand_fresh", False))
            and float(row.get("s_breakout_long") or 0.0) >= breakout_floor
            and float(row.get("s_confirm_long") or 0.0) >= confirm_floor
            and htf_long
            and float(row.get("df_long") or 0.0) >= entry_threshold
        ),
        "qualify_short": (
            float(row.get("comp_seen") or 0.0) >= comp_floor
            and float(row.get("expand_seen") or 0.0) >= expand_floor
            and bool(row.get("seq_comp_before_expand", False))
            and bool(row.get("seq_expand_fresh", False))
            and float(row.get("s_breakout_short") or 0.0) >= breakout_floor
            and float(row.get("s_confirm_short") or 0.0) >= confirm_floor
            and htf_short
            and float(row.get("df_short") or 0.0) >= entry_threshold
        ),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = downforce_threshold_pack(
        row=dict(payload.get("row") or {}),
        comp_floor=float(payload.get("comp_floor") or 0.0),
        expand_floor=float(payload.get("expand_floor") or 0.0),
        breakout_floor=float(payload.get("breakout_floor") or 0.0),
        confirm_floor=float(payload.get("confirm_floor") or 0.0),
        entry_threshold=float(payload.get("entry_threshold") or 0.0),
        htf_rsi_long_max=float(payload.get("htf_rsi_long_max") or 0.0),
        htf_rsi_short_min=float(payload.get("htf_rsi_short_min") or 0.0),
    )
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


def receipts(value: dict[str, bool]) -> list[dict[str, Any]]:
    return [{"receipt_id": "downforce-threshold-pack", "brick_id": CONCEPT["id"], "kind": "gate", "label": "Evaluated Downforce threshold pack.", "refs": [], "data": value}]
