from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.decision.action_result_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📦",
    "deterministic": True,
    "inputs": ["runtime.decision_request.v1"],
    "outputs": ["runtime.decision_response.v1"],
    "requires": [],
    "provides": ["runtime.action_result_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "decision", "action", "result", "events"],
    "description": "Package a normalized queued-action result with top-level fields, emitted events, and action-specific summary detail.",
}


def build_action_result_packet(
    action: str,
    ok: bool,
    result: str = "",
    detail: dict[str, Any] | None = None,
    tick: int | None = None,
    player_location: str | None = None,
    team_size: int | None = None,
    events: list[dict[str, Any]] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    packet: dict[str, Any] = {
        "action": action,
        "ok": bool(ok),
        "events": [dict(item) for item in (events or [])],
        "detail": dict(detail or {}),
    }
    if result:
        packet["result"] = result
    if tick is not None:
        packet["tick"] = int(tick)
    if player_location is not None:
        packet["player_location"] = player_location
    if team_size is not None:
        packet["team_size"] = int(team_size)
    if extra:
        packet.update(dict(extra))
    return packet


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_action_result_packet(
        action=str(payload.get("action") or ""),
        ok=bool(payload.get("ok")),
        result=str(payload.get("result") or ""),
        detail=dict(payload.get("detail") or {}),
        tick=payload.get("tick"),
        player_location=payload.get("player_location"),
        team_size=payload.get("team_size"),
        events=list(payload.get("events") or []),
        extra=dict(payload.get("extra") or {}),
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
        "receipt_id": "action-result-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built action-result packet.",
        "refs": [],
        "data": {"action": value.get("action", ""), "ok": value.get("ok", False)},
    }]
