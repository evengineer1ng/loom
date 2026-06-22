from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.terminal.puck_websocket_session_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🔌",
    "deterministic": True,
    "inputs": ["runtime.terminal_request.v1"],
    "outputs": ["runtime.terminal_response.v1"],
    "requires": [],
    "provides": ["runtime.puck_websocket_session_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "terminal", "puck", "websocket", "session"],
    "description": "Package the puck WebSocket session contract with registration, interaction, ping/pong, and disconnect handling.",
}


def build_puck_websocket_session_packet(
    path: str,
    accepted: bool,
    register_payload: dict[str, Any] | None,
    interact_payload: dict[str, Any] | None,
    ping_type: str,
    pong_type: str,
    unregister_on_disconnect: bool,
) -> dict[str, Any]:
    return {
        "path": path,
        "accepted": bool(accepted),
        "register_payload": dict(register_payload or {}),
        "interact_payload": dict(interact_payload or {}),
        "ping_type": ping_type,
        "pong_type": pong_type,
        "unregister_on_disconnect": bool(unregister_on_disconnect),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_puck_websocket_session_packet(
        path=str(payload.get("path") or "/ws/puck"),
        accepted=bool(payload.get("accepted", True)),
        register_payload=dict(payload.get("register_payload") or {}),
        interact_payload=dict(payload.get("interact_payload") or {}),
        ping_type=str(payload.get("ping_type") or "ping"),
        pong_type=str(payload.get("pong_type") or "pong"),
        unregister_on_disconnect=bool(payload.get("unregister_on_disconnect", True)),
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
        "receipt_id": "puck-websocket-session-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built puck WebSocket session packet.",
        "refs": [],
        "data": {"path": value.get("path", ""), "accepted": value.get("accepted", False)},
    }]
