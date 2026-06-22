from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.trace.token_pressure_status_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🫁",
    "deterministic": True,
    "inputs": ["runtime.trace_request.v1"],
    "outputs": ["runtime.trace_response.v1"],
    "requires": [],
    "provides": ["runtime.token_pressure_status_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "trace", "token", "pressure", "monitor"],
    "description": "Package token-pressure monitor state with warning/critical thresholds, last level, and fired callback flags.",
}


def build_token_pressure_status_packet(
    warning_threshold: float,
    critical_threshold: float,
    last_level: str,
    fired_warning: bool,
    fired_critical: bool,
) -> dict[str, Any]:
    return {
        "warning_threshold": float(warning_threshold),
        "critical_threshold": float(critical_threshold),
        "last_level": str(last_level),
        "fired_warning": bool(fired_warning),
        "fired_critical": bool(fired_critical),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_token_pressure_status_packet(
        warning_threshold=float(payload.get("warning_threshold") or 0.0),
        critical_threshold=float(payload.get("critical_threshold") or 0.0),
        last_level=str(payload.get("last_level") or ""),
        fired_warning=bool(payload.get("fired_warning")),
        fired_critical=bool(payload.get("fired_critical")),
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
        "receipt_id": "token-pressure-status-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built token-pressure status packet.",
        "refs": [],
        "data": {
            "last_level": value.get("last_level", ""),
            "warning_threshold": value.get("warning_threshold", 0.0),
        },
    }]
