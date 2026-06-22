from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.compiled_package_hydration_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🫗",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.compiled_package_hydration_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "hydration", "compiled-package", "forkuniverse"],
    "description": "Package the one-way hydration of a compiled world package into authoritative time, coefficients, actors, institutions, threads, predictions, and memory.",
}


def build_compiled_package_hydration_packet(
    universe_id: str,
    canonical_seed: str,
    coefficient_overrides: dict[str, Any] | None,
    table_counts: dict[str, Any] | None,
    hydrated_state_counts: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "universe_id": str(universe_id),
        "canonical_seed": str(canonical_seed),
        "coefficient_overrides": dict(coefficient_overrides or {}),
        "table_counts": dict(table_counts or {}),
        "hydrated_state_counts": dict(hydrated_state_counts or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_compiled_package_hydration_packet(
        universe_id=str(payload.get("universe_id") or ""),
        canonical_seed=str(payload.get("canonical_seed") or ""),
        coefficient_overrides=dict(payload.get("coefficient_overrides") or {}),
        table_counts=dict(payload.get("table_counts") or {}),
        hydrated_state_counts=dict(payload.get("hydrated_state_counts") or {}),
    )
    output_packet = {
        "packet_type": "runtime.state_response.v1",
        "packet_version": "runtime.state_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "compiled-package-hydration-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built compiled-package hydration packet.",
        "refs": [],
        "data": {
            "universe_id": value.get("universe_id", ""),
            "table_groups": len(value.get("table_counts", {})),
            "hydrated_groups": len(value.get("hydrated_state_counts", {})),
        },
    }]
