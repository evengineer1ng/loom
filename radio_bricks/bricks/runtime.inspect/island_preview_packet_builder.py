from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.island_preview_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🛰️",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.island_preview_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "inspect", "preview", "island", "seed"],
    "description": "Package a fast island preview from seed without full initialization, including climate, node count, base tier, and active types.",
}


def build_island_preview_packet(
    seed: int,
    name: str,
    climate: str,
    node_count: int,
    base_tier: str,
    active_types: list[str] | None,
    error: str = "",
) -> dict[str, Any]:
    packet = {
        "seed": int(seed),
        "name": name,
        "climate": climate,
        "node_count": int(node_count),
        "base_tier": base_tier,
        "active_types": list(active_types or []),
    }
    if error:
        packet["error"] = error
    return packet


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_island_preview_packet(
        seed=int(payload.get("seed") or 0),
        name=str(payload.get("name") or ""),
        climate=str(payload.get("climate") or ""),
        node_count=int(payload.get("node_count") or 0),
        base_tier=str(payload.get("base_tier") or ""),
        active_types=list(payload.get("active_types") or []),
        error=str(payload.get("error") or ""),
    )
    output_packet = {
        "packet_type": "runtime.inspect_response.v1",
        "packet_version": "runtime.inspect_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "island-preview-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built island-preview packet.",
        "refs": [],
        "data": {"seed": value.get("seed", 0), "node_count": value.get("node_count", 0)},
    }]
