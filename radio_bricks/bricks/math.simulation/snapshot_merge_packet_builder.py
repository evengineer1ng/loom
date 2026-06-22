from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.simulation.snapshot_merge_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧬",
    "deterministic": True,
    "inputs": ["math.simulation_request.v1"],
    "outputs": ["math.simulation_response.v1"],
    "requires": [],
    "provides": ["math.snapshot_merge_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "simulation", "snapshot", "merge", "pokemon"],
    "description": "Package a deep-merged snapshot result from base and patch dictionaries for Pokemon bridge runtime composition.",
}


def build_snapshot_merge_packet(base: dict[str, Any] | None, patch: dict[str, Any] | None, merged: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "base": dict(base or {}),
        "patch": dict(patch or {}),
        "merged": dict(merged or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_snapshot_merge_packet(
        base=dict(payload.get("base") or {}),
        patch=dict(payload.get("patch") or {}),
        merged=dict(payload.get("merged") or {}),
    )
    output_packet = {
        "packet_type": "math.simulation_response.v1",
        "packet_version": "math.simulation_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "snapshot-merge-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built snapshot merge packet.",
        "refs": [],
        "data": {
            "base_keys": len(value.get("base", {})),
            "patch_keys": len(value.get("patch", {})),
            "merged_keys": len(value.get("merged", {})),
        },
    }]
