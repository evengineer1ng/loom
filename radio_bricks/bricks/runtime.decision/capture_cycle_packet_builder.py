from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.decision.capture_cycle_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🫳",
    "deterministic": True,
    "inputs": ["runtime.decision_request.v1"],
    "outputs": ["runtime.decision_response.v1"],
    "requires": [],
    "provides": ["runtime.capture_cycle_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "decision", "capture", "release", "claim"],
    "description": "Package capture-cycle outcomes for capture, release, or claim actions with result tags, team size, and detailed event payloads.",
}


def build_capture_cycle_packet(
    action: str,
    ok: bool,
    result: str,
    detail: dict[str, Any] | None,
    team_size: int | None,
    tick: int | None,
    creatures_captured: int | None,
    events: list[dict[str, Any]] | None,
    error: str = "",
) -> dict[str, Any]:
    packet = {
        "action": action,
        "ok": bool(ok),
        "result": result,
        "detail": dict(detail or {}),
        "events": [dict(item) for item in (events or [])],
    }
    if team_size is not None:
        packet["team_size"] = int(team_size)
    if tick is not None:
        packet["tick"] = int(tick)
    if creatures_captured is not None:
        packet["creatures_captured"] = int(creatures_captured)
    if error:
        packet["error"] = error
    return packet


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_capture_cycle_packet(
        action=str(payload.get("action") or ""),
        ok=bool(payload.get("ok")),
        result=str(payload.get("result") or ""),
        detail=dict(payload.get("detail") or {}),
        team_size=payload.get("team_size"),
        tick=payload.get("tick"),
        creatures_captured=payload.get("creatures_captured"),
        events=list(payload.get("events") or []),
        error=str(payload.get("error") or ""),
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
        "receipt_id": "capture-cycle-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built capture-cycle packet.",
        "refs": [],
        "data": {"action": value.get("action", ""), "result": value.get("result", "")},
    }]
