from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.lifecycle.expedition_status_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📈",
    "deterministic": True,
    "inputs": ["runtime.lifecycle_request.v1"],
    "outputs": ["runtime.lifecycle_response.v1"],
    "requires": [],
    "provides": ["runtime.expedition_status_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "lifecycle", "expedition", "status", "profile"],
    "description": "Package current expedition status with live island metadata and optional saved-profile summary.",
}


def build_expedition_status_packet(
    seed: int,
    tick: int,
    island_name: str,
    current_tier: str,
    ngp_run: int,
    saved_profile: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "seed": int(seed),
        "tick": int(tick),
        "island_name": island_name,
        "current_tier": current_tier,
        "ngp_run": int(ngp_run),
        "saved_profile": dict(saved_profile or {}) if saved_profile is not None else None,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_expedition_status_packet(
        seed=int(payload.get("seed") or 0),
        tick=int(payload.get("tick") or 0),
        island_name=str(payload.get("island_name") or ""),
        current_tier=str(payload.get("current_tier") or ""),
        ngp_run=int(payload.get("ngp_run") or 0),
        saved_profile=payload.get("saved_profile"),
    )
    output_packet = {
        "packet_type": "runtime.lifecycle_response.v1",
        "packet_version": "runtime.lifecycle_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "expedition-status-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built expedition-status packet.",
        "refs": [],
        "data": {"seed": value.get("seed", 0), "ngp_run": value.get("ngp_run", 0)},
    }]
