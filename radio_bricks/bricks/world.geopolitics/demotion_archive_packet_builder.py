from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.geopolitics.demotion_archive_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📦",
    "deterministic": True,
    "inputs": ["world.geopolitics_request.v1"],
    "outputs": ["world.geopolitics_response.v1"],
    "requires": [],
    "provides": ["world.demotion_archive_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "geopolitics", "demotion", "archive", "vector"],
    "description": "Package a tracked-kingdom demotion back to Deep Field, including archive preservation and synced vector fields.",
}


def build_demotion_archive_packet(
    civ_id: str,
    tick: int,
    reason: str,
    archived_state_present: bool,
    wealth_index: float,
    stability: float,
    population: float,
    military_strength: float,
    volatility: float,
    cultural_alignment: float,
    trade_dependency: float,
) -> dict[str, Any]:
    return {
        "civ_id": civ_id,
        "tick": int(tick),
        "reason": reason,
        "archived_state_present": bool(archived_state_present),
        "synced_vector": {
            "wealth_index": float(wealth_index),
            "stability": float(stability),
            "population": float(population),
            "military_strength": float(military_strength),
            "volatility": float(volatility),
            "cultural_alignment": float(cultural_alignment),
            "trade_dependency": float(trade_dependency),
        },
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_demotion_archive_packet(
        civ_id=str(payload.get("civ_id") or ""),
        tick=int(payload.get("tick") or 0),
        reason=str(payload.get("reason") or ""),
        archived_state_present=bool(payload.get("archived_state_present", False)),
        wealth_index=float(payload.get("wealth_index") or 0.0),
        stability=float(payload.get("stability") or 0.0),
        population=float(payload.get("population") or 0.0),
        military_strength=float(payload.get("military_strength") or 0.0),
        volatility=float(payload.get("volatility") or 0.0),
        cultural_alignment=float(payload.get("cultural_alignment") or 0.0),
        trade_dependency=float(payload.get("trade_dependency") or 0.0),
    )
    output_packet = {
        "packet_type": "world.geopolitics_response.v1",
        "packet_version": "world.geopolitics_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "demotion-archive-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built demotion archive packet.",
        "refs": [],
        "data": {"civ_id": value.get("civ_id", ""), "reason": value.get("reason", "")},
    }]
