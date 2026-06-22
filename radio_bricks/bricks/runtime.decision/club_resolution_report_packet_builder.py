from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.decision.club_resolution_report_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪪",
    "deterministic": True,
    "inputs": ["runtime.decision_request.v1"],
    "outputs": ["runtime.decision_response.v1"],
    "requires": [],
    "provides": ["runtime.club_resolution_report_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "decision", "club", "dependency", "asks", "readiness"],
    "description": "Package a Club resolution report with readiness, resolved capabilities, asks, and missing required dependencies.",
}


def build_club_resolution_report_packet(
    ready: bool,
    resolved: dict[str, Any] | None,
    asks: list[dict[str, Any]] | None,
    missing_required: list[str] | tuple[str, ...] | None,
) -> dict[str, Any]:
    return {
        "ready": bool(ready),
        "resolved": dict(resolved or {}),
        "asks": [dict(item) for item in (asks or [])],
        "missing_required": [str(item) for item in (missing_required or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_club_resolution_report_packet(
        ready=bool(payload.get("ready")),
        resolved=dict(payload.get("resolved") or {}),
        asks=list(payload.get("asks") or []),
        missing_required=list(payload.get("missing_required") or []),
    )
    output_packet = {
        "packet_type": "runtime.decision_response.v1",
        "packet_version": "runtime.decision_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "club-resolution-report-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built Club resolution report packet.",
        "refs": [],
        "data": {
            "ready": value.get("ready", False),
            "ask_count": len(value.get("asks", [])),
            "missing_required_count": len(value.get("missing_required", [])),
        },
    }]
