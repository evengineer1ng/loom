from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "analytics.rankings.entry_genome_ranking_builder",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["analytics.rankings_request.v1"],
    "outputs": ["analytics.rankings_response.v1"],
    "requires": [],
    "provides": ["analytics.entry_genome_ranking"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["analytics", "rankings", "entry", "genome"],
    "description": "Build ranked entry-genome rows from exit-off metrics and derived attribution scores.",
}


def build_entry_genome_ranking(scored: dict[str, dict[str, Any]] | None) -> list[dict[str, Any]]:
    rows = dict(scored or {})
    order = sorted(
        [name for name, row in rows.items() if "entry_raw" in dict(row.get("d") or {})],
        key=lambda name: -float(dict(rows[name].get("d") or {}).get("entry_raw", 0.0) or 0.0),
    )
    out = []
    for index, name in enumerate(order, 1):
        metrics = dict(dict(rows[name].get("m") or {}).get("exit_off") or {})
        derived = dict(rows[name].get("d") or {})
        out.append({
            "rank": index,
            "strategy": name,
            "entry_raw": derived.get("entry_raw"),
            "exitoff_pnl": metrics.get("pnl"),
            "exitoff_win": metrics.get("win"),
            "exitoff_avg_dur": metrics.get("avg_dur"),
            "force_dependence": derived.get("force_dependence"),
        })
    return out


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    value = build_entry_genome_ranking(dict(input_packet.get("payload") or {}))
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
    return [{"receipt_id": "entry-genome-ranking", "brick_id": CONCEPT["id"], "kind": "ranking", "label": "Built entry genome ranking.", "refs": [], "data": {"rows": len(value)}}]
