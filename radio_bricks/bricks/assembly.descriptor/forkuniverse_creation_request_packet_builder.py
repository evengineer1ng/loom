from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.descriptor.forkuniverse_creation_request_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪄",
    "deterministic": True,
    "inputs": ["assembly.descriptor_request.v1"],
    "outputs": ["assembly.descriptor_response.v1"],
    "requires": [],
    "provides": ["assembly.forkuniverse_creation_request_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "descriptor", "forkuniverse", "creation", "request"],
    "description": "Package the full ForkUniverse creation request, including premise, scale, operator mode, ontology domains, constraints, and time policy.",
}


def build_forkuniverse_creation_request_packet(
    schema_version: str,
    universe_title: str,
    premise: str,
    setting_kind: str,
    time_period: str,
    story_mode: str,
    world_scale: str,
    starting_population: int,
    seed_mode: str,
    preset_id: str,
    custom_seed: str,
    location_flavor: str,
    genre_mix: dict[str, float] | None,
    tone_mix: dict[str, float] | None,
    starting_context: str,
    operator_insert_mode: str,
    operator_role_hint: str,
    ontology_domains: list[str] | None,
    constraints: dict[str, Any] | None,
    time_policy: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "schema_version": schema_version,
        "universe_title": universe_title,
        "premise": premise,
        "setting_kind": setting_kind,
        "time_period": time_period,
        "story_mode": story_mode,
        "world_scale": world_scale,
        "starting_population": int(starting_population),
        "seed_mode": seed_mode,
        "preset_id": preset_id,
        "custom_seed": custom_seed,
        "location_flavor": location_flavor,
        "genre_mix": {str(key): float(value) for key, value in (genre_mix or {}).items()},
        "tone_mix": {str(key): float(value) for key, value in (tone_mix or {}).items()},
        "starting_context": starting_context,
        "operator_insert_mode": operator_insert_mode,
        "operator_role_hint": operator_role_hint,
        "ontology_domains": list(ontology_domains or []),
        "constraints": dict(constraints or {}),
        "time_policy": dict(time_policy or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_forkuniverse_creation_request_packet(
        schema_version=str(payload.get("schema_version") or ""),
        universe_title=str(payload.get("universe_title") or ""),
        premise=str(payload.get("premise") or ""),
        setting_kind=str(payload.get("setting_kind") or ""),
        time_period=str(payload.get("time_period") or ""),
        story_mode=str(payload.get("story_mode") or ""),
        world_scale=str(payload.get("world_scale") or ""),
        starting_population=int(payload.get("starting_population") or 0),
        seed_mode=str(payload.get("seed_mode") or ""),
        preset_id=str(payload.get("preset_id") or ""),
        custom_seed=str(payload.get("custom_seed") or ""),
        location_flavor=str(payload.get("location_flavor") or ""),
        genre_mix=dict(payload.get("genre_mix") or {}),
        tone_mix=dict(payload.get("tone_mix") or {}),
        starting_context=str(payload.get("starting_context") or ""),
        operator_insert_mode=str(payload.get("operator_insert_mode") or ""),
        operator_role_hint=str(payload.get("operator_role_hint") or ""),
        ontology_domains=list(payload.get("ontology_domains") or []),
        constraints=dict(payload.get("constraints") or {}),
        time_policy=dict(payload.get("time_policy") or {}),
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
        "receipt_id": "forkuniverse-creation-request-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built ForkUniverse creation-request packet.",
        "refs": [],
        "data": {"universe_title": value.get("universe_title", ""), "world_scale": value.get("world_scale", "")},
    }]
