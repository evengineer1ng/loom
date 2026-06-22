from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.trace.console_log_line_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪵",
    "deterministic": True,
    "inputs": ["runtime.trace_request.v1"],
    "outputs": ["runtime.trace_response.v1"],
    "requires": [],
    "provides": ["runtime.console_log_line_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "trace", "console", "log", "bookmark", "status"],
    "description": "Package a single Bookmark-style console log line with role, safe message text, and its candidate subtitle/readout use.",
}


def build_console_log_line_packet(
    role: str,
    message: str,
    console_safe_role: str | None = None,
    console_safe_message: str | None = None,
) -> dict[str, Any]:
    return {
        "role": str(role),
        "message": str(message),
        "console_safe_role": str(console_safe_role or role),
        "console_safe_message": str(console_safe_message or message),
        "readout_candidate": f"{str(role)}: {str(message)}".strip(),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_console_log_line_packet(
        role=str(payload.get("role") or ""),
        message=str(payload.get("message") or ""),
        console_safe_role=payload.get("console_safe_role"),
        console_safe_message=payload.get("console_safe_message"),
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
        "receipt_id": "console-log-line-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built console log-line packet.",
        "refs": [],
        "data": {
            "role": value.get("role", ""),
        },
    }]
