from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "analytics.rankings.group_breadth_momentum_builder",
    "kind": "analyzer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["analytics.rankings_request.v1"],
    "outputs": ["analytics.rankings_response.v1"],
    "requires": [],
    "provides": ["analytics.group_breadth_momentum"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["analytics", "rankings", "breadth", "momentum"],
    "description": "Build median-return and breadth stats for slow and fast group lookbacks.",
}


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def group_breadth_momentum(rets_slow: list[float] | None, rets_fast: list[float] | None, median_deadband: float = 0.05) -> dict[str, Any]:
    slow = [float(item) for item in (rets_slow or [])]
    fast = [float(item) for item in (rets_fast or [])]
    median_slow = _median(slow)
    if median_slow is not None and abs(median_slow) < median_deadband:
        median_slow = 0.0
    aligned_slow = 0
    for value in slow:
        if median_slow is None:
            continue
        if median_slow > 0 and value > 0:
            aligned_slow += 1
        elif median_slow < 0 and value < 0:
            aligned_slow += 1
        elif abs(median_slow) < 0.1:
            aligned_slow += 1
    median_fast = _median(fast)
    if median_fast is not None and abs(median_fast) < median_deadband:
        median_fast = 0.0
    aligned_fast = 0
    for value in fast:
        if median_fast is None:
            continue
        if median_fast > 0 and value > 0:
            aligned_fast += 1
        elif median_fast < 0 and value < 0:
            aligned_fast += 1
        elif abs(median_fast) < 0.1:
            aligned_fast += 1
    return {
        "median_slow": median_slow,
        "breadth_slow": aligned_slow / len(slow) if slow else None,
        "count_slow": len(slow),
        "median_fast": median_fast,
        "breadth_fast": aligned_fast / len(fast) if fast else None,
        "count_fast": len(fast),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = group_breadth_momentum(payload.get("rets_slow"), payload.get("rets_fast"), float(payload.get("median_deadband") or 0.05))
    output_packet = {
        "packet_type": "analytics.rankings_response.v1",
        "packet_version": "analytics.rankings_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"receipt_id": "group-breadth-momentum", "brick_id": CONCEPT["id"], "kind": "analysis", "label": "Built group breadth momentum stats.", "refs": [], "data": {"count_slow": value.get("count_slow", 0)}}]
