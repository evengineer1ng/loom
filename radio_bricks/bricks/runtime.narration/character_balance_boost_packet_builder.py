from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.narration.character_balance_boost_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "⚡",
    "deterministic": True,
    "inputs": ["runtime.narration_request.v1"],
    "outputs": ["runtime.narration_response.v1"],
    "requires": [],
    "provides": ["runtime.character_balance_boost_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "narration", "character", "balance", "boost"],
    "description": "Package underused-character balancing math with expected share, actual share, deficit, and resulting selection boost.",
}


def build_character_balance_boost_packet(
    character: str,
    total_utterances: int,
    character_count: int,
    actual_percent: float,
    expected_percent: float,
    deficit: float,
    boost: float,
) -> dict[str, Any]:
    return {
        "character": str(character),
        "total_utterances": int(total_utterances),
        "character_count": int(character_count),
        "actual_percent": float(actual_percent),
        "expected_percent": float(expected_percent),
        "deficit": float(deficit),
        "boost": float(boost),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_character_balance_boost_packet(
        character=str(payload.get("character") or ""),
        total_utterances=int(payload.get("total_utterances") or 0),
        character_count=int(payload.get("character_count") or 0),
        actual_percent=float(payload.get("actual_percent") or 0.0),
        expected_percent=float(payload.get("expected_percent") or 0.0),
        deficit=float(payload.get("deficit") or 0.0),
        boost=float(payload.get("boost") or 0.0),
    )
    output_packet = {
        "packet_type": "runtime.narration_response.v1",
        "packet_version": "runtime.narration_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "character-balance-boost-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built character-balance boost packet.",
        "refs": [],
        "data": {
            "character": value.get("character", ""),
            "deficit": value.get("deficit", 0.0),
            "boost": value.get("boost", 0.0),
        },
    }]
