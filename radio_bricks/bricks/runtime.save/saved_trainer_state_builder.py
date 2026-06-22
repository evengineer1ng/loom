from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.save.saved_trainer_state_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🏅",
    "deterministic": True,
    "inputs": ["runtime.save_request.v1"],
    "outputs": ["runtime.save_response.v1"],
    "requires": [],
    "provides": ["runtime.saved_trainer_state"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "save", "trainer", "rating", "league"],
    "description": "Package saved trainer state preserving rating, wins, and losses across regenerated islands.",
}


def build_saved_trainer_state(
    trainer_id: str,
    rating: float,
    wins: int,
    losses: int,
) -> dict[str, Any]:
    return {
        "trainer_id": trainer_id,
        "rating": float(rating),
        "wins": int(wins),
        "losses": int(losses),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_saved_trainer_state(
        trainer_id=str(payload.get("trainer_id") or ""),
        rating=float(payload.get("rating") or 0.0),
        wins=int(payload.get("wins") or 0),
        losses=int(payload.get("losses") or 0),
    )
    output_packet = {
        "packet_type": "runtime.save_response.v1",
        "packet_version": "runtime.save_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "saved-trainer-state",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built saved-trainer state packet.",
        "refs": [],
        "data": {"trainer_id": value.get("trainer_id", ""), "rating": value.get("rating", 0.0)},
    }]
