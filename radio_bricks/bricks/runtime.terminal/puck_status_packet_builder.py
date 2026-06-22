from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.terminal.puck_status_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📟",
    "deterministic": True,
    "inputs": ["runtime.terminal_request.v1"],
    "outputs": ["runtime.terminal_response.v1"],
    "requires": [],
    "provides": ["runtime.puck_status_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "terminal", "puck", "device", "status"],
    "description": "Package puck-manager status with initialization truth, connected count, and per-puck details.",
}


def build_puck_status_packet(
    ok: bool,
    connected: int,
    pucks: list[dict[str, Any]] | None,
    error: str = "",
) -> dict[str, Any]:
    packet = {
        "ok": bool(ok),
        "connected": int(connected),
        "pucks": [dict(item) for item in (pucks or [])],
    }
    if error:
        packet["error"] = error
    return packet


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_puck_status_packet(
        ok=bool(payload.get("ok")),
        connected=int(payload.get("connected") or 0),
        pucks=list(payload.get("pucks") or []),
        error=str(payload.get("error") or ""),
    )
    output_packet = {
        "packet_type": "runtime.terminal_response.v1",
        "packet_version": "runtime.terminal_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "puck-status-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built puck-status packet.",
        "refs": [],
        "data": {"ok": value.get("ok", False), "connected": value.get("connected", 0)},
    }]
