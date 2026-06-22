from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.trace.causal_source_trace_reader",
    "kind": "reader",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.trace_request.v1"],
    "outputs": ["runtime.trace_response.v1"],
    "requires": [],
    "provides": ["runtime.causal_source_trace"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "trace", "causal", "source"],
    "description": "Collect all causal effects emitted by a single source id.",
}


def build_causal_source_trace(edges: list[dict[str, Any]] | None, source_id: str) -> dict[str, Any]:
    rows = [dict(edge) for edge in (edges or []) if str(dict(edge).get("source_id") or "") == source_id]
    rows.sort(key=lambda row: int(row.get("tick") or 0))
    return {"source_id": source_id, "edges": rows, "edge_count": len(rows)}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_causal_source_trace(
        edges=list(payload.get("edges") or []),
        source_id=str(payload.get("source_id") or ""),
    )
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
        "receipt_id": "causal-source-trace",
        "brick_id": CONCEPT["id"],
        "kind": "read",
        "label": "Built causal source trace.",
        "refs": [],
        "data": {"edge_count": value.get("edge_count", 0)},
    }]
