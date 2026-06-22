from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.interpretation.field_map_derivation_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🗺️",
    "deterministic": True,
    "inputs": ["math.interpretation_request.v1"],
    "outputs": ["math.interpretation_response.v1"],
    "requires": [],
    "provides": ["math.field_map_derivation_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "interpretation", "field-map", "bucket", "heuristic"],
    "description": "Package narration-bucket field-map derivation from discovered fields, bucket hints, and optional per-source overrides.",
}


def build_field_map_derivation_packet(
    fields: dict[str, Any] | None,
    bucket_hints: dict[str, Any] | None,
    inferred_field_map: dict[str, Any] | None,
    overrides: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "fields": dict(fields or {}),
        "bucket_hints": dict(bucket_hints or {}),
        "inferred_field_map": dict(inferred_field_map or {}),
        "overrides": dict(overrides or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_field_map_derivation_packet(
        fields=dict(payload.get("fields") or {}),
        bucket_hints=dict(payload.get("bucket_hints") or {}),
        inferred_field_map=dict(payload.get("inferred_field_map") or {}),
        overrides=dict(payload.get("overrides") or {}),
    )
    output_packet = {
        "packet_type": "math.interpretation_response.v1",
        "packet_version": "math.interpretation_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "field-map-derivation-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built field-map derivation packet.",
        "refs": [],
        "data": {
            "field_count": len(value.get("fields", {})),
            "bucket_count": len(value.get("inferred_field_map", {})),
            "override_count": len(value.get("overrides", {})),
        },
    }]
