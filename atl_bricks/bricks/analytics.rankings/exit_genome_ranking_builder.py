from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "analytics.rankings.exit_genome_ranking_builder",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["analytics.rankings_request.v1"],
    "outputs": ["analytics.rankings_response.v1"],
    "requires": [],
    "provides": ["analytics.exit_genome_ranking"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["analytics", "rankings", "exit", "genome"],
    "description": "Build ranked exit-genome rows with verdicts from attribution scores.",
}


def build_exit_genome_ranking(scored: dict[str, dict[str, Any]] | None) -> list[dict[str, Any]]:
    rows = dict(scored or {})
    order = sorted(
        [name for name, row in rows.items() if "exit_alpha" in dict(row.get("d") or {})],
        key=lambda name: -float(dict(rows[name].get("d") or {}).get("exit_alpha", 0.0) or 0.0),
    )
    out = []
    for index, name in enumerate(order, 1):
        derived = dict(rows[name].get("d") or {})
        exit_alpha = float(derived.get("exit_alpha", 0.0) or 0.0)
        verdict = "exits ADD value" if exit_alpha > 20 else ("exits DESTROY value" if exit_alpha < -20 else "neutral")
        out.append({
            "rank": index,
            "strategy": name,
            "exit_alpha": derived.get("exit_alpha"),
            "custom_exit_contribution": derived.get("custom_exit_contribution"),
            "profit_only_sensitivity": derived.get("profit_only_sensitivity"),
            "verdict": verdict,
        })
    return out


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    value = build_exit_genome_ranking(dict(input_packet.get("payload") or {}))
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
    return [{"receipt_id": "exit-genome-ranking", "brick_id": CONCEPT["id"], "kind": "ranking", "label": "Built exit genome ranking.", "refs": [], "data": {"rows": len(value)}}]
