from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.terminal.puck_interaction_bridge_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧲",
    "deterministic": True,
    "inputs": ["runtime.terminal_request.v1"],
    "outputs": ["runtime.terminal_response.v1"],
    "requires": [],
    "provides": ["runtime.puck_interaction_bridge_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "terminal", "puck", "interaction", "bridge"],
    "description": "Package the puck-manager interaction bridge from registered puck ids to node ids and interaction callbacks.",
}


def build_puck_interaction_bridge_packet(
    puck_id: str,
    node_id: str,
    action: str,
    loop_attached: bool,
) -> dict[str, Any]:
    return {
        "puck_id": puck_id,
        "node_id": node_id,
        "action": action,
        "loop_attached": bool(loop_attached),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_puck_interaction_bridge_packet(
        puck_id=str(payload.get("puck_id") or ""),
        node_id=str(payload.get("node_id") or ""),
        action=str(payload.get("action") or "interact"),
        loop_attached=bool(payload.get("loop_attached")),
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
        "receipt_id": "puck-interaction-bridge-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built puck-interaction bridge packet.",
        "refs": [],
        "data": {"puck_id": value.get("puck_id", ""), "action": value.get("action", "")},
    }]
