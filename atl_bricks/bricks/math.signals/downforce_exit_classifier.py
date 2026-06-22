from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.signals.downforce_exit_classifier",
    "kind": "classifier",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.series_request.v1"],
    "outputs": ["math.series_response.v1"],
    "requires": [],
    "provides": ["math.downforce_exit_label"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "signals", "downforce", "exit"],
    "description": "Classify Downforce exhaustion, invalidation, and reversal exits from current state.",
}


def downforce_exit_label(last: dict[str, Any], prev_adx: float, is_long: bool, current_profit_ratio: float, exhaustion_exit: float) -> str | None:
    dir_suff = "long" if is_long else "short"
    exhaustion = float(last.get(f"s_exhaustion_{dir_suff}") or 0.0)
    if exhaustion >= exhaustion_exit and current_profit_ratio > 0.008:
        return f"df_exhaustion_{dir_suff}"
    confirm_collapse = float(last.get(f"s_confirm_{dir_suff}") or 0.0) < 0.25
    adx = float(last.get("adx") or 0.0)
    adx_crumble = adx < 20.0 and (adx - float(prev_adx)) < -6.0
    if confirm_collapse and adx_crumble:
        return f"df_invalidation_{dir_suff}"
    ema_f = float(last.get("ema_f") or 0.0)
    ema_m = float(last.get("ema_m") or 0.0)
    plus_di = float(last.get("plus_di") or 0.0)
    minus_di = float(last.get("minus_di") or 0.0)
    ema_fast_1h = float(last.get("ema_fast_1h") or 0.0)
    ema_slow_1h = float(last.get("ema_slow_1h") or 0.0)
    if is_long:
        rev = ema_f < ema_m or minus_di > plus_di
        htf_rev = ema_fast_1h < ema_slow_1h
    else:
        rev = ema_f > ema_m or plus_di > minus_di
        htf_rev = ema_fast_1h > ema_slow_1h
    if rev and htf_rev:
        return f"df_reversal_{dir_suff}"
    return None


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    label = downforce_exit_label(
        last=dict(payload.get("last") or {}),
        prev_adx=float(payload.get("prev_adx") or 0.0),
        is_long=bool(payload.get("is_long", True)),
        current_profit_ratio=float(payload.get("current_profit_ratio") or 0.0),
        exhaustion_exit=float(payload.get("exhaustion_exit") or 0.0),
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


def receipts(label: str | None) -> list[dict[str, Any]]:
    return [{"receipt_id": "downforce-exit-classifier", "brick_id": CONCEPT["id"], "kind": "classification", "label": "Classified Downforce exit.", "refs": [], "data": {"label": label}}]
