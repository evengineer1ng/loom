from __future__ import annotations

from typing import Any
import math


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.league.rating_update_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📈",
    "deterministic": True,
    "inputs": ["runtime.league_request.v1"],
    "outputs": ["runtime.league_response.v1"],
    "requires": [],
    "provides": ["runtime.rating_update_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "league", "rating", "elo", "update"],
    "description": "Package an ELO-like trainer rating update with expected scores and post-match ratings.",
}


def build_rating_update_packet(winner_id: str, loser_id: str, winner_rating: float, loser_rating: float, k: float = 32.0) -> dict[str, Any]:
    expected_w = 1.0 / (1.0 + 10 ** ((loser_rating - winner_rating) / 400.0))
    expected_l = 1.0 - expected_w
    return {
        "winner_id": winner_id,
        "loser_id": loser_id,
        "k": float(k),
        "winner_expected": float(expected_w),
        "loser_expected": float(expected_l),
        "winner_new_rating": float(winner_rating + k * (1.0 - expected_w)),
        "loser_new_rating": float(loser_rating + k * (0.0 - expected_l)),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_rating_update_packet(
        winner_id=str(payload.get("winner_id") or ""),
        loser_id=str(payload.get("loser_id") or ""),
        winner_rating=float(payload.get("winner_rating") or 0.0),
        loser_rating=float(payload.get("loser_rating") or 0.0),
        k=float(payload.get("k") or 32.0),
    )
    output_packet = {
        "packet_type": "runtime.league_response.v1",
        "packet_version": "runtime.league_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "rating-update-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built rating-update packet.",
        "refs": [],
        "data": {"winner_id": value.get("winner_id", ""), "loser_id": value.get("loser_id", "")},
    }]
