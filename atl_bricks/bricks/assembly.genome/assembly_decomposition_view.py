from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.genome.assembly_decomposition_view",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["assembly.catalog_request.v1"],
    "outputs": ["assembly.catalog_response.v1"],
    "requires": [],
    "provides": ["assembly.assembly_decomposition_view"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "decomposition", "view"],
    "description": "Build a read-only decomposition bundle for one assembly plus its resolved organs and artifact.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    if "assembly" not in payload:
        return [{"code": "missing_assembly", "message": "payload.assembly is required."}]
    return []


def assembly_decomposition_view(
    assembly: dict[str, Any] | None,
    entry_genome: dict[str, Any] | None,
    exit_genome: dict[str, Any] | None,
    management_genome: dict[str, Any] | None,
    compiled_artifact: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if not assembly:
        return None
    return {
        "assembly": assembly,
        "entry_genome": entry_genome,
        "exit_genome": exit_genome,
        "management_genome": management_genome,
        "compiled_artifact": compiled_artifact,
        "self_paired": bool(assembly.get("self_paired")),
    }


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    value = assembly_decomposition_view(
        payload.get("assembly"),
        payload.get("entry_genome"),
        payload.get("exit_genome"),
        payload.get("management_genome"),
        payload.get("compiled_artifact"),
    )
    output_packet = {
        "packet_type": "assembly.catalog_response.v1",
        "packet_version": "assembly.catalog_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "assembly-decomposition-view-built",
        "brick_id": CONCEPT["id"],
        "kind": "view_build",
        "label": "Built assembly decomposition view.",
        "refs": [],
        "data": {"has_value": bool(output_packet["payload"])},
    }]
