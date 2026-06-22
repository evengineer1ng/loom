from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.signals.pre_expansion_confirmation_gate",
    "kind": "classifier",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.series_request.v1"],
    "outputs": ["math.series_response.v1"],
    "requires": [],
    "provides": ["math.pre_expansion_confirmation"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "signals", "pre-expansion", "confirmation", "compression"],
    "description": "Confirm an expansion entry only when a matching directional compression signal existed in the immediately preceding lookback window.",
}


def evaluate_pre_expansion_confirmation(cosmo_long: bool, cosmo_short: bool, prior_long_signals: list[float] | None, prior_short_signals: list[float] | None, prior_long_confidences: list[float] | None = None, prior_short_confidences: list[float] | None = None) -> dict[str, Any]:
    long_hits = [float(item) for item in (prior_long_signals or [])]
    short_hits = [float(item) for item in (prior_short_signals or [])]
    long_conf = [float(item) for item in (prior_long_confidences or [])]
    short_conf = [float(item) for item in (prior_short_confidences or [])]
    long_confirm = any(item >= 1.0 for item in long_hits)
    short_confirm = any(item >= 1.0 for item in short_hits)
    final_long = bool(cosmo_long) and long_confirm
    final_short = bool(cosmo_short) and short_confirm
    return {
        "long_confirm": long_confirm,
        "short_confirm": short_confirm,
        "final_long": final_long,
        "final_short": final_short,
        "rejected_long": bool(cosmo_long) and not long_confirm,
        "rejected_short": bool(cosmo_short) and not short_confirm,
        "long_confidence_max": max(long_conf) if long_conf else None,
        "short_confidence_max": max(short_conf) if short_conf else None,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = evaluate_pre_expansion_confirmation(
        cosmo_long=bool(payload.get("cosmo_long", False)),
        cosmo_short=bool(payload.get("cosmo_short", False)),
        prior_long_signals=list(payload.get("prior_long_signals") or []),
        prior_short_signals=list(payload.get("prior_short_signals") or []),
        prior_long_confidences=list(payload.get("prior_long_confidences") or []),
        prior_short_confidences=list(payload.get("prior_short_confidences") or []),
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
    return [{
        "receipt_id": "pre-expansion-confirmation",
        "brick_id": CONCEPT["id"],
        "kind": "classification",
        "label": "Evaluated pre-expansion confirmation gate.",
        "refs": [],
        "data": {"final_long": value.get("final_long", False), "final_short": value.get("final_short", False)},
    }]
