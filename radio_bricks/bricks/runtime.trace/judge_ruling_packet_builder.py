from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.trace.judge_ruling_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "⚖️",
    "deterministic": True,
    "inputs": ["runtime.trace_request.v1"],
    "outputs": ["runtime.trace_response.v1"],
    "requires": [],
    "provides": ["runtime.judge_ruling_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "trace", "judge", "ruling", "courtroom"],
    "description": "Package a deterministic courtroom ruling with transform, status, confidence, admitted findings, unresolved points, citations, relations, and top-hit context.",
}


def build_judge_ruling_packet(
    query: str,
    focus: str,
    transform: str,
    status: str,
    confidence: float,
    admitted_findings: list[str] | None,
    related_material: list[str] | None,
    unresolved_points: list[str] | None,
    citations: list[str] | None,
    top_hit: dict[str, Any] | None,
    relations: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "query": str(query),
        "focus": str(focus),
        "transform": str(transform),
        "status": str(status),
        "confidence": float(confidence),
        "admitted_findings": [str(item) for item in (admitted_findings or [])],
        "related_material": [str(item) for item in (related_material or [])],
        "unresolved_points": [str(item) for item in (unresolved_points or [])],
        "citations": [str(item) for item in (citations or [])],
        "top_hit": dict(top_hit or {}),
        "relations": dict(relations or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_judge_ruling_packet(
        query=str(payload.get("query") or ""),
        focus=str(payload.get("focus") or ""),
        transform=str(payload.get("transform") or ""),
        status=str(payload.get("status") or ""),
        confidence=float(payload.get("confidence") or 0.0),
        admitted_findings=list(payload.get("admitted_findings") or []),
        related_material=list(payload.get("related_material") or []),
        unresolved_points=list(payload.get("unresolved_points") or []),
        citations=list(payload.get("citations") or []),
        top_hit=dict(payload.get("top_hit") or {}),
        relations=dict(payload.get("relations") or {}),
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
        "receipt_id": "judge-ruling-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built judge ruling packet.",
        "refs": [],
        "data": {
            "transform": value.get("transform", ""),
            "status": value.get("status", ""),
            "citation_count": len(value.get("citations", [])),
        },
    }]
