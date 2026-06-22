from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.signals.composite_momentum_score",
    "kind": "calculator",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.series_request.v1"],
    "outputs": ["math.series_response.v1"],
    "requires": [],
    "provides": ["math.composite_momentum_score"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "signals", "momentum", "composite"],
    "description": "Compute a weighted multi-horizon composite momentum score.",
}


def composite_momentum_score(return_15m: float, return_1h: float, return_4h: float, weights: list[float] | None = None) -> float:
    a, b, c = list(weights or [0.5, 0.3, 0.2])
    return float(a) * float(return_15m) + float(b) * float(return_1h) + float(c) * float(return_4h)


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = {"score": composite_momentum_score(float(payload.get("return_15m") or 0.0), float(payload.get("return_1h") or 0.0), float(payload.get("return_4h") or 0.0), payload.get("weights"))}
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
    return [{"receipt_id": "composite-momentum-score", "brick_id": CONCEPT["id"], "kind": "calculation", "label": "Computed composite momentum score.", "refs": [], "data": value}]
