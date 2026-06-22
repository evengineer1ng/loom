from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.decision.move_result_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🚶",
    "deterministic": True,
    "inputs": ["runtime.decision_request.v1"],
    "outputs": ["runtime.decision_response.v1"],
    "requires": [],
    "provides": ["runtime.move_result_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "decision", "move", "gate", "result"],
    "description": "Package move action results, including success, rejection reason, player location, player stats, and emitted events.",
}


def build_move_result_packet(
    ok: bool,
    player_location: str,
    node_name: str,
    neighbors: list[str] | None,
    error: str = "",
    player_stats: dict[str, Any] | None = None,
    events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    packet = {
        "ok": bool(ok),
        "player_location": player_location,
        "node_name": node_name,
        "neighbors": list(neighbors or []),
        "events": [dict(item) for item in (events or [])],
    }
    if error:
        packet["error"] = error
    if player_stats is not None:
        packet["player_stats"] = dict(player_stats)
    return packet


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_move_result_packet(
        ok=bool(payload.get("ok")),
        player_location=str(payload.get("player_location") or ""),
        node_name=str(payload.get("node_name") or ""),
        neighbors=list(payload.get("neighbors") or []),
        error=str(payload.get("error") or ""),
        player_stats=payload.get("player_stats"),
        events=list(payload.get("events") or []),
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
        "receipt_id": "move-result-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built move-result packet.",
        "refs": [],
        "data": {"ok": value.get("ok", False), "player_location": value.get("player_location", "")},
    }]
