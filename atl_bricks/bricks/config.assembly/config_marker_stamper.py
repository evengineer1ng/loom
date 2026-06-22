from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "config.assembly.config_marker_stamper",
    "kind": "transformer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["config.assembly_request.v1"],
    "outputs": ["config.assembly_response.v1"],
    "requires": [],
    "provides": ["config.stamp_run_markers"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["config", "markers", "assembly"],
    "description": "Stamp portable run markers into a config payload so downstream artifacts can be matched back to a run cell.",
}


def stamp_run_markers(config: dict[str, Any] | None, strategy: str, universe: str, variant: str, overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    stamped = dict(config or {})
    stamped.update(dict(overrides or {}))
    stamped["pliers_variant"] = variant
    stamped["pliers_strategy"] = strategy
    stamped["pliers_universe"] = universe
    return stamped


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = stamp_run_markers(
        config=dict(payload.get("config") or {}),
        strategy=str(payload.get("strategy") or ""),
        universe=str(payload.get("universe") or ""),
        variant=str(payload.get("variant") or ""),
        overrides=dict(payload.get("overrides") or {}),
    )
    output_packet = {
        "packet_type": "config.assembly_response.v1",
        "packet_version": "config.assembly_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    payload = output_packet.get("payload") or {}
    return [{
        "receipt_id": "config-markers-stamped",
        "brick_id": CONCEPT["id"],
        "kind": "transformation",
        "label": "Stamped run markers into config payload.",
        "refs": [],
        "data": {
            "strategy": payload.get("pliers_strategy", ""),
            "universe": payload.get("pliers_universe", ""),
            "variant": payload.get("pliers_variant", ""),
        },
    }]
