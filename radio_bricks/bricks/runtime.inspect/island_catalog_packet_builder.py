from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.island_catalog_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🗺",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.island_catalog_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "inspect", "catalog", "islands", "cache"],
    "description": "Package the cached island preview catalog with partial-warmup readiness and cached-count metadata.",
}


def build_island_catalog_packet(
    islands: list[dict[str, Any]] | None,
    cache_ready: bool,
    cached_count: int,
) -> dict[str, Any]:
    return {
        "islands": [dict(item) for item in (islands or [])],
        "cache_ready": bool(cache_ready),
        "cached_count": int(cached_count),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_island_catalog_packet(
        islands=list(payload.get("islands") or []),
        cache_ready=bool(payload.get("cache_ready")),
        cached_count=int(payload.get("cached_count") or 0),
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
        "receipt_id": "island-catalog-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built island-catalog packet.",
        "refs": [],
        "data": {"cached_count": value.get("cached_count", 0), "cache_ready": value.get("cache_ready", False)},
    }]
