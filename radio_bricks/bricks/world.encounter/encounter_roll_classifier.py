from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.encounter.encounter_roll_classifier",
    "kind": "classifier",
    "version": "0.1.0",
    "emoji": "🎲",
    "deterministic": True,
    "inputs": ["world.encounter_request.v1"],
    "outputs": ["world.encounter_response.v1"],
    "requires": [],
    "provides": ["world.encounter_roll_classification"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "encounter", "roll", "rarity", "classifier"],
    "description": "Classify which encounter rarity band a Neikos roll resolves into before species selection.",
}


def classify_encounter_roll(roll: float, has_anomaly: bool, has_apex: bool, elite_count: int, rare_count: int, uncommon_count: int, common_count: int) -> dict[str, Any]:
    rarity = "none"
    if roll < 0.02 and has_anomaly:
        rarity = "anomaly"
    elif roll < 0.05 and has_apex:
        rarity = "apex"
    elif roll < 0.15 and elite_count > 0:
        rarity = "elite"
    elif roll < 0.30 and rare_count > 0:
        rarity = "rare"
    elif roll < 0.55 and uncommon_count > 0:
        rarity = "uncommon"
    elif common_count > 0:
        rarity = "common"
    return {
        "roll": float(roll),
        "selected_rarity": rarity,
        "has_anomaly": bool(has_anomaly),
        "has_apex": bool(has_apex),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = classify_encounter_roll(
        roll=float(payload.get("roll") or 0.0),
        has_anomaly=bool(payload.get("has_anomaly", False)),
        has_apex=bool(payload.get("has_apex", False)),
        elite_count=int(payload.get("elite_count") or 0),
        rare_count=int(payload.get("rare_count") or 0),
        uncommon_count=int(payload.get("uncommon_count") or 0),
        common_count=int(payload.get("common_count") or 0),
    )
    output_packet = {
        "packet_type": "world.encounter_response.v1",
        "packet_version": "world.encounter_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "encounter-roll-classification",
        "brick_id": CONCEPT["id"],
        "kind": "classify",
        "label": "Classified encounter roll.",
        "refs": [],
        "data": {"selected_rarity": value.get("selected_rarity", "none")},
    }]
