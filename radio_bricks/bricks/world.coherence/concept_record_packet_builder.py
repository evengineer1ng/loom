from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.coherence.concept_record_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧠",
    "deterministic": True,
    "inputs": ["world.coherence_request.v1"],
    "outputs": ["world.coherence_response.v1"],
    "requires": [],
    "provides": ["world.concept_record_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "coherence", "forkuniverse", "concept", "record"],
    "description": "Package a ForkUniverse ontology concept record with effects, threads, predictions, surfaces, coefficients, and tags.",
}


def build_concept_record_packet(
    concept_id: str,
    label: str,
    category: str,
    description: str,
    affects: list[str] | None,
    creates_events: list[str] | None,
    creates_threads: list[str] | None,
    creates_predictions: list[str] | None,
    decays_with: list[str] | None,
    intensifies_with: list[str] | None,
    resolution_modes: list[str] | None,
    failure_modes: list[str] | None,
    radio_surfaces: list[str] | None,
    default_coefficients: dict[str, float] | None,
    tags: list[str] | None,
) -> dict[str, Any]:
    return {
        "concept_id": concept_id,
        "label": label,
        "category": category,
        "description": description,
        "affects": list(affects or []),
        "creates_events": list(creates_events or []),
        "creates_threads": list(creates_threads or []),
        "creates_predictions": list(creates_predictions or []),
        "decays_with": list(decays_with or []),
        "intensifies_with": list(intensifies_with or []),
        "resolution_modes": list(resolution_modes or []),
        "failure_modes": list(failure_modes or []),
        "radio_surfaces": list(radio_surfaces or []),
        "default_coefficients": {str(key): float(value) for key, value in (default_coefficients or {}).items()},
        "tags": list(tags or []),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_concept_record_packet(
        concept_id=str(payload.get("concept_id") or ""),
        label=str(payload.get("label") or ""),
        category=str(payload.get("category") or ""),
        description=str(payload.get("description") or ""),
        affects=list(payload.get("affects") or []),
        creates_events=list(payload.get("creates_events") or []),
        creates_threads=list(payload.get("creates_threads") or []),
        creates_predictions=list(payload.get("creates_predictions") or []),
        decays_with=list(payload.get("decays_with") or []),
        intensifies_with=list(payload.get("intensifies_with") or []),
        resolution_modes=list(payload.get("resolution_modes") or []),
        failure_modes=list(payload.get("failure_modes") or []),
        radio_surfaces=list(payload.get("radio_surfaces") or []),
        default_coefficients=dict(payload.get("default_coefficients") or {}),
        tags=list(payload.get("tags") or []),
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
        "receipt_id": "concept-record-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built concept-record packet.",
        "refs": [],
        "data": {"concept_id": value.get("concept_id", ""), "tag_count": len(value.get("tags", []))},
    }]
