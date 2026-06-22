from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "analytics.rankings.power_rank_side_builder",
    "kind": "ranking",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["analytics.rankings_request.v1"],
    "outputs": ["analytics.rankings_response.v1"],
    "requires": [],
    "provides": ["analytics.power_rank_side"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["analytics", "rankings", "power-rank"],
    "description": "Rank same-side trades from worst to best using profit plus weighted velocity.",
}


def power_rank_side(rows: list[dict[str, Any]] | None, velocity_weight: float) -> dict[int, int]:
    scored = []
    for row in list(rows or []):
        trade_id = int(row.get("trade_id") or 0)
        current_profit = row.get("current_profit")
        if current_profit is None:
            continue
        velocity = float(row.get("velocity") or 0.0)
        score = float(current_profit) + float(velocity_weight) * velocity
        scored.append((trade_id, score))
    scored.sort(key=lambda item: item[1])
    return {trade_id: index + 1 for index, (trade_id, _) in enumerate(scored)}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = power_rank_side(payload.get("rows"), float(payload.get("velocity_weight") or 0.0))
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


def receipts(value: dict[int, int]) -> list[dict[str, Any]]:
    return [{"receipt_id": "power-rank-side", "brick_id": CONCEPT["id"], "kind": "ranking", "label": "Built side power ranks.", "refs": [], "data": {"rows": len(value)}}]
