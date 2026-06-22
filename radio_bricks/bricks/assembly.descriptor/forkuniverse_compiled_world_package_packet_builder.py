from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.descriptor.forkuniverse_compiled_world_package_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📦",
    "deterministic": True,
    "inputs": ["assembly.descriptor_request.v1"],
    "outputs": ["assembly.descriptor_response.v1"],
    "requires": [],
    "provides": ["assembly.forkuniverse_compiled_world_package_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "descriptor", "forkuniverse", "compiled", "package"],
    "description": "Package a compiled ForkUniverse world package with identity, brief, time policy, coefficients, world tables, and compiler fill.",
}


def build_forkuniverse_compiled_world_package_packet(
    schema_version: str,
    package_identity: dict[str, Any] | None,
    universe_brief: dict[str, Any] | None,
    time_policy: dict[str, Any] | None,
    coefficient_profile: dict[str, float] | None,
    world_tables: dict[str, Any] | None,
    compiler_fill: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "schema_version": schema_version,
        "package_identity": dict(package_identity or {}),
        "universe_brief": dict(universe_brief or {}),
        "time_policy": dict(time_policy or {}),
        "coefficient_profile": {str(key): float(value) for key, value in (coefficient_profile or {}).items()},
        "world_tables": dict(world_tables or {}),
        "compiler_fill": dict(compiler_fill or {}) if compiler_fill is not None else None,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_forkuniverse_compiled_world_package_packet(
        schema_version=str(payload.get("schema_version") or ""),
        package_identity=dict(payload.get("package_identity") or {}),
        universe_brief=dict(payload.get("universe_brief") or {}),
        time_policy=dict(payload.get("time_policy") or {}),
        coefficient_profile=dict(payload.get("coefficient_profile") or {}),
        world_tables=dict(payload.get("world_tables") or {}),
        compiler_fill=payload.get("compiler_fill"),
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
        "receipt_id": "forkuniverse-compiled-world-package-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built ForkUniverse compiled-world-package packet.",
        "refs": [],
        "data": {"table_count": len(value.get("world_tables", {})), "coefficient_count": len(value.get("coefficient_profile", {}))},
    }]
