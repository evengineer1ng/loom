from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "analytics.rankings.zscore_outlier_gate",
    "kind": "gate",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["analytics.rankings_request.v1"],
    "outputs": ["analytics.rankings_response.v1"],
    "requires": [],
    "provides": ["analytics.zscore_outlier_gate"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["analytics", "rankings", "zscore", "gate"],
    "description": "Decide long or short outlier entry eligibility from current and previous z-score state plus rank hurdles.",
}


def zscore_outlier_gate(z: float, z_prev: float, current_composite: float, std: float, in_cooldown: bool, zscore_entry: float, long_threshold: float, short_threshold: float) -> dict[str, bool]:
    if float(std) < 1e-9 or bool(in_cooldown):
        return {"enter_long": False, "enter_short": False}
    long_hurdle = max(float(zscore_entry), float(long_threshold))
    short_hurdle = min(-float(zscore_entry), float(short_threshold))
    return {
        "enter_long": float(z) > long_hurdle and float(z) > float(z_prev) and float(current_composite) > 0.0,
        "enter_short": float(z) < short_hurdle and float(z) < float(z_prev) and float(current_composite) < 0.0,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = zscore_outlier_gate(
        z=float(payload.get("z") or 0.0),
        z_prev=float(payload.get("z_prev") or 0.0),
        current_composite=float(payload.get("current_composite") or 0.0),
        std=float(payload.get("std") or 0.0),
        in_cooldown=bool(payload.get("in_cooldown", False)),
        zscore_entry=float(payload.get("zscore_entry") or 0.0),
        long_threshold=float(payload.get("long_threshold") or 0.0),
        short_threshold=float(payload.get("short_threshold") or 0.0),
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


def receipts(value: dict[str, bool]) -> list[dict[str, Any]]:
    return [{"receipt_id": "zscore-outlier-gate", "brick_id": CONCEPT["id"], "kind": "gate", "label": "Evaluated zscore outlier gate.", "refs": [], "data": value}]
