from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "analytics.trades.obvious_loss_detector",
    "kind": "analyzer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["analytics.trades_request.v1"],
    "outputs": ["analytics.trades_response.v1"],
    "requires": [],
    "provides": ["analytics.loss_obvious_before_exit"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["analytics", "trades", "loss", "timing"],
    "description": "Detect whether a loss threshold was breached at least N candles before the final exit candle.",
}


def loss_obvious_before_exit(adverse_path: list[float] | None, threshold: float = -0.02, min_candles_before_exit: int = 4) -> bool:
    values = list(adverse_path or [])
    for index, value in enumerate(values):
        if float(value) <= float(threshold) and (len(values) - 1 - index) >= int(min_candles_before_exit):
            return True
    return False


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = {
        "obvious": loss_obvious_before_exit(
            adverse_path=payload.get("adverse_path"),
            threshold=float(payload.get("threshold") or -0.02),
            min_candles_before_exit=int(payload.get("min_candles_before_exit") or 4),
        )
    }
    output_packet = {
        "packet_type": "analytics.trades_response.v1",
        "packet_version": "analytics.trades_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "obvious-loss-detector",
        "brick_id": CONCEPT["id"],
        "kind": "analysis",
        "label": "Detected whether the loss was obvious before exit.",
        "refs": [],
        "data": {"obvious": value.get("obvious", False)},
    }]
