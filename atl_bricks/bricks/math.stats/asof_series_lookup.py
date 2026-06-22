from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.stats.asof_series_lookup",
    "kind": "calculator",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.series_request.v1"],
    "outputs": ["math.series_response.v1"],
    "requires": [],
    "provides": ["math.asof_lookup"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "series", "asof"],
    "description": "Return the latest series value whose key is less than or equal to a requested key.",
}


def asof_lookup(sorted_pairs: list[list[Any]] | list[tuple[Any, Any]] | None, key: Any, default: Any) -> Any:
    chosen = default
    for pair in list(sorted_pairs or []):
        if len(pair) != 2:
            continue
        pair_key, pair_value = pair[0], pair[1]
        if pair_key <= key:
            chosen = pair_value
        else:
            break
    return chosen


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = {"value": asof_lookup(list(payload.get("pairs") or []), payload.get("key"), payload.get("default"))}
    output_packet = {
        "packet_type": "math.series_response.v1",
        "packet_version": "math.series_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "asof-series-lookup",
        "brick_id": CONCEPT["id"],
        "kind": "calculation",
        "label": "Computed as-of series lookup.",
        "refs": [],
        "data": {},
    }]
