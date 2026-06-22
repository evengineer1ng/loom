from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.signals.maverick_entry_exit_pack",
    "kind": "gate",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.series_request.v1"],
    "outputs": ["math.series_response.v1"],
    "requires": [],
    "provides": ["math.maverick_entry_exit_pack"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "signals", "maverick"],
    "description": "Evaluate Maverick z-score outlier entries, mean-reversion exits, and time-stop losers.",
}


def maverick_entry_exit_pack(z: float, z_prev: float, current_composite: float, std: float, in_cooldown: bool, zscore_entry: float, long_threshold: float, short_threshold: float, exit_zscore_threshold: float, is_short: bool, duration_minutes: float, current_profit: float, time_stop_minutes: float) -> dict[str, Any]:
    long_hurdle = max(float(zscore_entry), float(long_threshold))
    short_hurdle = min(-float(zscore_entry), float(short_threshold))
    enter_long = float(std) >= 1e-9 and not in_cooldown and float(z) > long_hurdle and float(z) > float(z_prev) and float(current_composite) > 0.0
    enter_short = float(std) >= 1e-9 and not in_cooldown and float(z) < short_hurdle and float(z) < float(z_prev) and float(current_composite) < 0.0
    exit_label = None
    if is_short and float(z) > -float(exit_zscore_threshold):
        exit_label = "zscore_mean_revert_short"
    elif not is_short and float(z) < float(exit_zscore_threshold):
        exit_label = "zscore_mean_revert_long"
    elif float(duration_minutes) >= float(time_stop_minutes) and float(current_profit) < 0:
        exit_label = "time_stop_loser"
    return {"enter_long": enter_long, "enter_short": enter_short, "exit_label": exit_label}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = maverick_entry_exit_pack(
        z=float(payload.get("z") or 0.0),
        z_prev=float(payload.get("z_prev") or 0.0),
        current_composite=float(payload.get("current_composite") or 0.0),
        std=float(payload.get("std") or 0.0),
        in_cooldown=bool(payload.get("in_cooldown", False)),
        zscore_entry=float(payload.get("zscore_entry") or 0.0),
        long_threshold=float(payload.get("long_threshold") or 0.0),
        short_threshold=float(payload.get("short_threshold") or 0.0),
        exit_zscore_threshold=float(payload.get("exit_zscore_threshold") or 0.0),
        is_short=bool(payload.get("is_short", False)),
        duration_minutes=float(payload.get("duration_minutes") or 0.0),
        current_profit=float(payload.get("current_profit") or 0.0),
        time_stop_minutes=float(payload.get("time_stop_minutes") or 0.0),
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


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"receipt_id": "maverick-pack", "brick_id": CONCEPT["id"], "kind": "gate", "label": "Evaluated Maverick entry/exit pack.", "refs": [], "data": value}]
