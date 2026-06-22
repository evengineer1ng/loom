from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.coherence.concept_registry_merge_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧬",
    "deterministic": True,
    "inputs": ["world.coherence_request.v1"],
    "outputs": ["world.coherence_response.v1"],
    "requires": [],
    "provides": ["world.concept_registry_merge_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "coherence", "forkuniverse", "registry", "merge"],
    "description": "Package a concept-registry merge result with replacement policy and the ordered merged concept rows.",
}


def build_concept_registry_merge_packet(
    registry_id: str,
    replace_existing: bool,
    concepts: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "registry_id": registry_id,
        "replace_existing": bool(replace_existing),
        "concepts": [dict(item) for item in (concepts or [])],
        "count": len(concepts or []),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_concept_registry_merge_packet(
        registry_id=str(payload.get("registry_id") or ""),
        replace_existing=bool(payload.get("replace_existing")),
        concepts=list(payload.get("concepts") or []),
    )
    output_packet = {
        "packet_type": "world.coherence_response.v1",
        "packet_version": "world.coherence_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "concept-registry-merge-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built concept-registry merge packet.",
        "refs": [],
        "data": {"registry_id": value.get("registry_id", ""), "count": value.get("count", 0)},
    }]
