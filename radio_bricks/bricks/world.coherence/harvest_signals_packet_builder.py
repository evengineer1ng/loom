from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "world.coherence.harvest_signals_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🛰",
    "deterministic": True,
    "inputs": ["world.coherence_request.v1"],
    "outputs": ["world.coherence_response.v1"],
    "requires": [],
    "provides": ["world.harvest_signals_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["world", "coherence", "forkuniverse", "harvest", "signals"],
    "description": "Package harvested ontology signals from dictionary and concept-network sources before they are normalized into a concept record.",
}


def build_harvest_signals_packet(
    word: str,
    definitions: list[str] | None,
    examples: list[str] | None,
    synonyms: list[str] | None,
    antonyms: list[str] | None,
    causes: list[str] | None,
    subevents: list[str] | None,
    desires: list[str] | None,
    related: list[str] | None,
    locations: list[str] | None,
    used_for: list[str] | None,
) -> dict[str, Any]:
    return {
        "word": word,
        "definitions": list(definitions or []),
        "examples": list(examples or []),
        "synonyms": list(synonyms or []),
        "antonyms": list(antonyms or []),
        "causes": list(causes or []),
        "subevents": list(subevents or []),
        "desires": list(desires or []),
        "related": list(related or []),
        "locations": list(locations or []),
        "used_for": list(used_for or []),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_harvest_signals_packet(
        word=str(payload.get("word") or ""),
        definitions=list(payload.get("definitions") or []),
        examples=list(payload.get("examples") or []),
        synonyms=list(payload.get("synonyms") or []),
        antonyms=list(payload.get("antonyms") or []),
        causes=list(payload.get("causes") or []),
        subevents=list(payload.get("subevents") or []),
        desires=list(payload.get("desires") or []),
        related=list(payload.get("related") or []),
        locations=list(payload.get("locations") or []),
        used_for=list(payload.get("used_for") or []),
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
        "receipt_id": "harvest-signals-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built harvest-signals packet.",
        "refs": [],
        "data": {"word": value.get("word", ""), "definition_count": len(value.get("definitions", []))},
    }]
