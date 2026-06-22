from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.geopolitics.promotion_transition_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🚀",
    "deterministic": True,
    "inputs": ["world.geopolitics_request.v1"],
    "outputs": ["world.geopolitics_response.v1"],
    "requires": [],
    "provides": ["world.promotion_transition_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "geopolitics", "promotion", "transition", "tracked"],
    "description": "Package a Deep Field to tracked-kingdom promotion transition, including rank, importance, and seeded era context.",
}


def build_promotion_transition_packet(
    civ_id: str,
    name: str,
    tick: int,
    importance: float,
    rank: int,
    era_flag: str,
    restored_from_archive: bool,
    displaced_kingdom_id: str = "",
) -> dict[str, Any]:
    return {
        "civ_id": civ_id,
        "name": name,
        "tick": int(tick),
        "importance": float(importance),
        "rank": int(rank),
        "era_flag": era_flag,
        "restored_from_archive": bool(restored_from_archive),
        "displaced_kingdom_id": displaced_kingdom_id,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_promotion_transition_packet(
        civ_id=str(payload.get("civ_id") or ""),
        name=str(payload.get("name") or ""),
        tick=int(payload.get("tick") or 0),
        importance=float(payload.get("importance") or 0.0),
        rank=int(payload.get("rank") or 0),
        era_flag=str(payload.get("era_flag") or ""),
        restored_from_archive=bool(payload.get("restored_from_archive", False)),
        displaced_kingdom_id=str(payload.get("displaced_kingdom_id") or ""),
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
        "receipt_id": "promotion-transition-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built promotion transition packet.",
        "refs": [],
        "data": {"civ_id": value.get("civ_id", ""), "restored_from_archive": value.get("restored_from_archive", False)},
    }]
