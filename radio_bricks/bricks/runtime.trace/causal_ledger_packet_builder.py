from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.trace.causal_ledger_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪵",
    "deterministic": True,
    "inputs": ["runtime.trace_request.v1"],
    "outputs": ["runtime.trace_response.v1"],
    "requires": [],
    "provides": ["runtime.causal_ledger_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "trace", "ledger", "causal"],
    "description": "Package the append-only ForkUniverse causal ledger as an ordered world-event record.",
}


def build_causal_ledger_packet(events: list[dict[str, Any]] | None) -> dict[str, Any]:
    rows = [dict(item) for item in (events or [])]
    return {"events": rows, "count": len(rows)}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_causal_ledger_packet(events=list(payload.get("events") or []))
    output_packet = {
        "packet_type": "runtime.trace_response.v1",
        "packet_version": "runtime.trace_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "causal-ledger-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built causal-ledger packet.",
        "refs": [],
        "data": {"count": value.get("count", 0)},
    }]
