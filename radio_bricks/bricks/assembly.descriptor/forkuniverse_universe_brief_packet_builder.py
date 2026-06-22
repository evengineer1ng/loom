from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.descriptor.forkuniverse_universe_brief_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📜",
    "deterministic": True,
    "inputs": ["assembly.descriptor_request.v1"],
    "outputs": ["assembly.descriptor_response.v1"],
    "requires": [],
    "provides": ["assembly.forkuniverse_universe_brief_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "descriptor", "forkuniverse", "brief", "compiler"],
    "description": "Package the normalized ForkUniverse universe brief with seed, ruleset family, targets, pressure profile, and prompt inputs.",
}


def build_forkuniverse_universe_brief_packet(
    schema_version: str,
    ruleset_family: str,
    canonical_seed: str,
    seed_hash: str,
    execution_model: str,
    time_policy_preset: str,
    world_seconds_per_real_second: float,
    selected_ontology_domains: list[str] | None,
    population_targets: dict[str, Any] | None,
    pressure_profile: dict[str, float] | None,
    compiler_prompt_inputs: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "schema_version": schema_version,
        "ruleset_family": ruleset_family,
        "canonical_seed": canonical_seed,
        "seed_hash": seed_hash,
        "execution_model": execution_model,
        "time_policy_preset": time_policy_preset,
        "world_seconds_per_real_second": float(world_seconds_per_real_second),
        "selected_ontology_domains": list(selected_ontology_domains or []),
        "population_targets": dict(population_targets or {}),
        "pressure_profile": {str(key): float(value) for key, value in (pressure_profile or {}).items()},
        "compiler_prompt_inputs": dict(compiler_prompt_inputs or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_forkuniverse_universe_brief_packet(
        schema_version=str(payload.get("schema_version") or ""),
        ruleset_family=str(payload.get("ruleset_family") or ""),
        canonical_seed=str(payload.get("canonical_seed") or ""),
        seed_hash=str(payload.get("seed_hash") or ""),
        execution_model=str(payload.get("execution_model") or ""),
        time_policy_preset=str(payload.get("time_policy_preset") or ""),
        world_seconds_per_real_second=float(payload.get("world_seconds_per_real_second") or 0.0),
        selected_ontology_domains=list(payload.get("selected_ontology_domains") or []),
        population_targets=dict(payload.get("population_targets") or {}),
        pressure_profile=dict(payload.get("pressure_profile") or {}),
        compiler_prompt_inputs=dict(payload.get("compiler_prompt_inputs") or {}),
    )
    output_packet = {
        "packet_type": "assembly.descriptor_response.v1",
        "packet_version": "assembly.descriptor_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "forkuniverse-universe-brief-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built ForkUniverse universe-brief packet.",
        "refs": [],
        "data": {"ruleset_family": value.get("ruleset_family", ""), "selected_ontology_domains": len(value.get("selected_ontology_domains", []))},
    }]
