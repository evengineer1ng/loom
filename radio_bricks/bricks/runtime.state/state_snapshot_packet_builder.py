from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.state_snapshot_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪞",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.state_snapshot_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "snapshot", "events", "player"],
    "description": "Package the live state snapshot with team summary, recent events ring-buffer view, and player league stats.",
}


def build_state_snapshot_packet(
    team: list[dict[str, Any]] | None,
    recent_events: list[dict[str, Any]] | None,
    player_rating: float,
    player_wins: int,
    player_losses: int,
) -> dict[str, Any]:
    return {
        "team": [dict(item) for item in (team or [])],
        "recent_events": [dict(item) for item in (recent_events or [])],
        "player_rating": float(player_rating),
        "player_wins": int(player_wins),
        "player_losses": int(player_losses),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_state_snapshot_packet(
        team=list(payload.get("team") or []),
        recent_events=list(payload.get("recent_events") or []),
        player_rating=float(payload.get("player_rating") or 0.0),
        player_wins=int(payload.get("player_wins") or 0),
        player_losses=int(payload.get("player_losses") or 0),
    )
    output_packet = {
        "packet_type": "runtime.state_response.v1",
        "packet_version": "runtime.state_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "state-snapshot-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built state-snapshot packet.",
        "refs": [],
        "data": {"team_size": len(value.get("team", [])), "recent_event_count": len(value.get("recent_events", []))},
    }]
