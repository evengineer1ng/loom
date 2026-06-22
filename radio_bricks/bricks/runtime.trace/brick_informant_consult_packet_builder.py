from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.trace.brick_informant_consult_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧱",
    "deterministic": True,
    "inputs": ["runtime.trace_request.v1"],
    "outputs": ["runtime.trace_response.v1"],
    "requires": [],
    "provides": ["runtime.brick_informant_consult_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "trace", "brick", "informant", "retrieval"],
    "description": "Package a brick-informant consult with status, candidates, citations, and any missing-brick gaps surfaced by lexical tape retrieval.",
}


def build_brick_informant_consult_packet(
    query: str,
    status: str,
    confidence: float,
    candidates: list[dict[str, Any]] | None,
    citations: list[str] | None,
    gaps: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "query": str(query),
        "status": str(status),
        "confidence": float(confidence),
        "candidates": [dict(item) for item in (candidates or [])],
        "citations": [str(item) for item in (citations or [])],
        "gaps": [dict(item) for item in (gaps or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_brick_informant_consult_packet(
        query=str(payload.get("query") or ""),
        status=str(payload.get("status") or ""),
        confidence=float(payload.get("confidence") or 0.0),
        candidates=list(payload.get("candidates") or []),
        citations=list(payload.get("citations") or []),
        gaps=list(payload.get("gaps") or []),
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
        "receipt_id": "brick-informant-consult-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built brick informant consult packet.",
        "refs": [],
        "data": {
            "status": value.get("status", ""),
            "candidate_count": len(value.get("candidates", [])),
            "gap_count": len(value.get("gaps", [])),
        },
    }]
