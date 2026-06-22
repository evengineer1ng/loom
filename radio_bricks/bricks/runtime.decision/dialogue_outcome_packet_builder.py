from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.decision.dialogue_outcome_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🗣️",
    "deterministic": True,
    "inputs": ["runtime.decision_request.v1"],
    "outputs": ["runtime.decision_response.v1"],
    "requires": [],
    "provides": ["runtime.dialogue_outcome_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "decision", "dialogue", "credibility", "standing"],
    "description": "Package dialogue stance outcomes with credibility, faction-standing shifts, and the emitted event window.",
}


def build_dialogue_outcome_packet(
    ok: bool,
    stance: str,
    label: str,
    credibility: float,
    standing_shifts: dict[str, float] | None,
    faction_standings: dict[str, float] | None,
    events: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "ok": bool(ok),
        "stance": stance,
        "label": label,
        "credibility": float(credibility),
        "standing_shifts": {str(key): float(value) for key, value in (standing_shifts or {}).items()},
        "faction_standings": {str(key): float(value) for key, value in (faction_standings or {}).items()},
        "events": [dict(item) for item in (events or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_dialogue_outcome_packet(
        ok=bool(payload.get("ok")),
        stance=str(payload.get("stance") or ""),
        label=str(payload.get("label") or ""),
        credibility=float(payload.get("credibility") or 0.0),
        standing_shifts=dict(payload.get("standing_shifts") or {}),
        faction_standings=dict(payload.get("faction_standings") or {}),
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
        "receipt_id": "dialogue-outcome-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built dialogue-outcome packet.",
        "refs": [],
        "data": {"stance": value.get("stance", ""), "credibility": value.get("credibility", 0.0)},
    }]
