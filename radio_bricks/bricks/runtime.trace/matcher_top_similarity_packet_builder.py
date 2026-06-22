from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.trace.matcher_top_similarity_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🔭",
    "deterministic": True,
    "inputs": ["runtime.trace_request.v1"],
    "outputs": ["runtime.trace_response.v1"],
    "requires": [],
    "provides": ["runtime.matcher_top_similarity_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "trace", "matcher", "similarity", "ranking"],
    "description": "Package top similarity rows for matcher debugging across entry, active, and release anchor scores.",
}


def build_matcher_top_similarity_packet(rows: list[dict[str, Any]] | None) -> dict[str, Any]:
    normalized_rows = []
    for row in rows or []:
        normalized_rows.append({
            "label": str(row.get("label") or ""),
            "entry_similarity": float(row.get("entry_similarity") or 0.0),
            "active_similarity": float(row.get("active_similarity") or 0.0),
            "release_similarity": float(row.get("release_similarity") or 0.0),
        })
    return {"rows": normalized_rows}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_matcher_top_similarity_packet(rows=list(payload.get("rows") or []))
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
        "receipt_id": "matcher-top-similarity-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built matcher top-similarity packet.",
        "refs": [],
        "data": {
            "row_count": len(value.get("rows", [])),
        },
    }]
