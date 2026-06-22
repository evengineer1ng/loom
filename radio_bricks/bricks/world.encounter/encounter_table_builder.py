from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.encounter.encounter_table_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🌾",
    "deterministic": True,
    "inputs": ["world.encounter_request.v1"],
    "outputs": ["world.encounter_response.v1"],
    "requires": [],
    "provides": ["world.encounter_table_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "encounter", "table", "rarity", "node"],
    "description": "Package a node encounter table with rarity-tiered slots plus apex and anomaly caps.",
}


def build_encounter_table_packet(
    node_id: str,
    common_slots: list[str] | None,
    uncommon_slots: list[str] | None,
    rare_slots: list[str] | None,
    elite_slots: list[str] | None,
    apex_slot: str | None = None,
    anomaly_slot: str | None = None,
) -> dict[str, Any]:
    return {
        "node_id": node_id,
        "common_slots": list(common_slots or []),
        "uncommon_slots": list(uncommon_slots or []),
        "rare_slots": list(rare_slots or []),
        "elite_slots": list(elite_slots or []),
        "apex_slot": apex_slot,
        "anomaly_slot": anomaly_slot,
        "all_species": [*list(common_slots or []), *list(uncommon_slots or []), *list(rare_slots or []), *list(elite_slots or []), *([apex_slot] if apex_slot else []), *([anomaly_slot] if anomaly_slot else [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_encounter_table_packet(
        node_id=str(payload.get("node_id") or ""),
        common_slots=list(payload.get("common_slots") or []),
        uncommon_slots=list(payload.get("uncommon_slots") or []),
        rare_slots=list(payload.get("rare_slots") or []),
        elite_slots=list(payload.get("elite_slots") or []),
        apex_slot=payload.get("apex_slot"),
        anomaly_slot=payload.get("anomaly_slot"),
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
        "receipt_id": "encounter-table-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built encounter-table packet.",
        "refs": [],
        "data": {"node_id": value.get("node_id", ""), "species_count": len(value.get("all_species", []))},
    }]
