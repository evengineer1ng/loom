from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "history.metrics.momentum_metric_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["history.metrics_request.v1"],
    "outputs": ["history.metrics_response.v1"],
    "requires": [],
    "provides": ["history.momentum_metric_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["history", "metrics", "momentum", "math"],
    "description": "Derive form and momentum slope from recent championship positions.",
}


def build_momentum_metric_packet(championship_positions: list[int] | None, tick: int) -> dict[str, Any]:
    finishes = [int(value) for value in (championship_positions or []) if int(value) > 0][:5]
    if len(finishes) < 2:
        return {
            "form_last_3_races": 50.0,
            "form_last_5_races": 50.0,
            "momentum_slope": 0.0,
            "momentum_state": "stable",
            "last_updated_tick": int(tick),
        }

    form_last_3 = 100.0 - (sum(finishes[:3]) / len(finishes[:3]) * 5.0) if len(finishes) >= 3 else 50.0
    form_last_5 = 100.0 - (sum(finishes) / len(finishes) * 5.0) if len(finishes) >= 5 else 50.0

    finishes_reversed = list(reversed(finishes))
    count = len(finishes_reversed)
    x_mean = (count - 1) / 2.0
    y_mean = sum(finishes_reversed) / count
    numerator = sum((index - x_mean) * (finishes_reversed[index] - y_mean) for index in range(count))
    denominator = sum((index - x_mean) ** 2 for index in range(count))
    slope = numerator / denominator if denominator else 0.0
    momentum_slope = -slope

    if momentum_slope > 2.0:
        momentum_state = "surging"
    elif momentum_slope > 0.5:
        momentum_state = "rising"
    elif momentum_slope < -2.0:
        momentum_state = "collapsing"
    elif momentum_slope < -0.5:
        momentum_state = "declining"
    else:
        momentum_state = "stable"

    return {
        "form_last_3_races": form_last_3,
        "form_last_5_races": form_last_5,
        "momentum_slope": momentum_slope,
        "momentum_state": momentum_state,
        "last_updated_tick": int(tick),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_momentum_metric_packet(
        championship_positions=list(payload.get("championship_positions") or []),
        tick=int(payload.get("tick") or 0),
    )
    output_packet = {
        "packet_type": "history.metrics_response.v1",
        "packet_version": "history.metrics_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "momentum-metric-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built momentum metric packet.",
        "refs": [],
        "data": {"momentum_state": value.get("momentum_state", "stable")},
    }]
