from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.save.saved_creature_payload_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧬",
    "deterministic": True,
    "inputs": ["runtime.save_request.v1"],
    "outputs": ["runtime.save_response.v1"],
    "requires": [],
    "provides": ["runtime.saved_creature_payload"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "save", "creature", "genes", "payload"],
    "description": "Package a saved creature payload with identity, progression stats, and nested genetic profile data.",
}


def build_saved_creature_payload(
    instance_id: str,
    species_id: str,
    nickname: str,
    level: int,
    xp: int,
    fatigue: float,
    loyalty: float,
    temperament: float,
    adaptation_drift: float,
    current_hp: int,
    genes: dict[str, Any] | None,
) -> dict[str, Any]:
    gene_payload = dict(genes or {})
    gene_payload["stat_genes"] = list(gene_payload.get("stat_genes") or [])
    gene_payload["type_genes"] = list(gene_payload.get("type_genes") or [])
    gene_payload["mutation_flags"] = list(gene_payload.get("mutation_flags") or [])
    gene_payload["expression_level"] = float(gene_payload.get("expression_level") or 0.0)
    return {
        "instance_id": instance_id,
        "species_id": species_id,
        "nickname": nickname,
        "level": int(level),
        "xp": int(xp),
        "fatigue": float(fatigue),
        "loyalty": float(loyalty),
        "temperament": float(temperament),
        "adaptation_drift": float(adaptation_drift),
        "current_hp": int(current_hp),
        "genes": gene_payload,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_saved_creature_payload(
        instance_id=str(payload.get("instance_id") or ""),
        species_id=str(payload.get("species_id") or ""),
        nickname=str(payload.get("nickname") or ""),
        level=int(payload.get("level") or 0),
        xp=int(payload.get("xp") or 0),
        fatigue=float(payload.get("fatigue") or 0.0),
        loyalty=float(payload.get("loyalty") or 0.0),
        temperament=float(payload.get("temperament") or 0.0),
        adaptation_drift=float(payload.get("adaptation_drift") or 0.0),
        current_hp=int(payload.get("current_hp") or 0),
        genes=dict(payload.get("genes") or {}),
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
        "receipt_id": "saved-creature-payload",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built saved-creature payload.",
        "refs": [],
        "data": {"instance_id": value.get("instance_id", ""), "species_id": value.get("species_id", "")},
    }]
