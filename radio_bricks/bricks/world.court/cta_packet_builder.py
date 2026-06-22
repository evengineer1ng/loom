from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.court.cta_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["world.court_request.v1"],
    "outputs": ["world.court_response.v1"],
    "requires": [],
    "provides": ["world.cta_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "court", "cta", "signals"],
    "description": "Package newly generated court presence requests and environmental signals into one CTA surface.",
}


def build_cta_packet(requests: list[dict[str, Any]] | None, signals: list[dict[str, Any]] | None, tick: int) -> dict[str, Any]:
    reqs = [dict(item) for item in (requests or [])]
    sigs = [dict(item) for item in (signals or [])]
    return {
        "tick": int(tick),
        "requests": reqs,
        "signals": sigs,
        "request_count": len(reqs),
        "signal_count": len(sigs),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_cta_packet(
        requests=list(payload.get("requests") or []),
        signals=list(payload.get("signals") or []),
        tick=int(payload.get("tick") or 0),
    )
    output_packet = {
        "packet_type": "world.court_response.v1",
        "packet_version": "world.court_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "cta-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built court CTA packet.",
        "refs": [],
        "data": {"request_count": value.get("request_count", 0), "signal_count": value.get("signal_count", 0)},
    }]
