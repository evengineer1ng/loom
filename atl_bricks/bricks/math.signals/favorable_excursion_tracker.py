from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.signals.favorable_excursion_tracker",
    "kind": "calculator",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.series_request.v1"],
    "outputs": ["math.series_response.v1"],
    "requires": [],
    "provides": ["math.favorable_excursion"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "signals", "excursion"],
    "description": "Compute peak and current favorable excursion in the trade's own direction.",
}


def favorable_excursion(open_rate: float, current_rate: float, best_rate: float, is_short: bool) -> dict[str, float]:
    entry = float(open_rate or 0.0)
    if entry <= 0:
        return {"peak": 0.0, "current": 0.0}
    if bool(is_short):
        return {"peak": (entry - float(best_rate)) / entry, "current": (entry - float(current_rate)) / entry}
    return {"peak": (float(best_rate) - entry) / entry, "current": (float(current_rate) - entry) / entry}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = favorable_excursion(
        open_rate=float(payload.get("open_rate") or 0.0),
        current_rate=float(payload.get("current_rate") or 0.0),
        best_rate=float(payload.get("best_rate") or 0.0),
        is_short=bool(payload.get("is_short", False)),
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


def receipts(value: dict[str, float]) -> list[dict[str, Any]]:
    return [{"receipt_id": "favorable-excursion", "brick_id": CONCEPT["id"], "kind": "calculation", "label": "Computed favorable excursion.", "refs": [], "data": value}]
