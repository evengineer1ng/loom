from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "analytics.rankings.cross_universe_consistency_builder",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["analytics.rankings_request.v1"],
    "outputs": ["analytics.rankings_response.v1"],
    "requires": [],
    "provides": ["analytics.cross_universe_consistency"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["analytics", "rankings", "consistency"],
    "description": "Build cross-universe consistency rows from exit-damage values.",
}


def build_cross_universe_consistency(exit_damage_by_strategy: dict[str, dict[str, float]] | None) -> list[dict[str, Any]]:
    rows = dict(exit_damage_by_strategy or {})
    out = []
    for strategy, universe_values in sorted(rows.items()):
        values = dict(universe_values or {})
        signs = {">0" if float(value) > 0 else "<0" for value in values.values() if value is not None}
        out.append({
            "strategy": strategy,
            "exit_damage_by_universe": values,
            "consistent": len(signs) == 1,
            "verdict": "yes" if len(signs) == 1 else "NO - universe-specific",
        })
    return out


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    value = build_cross_universe_consistency(dict(input_packet.get("payload") or {}))
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


def receipts(value: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"receipt_id": "cross-universe-consistency", "brick_id": CONCEPT["id"], "kind": "report", "label": "Built cross-universe consistency report.", "refs": [], "data": {"rows": len(value)}}]
