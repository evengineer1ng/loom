from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.producer_tuning_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎛️",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.producer_tuning_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "producer", "tuning", "config"],
    "description": "Package live producer tuning updates for pacing, queue depth, enqueue cap, temperature, tokens, and low-water thresholds.",
}


def build_producer_tuning_packet(
    producer_config: dict[str, Any] | None,
    changed_key: str,
    changed_value: Any,
    persisted_to_manifest: bool,
) -> dict[str, Any]:
    return {
        "producer_config": dict(producer_config or {}),
        "changed_key": str(changed_key),
        "changed_value": changed_value,
        "persisted_to_manifest": bool(persisted_to_manifest),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_producer_tuning_packet(
        producer_config=dict(payload.get("producer_config") or {}),
        changed_key=str(payload.get("changed_key") or ""),
        changed_value=payload.get("changed_value"),
        persisted_to_manifest=bool(payload.get("persisted_to_manifest")),
    )
    output_packet = {
        "packet_type": "runtime.binding_response.v1",
        "packet_version": "runtime.binding_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "producer-tuning-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built producer-tuning packet.",
        "refs": [],
        "data": {
            "changed_key": value.get("changed_key", ""),
            "persisted_to_manifest": value.get("persisted_to_manifest", False),
        },
    }]
