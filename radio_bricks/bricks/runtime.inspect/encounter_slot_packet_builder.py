from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.encounter_slot_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎲",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.encounter_slot_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "inspect", "encounter", "rarity", "slot"],
    "description": "Package a local-intel encounter slot with rarity tier, encounter rate, and species briefs.",
}


def build_encounter_slot_packet(
    tier: str,
    encounter_rate: float,
    species: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "tier": tier,
        "encounter_rate": float(encounter_rate),
        "species": [dict(item) for item in (species or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_encounter_slot_packet(
        tier=str(payload.get("tier") or ""),
        encounter_rate=float(payload.get("encounter_rate") or 0.0),
        species=list(payload.get("species") or []),
    )
    output_packet = {
        "packet_type": "runtime.inspect_response.v1",
        "packet_version": "runtime.inspect_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "encounter-slot-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built encounter-slot packet.",
        "refs": [],
        "data": {"tier": value.get("tier", ""), "species_count": len(value.get("species", []))},
    }]
