from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.decision.encounter_result_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "👾",
    "deterministic": True,
    "inputs": ["runtime.decision_request.v1"],
    "outputs": ["runtime.decision_response.v1"],
    "requires": [],
    "provides": ["runtime.encounter_result_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "decision", "encounter", "result", "wild"],
    "description": "Package an encounter action result with surfaced encounter data or explicit no-encounter outcome plus action event context.",
}


def build_encounter_result_packet(
    ok: bool,
    tick: int | None,
    player_location: str | None,
    encounter: dict[str, Any] | None,
    no_encounter: bool,
    message: str,
    events: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    packet = {
        "ok": bool(ok),
        "no_encounter": bool(no_encounter),
        "message": message,
        "events": [dict(item) for item in (events or [])],
    }
    if tick is not None:
        packet["tick"] = int(tick)
    if player_location is not None:
        packet["player_location"] = player_location
    if encounter is not None:
        packet["encounter"] = dict(encounter)
    return packet


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_encounter_result_packet(
        ok=bool(payload.get("ok")),
        tick=payload.get("tick"),
        player_location=payload.get("player_location"),
        encounter=payload.get("encounter"),
        no_encounter=bool(payload.get("no_encounter")),
        message=str(payload.get("message") or ""),
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
        "receipt_id": "encounter-result-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built encounter-result packet.",
        "refs": [],
        "data": {"no_encounter": value.get("no_encounter", False), "has_encounter": "encounter" in value},
    }]
