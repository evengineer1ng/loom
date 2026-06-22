from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.island_cache_build_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧮",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.island_cache_build_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "inspect", "cache", "island", "background"],
    "description": "Package the background island-cache build contract, including preview entries, build range, and ready state.",
}


def build_island_cache_build_packet(
    seed_start: int,
    seed_end: int,
    entries: list[dict[str, Any]] | None,
    cache_ready: bool,
) -> dict[str, Any]:
    return {
        "seed_start": int(seed_start),
        "seed_end": int(seed_end),
        "entries": [dict(item) for item in (entries or [])],
        "cache_ready": bool(cache_ready),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_island_cache_build_packet(
        seed_start=int(payload.get("seed_start") or 1),
        seed_end=int(payload.get("seed_end") or 100),
        entries=list(payload.get("entries") or []),
        cache_ready=bool(payload.get("cache_ready")),
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
        "receipt_id": "island-cache-build-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built island-cache build packet.",
        "refs": [],
        "data": {"seed_end": value.get("seed_end", 0), "cache_ready": value.get("cache_ready", False)},
    }]
