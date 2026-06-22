from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.trace.causal_variable_history_reader",
    "kind": "reader",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.trace_request.v1"],
    "outputs": ["runtime.trace_response.v1"],
    "requires": [],
    "provides": ["runtime.causal_variable_history"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "trace", "causal", "history"],
    "description": "Build a timeline-friendly history of mutations for a single causal variable.",
}


def build_causal_variable_history(edges: list[dict[str, Any]] | None, variable: str, tick_start: int | None = None, tick_end: int | None = None, last_n: int = 50) -> dict[str, Any]:
    rows = []
    for edge in edges or []:
        item = dict(edge)
        if str(item.get("variable") or "") != variable:
            continue
        tick = int(item.get("tick") or 0)
        if tick_start is not None and tick < int(tick_start):
            continue
        if tick_end is not None and tick > int(tick_end):
            continue
        rows.append(item)
    rows.sort(key=lambda row: int(row.get("tick") or 0))
    history = [{
        "tick": int(row.get("tick") or 0),
        "delta": float(row.get("delta") or 0.0),
        "source_type": str(row.get("source_type") or ""),
        "source_id": str(row.get("source_id") or ""),
        "metadata": dict(row.get("metadata") or {}),
    } for row in rows[-max(int(last_n), 0):]]
    return {"variable": variable, "history": history, "entry_count": len(history)}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_causal_variable_history(
        edges=list(payload.get("edges") or []),
        variable=str(payload.get("variable") or ""),
        tick_start=payload.get("tick_start"),
        tick_end=payload.get("tick_end"),
        last_n=int(payload.get("last_n") or 50),
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
        "receipt_id": "causal-variable-history",
        "brick_id": CONCEPT["id"],
        "kind": "read",
        "label": "Built causal variable history.",
        "refs": [],
        "data": {"entry_count": value.get("entry_count", 0)},
    }]
