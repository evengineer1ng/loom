from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.genome.strategy_genome_diagnoser",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["assembly.catalog_request.v1"],
    "outputs": ["assembly.catalog_response.v1"],
    "requires": [],
    "provides": ["assembly.strategy_genome_tags"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "genome", "diagnosis"],
    "description": "Assign diagnostic genome tags from baseline and exit-off metrics plus derived attribution scores.",
}


def strategy_genome_tags(metrics_by_variant: dict[str, dict[str, Any]] | None, scores: dict[str, Any] | None) -> list[str]:
    variants = dict(metrics_by_variant or {})
    derived = dict(scores or {})
    baseline = variants.get("baseline")
    exit_off = variants.get("exit_off")
    if not (baseline and exit_off):
        return ["incomplete"]
    tags: list[str] = []
    exit_damage = float(derived.get("exit_damage", 0.0) or 0.0)
    churn = derived.get("churn_amp", 1)
    entry_ok = float(exit_off.get("pnl", 0.0) or 0.0) > 0
    exit_ok = float(baseline.get("pnl", 0.0) or 0.0) > 0
    if exit_damage > 20 and entry_ok and not exit_ok:
        tags.append("Entry Alpha / Exit Damage")
    if float(derived.get("exit_alpha", 0.0) or 0.0) > 20 and exit_ok and float(exit_off.get("pnl", 0.0) or 0.0) <= 0:
        tags.append("Exit Alpha / Weak Entry")
    if entry_ok and exit_ok:
        tags.append("Both Strong")
    if not entry_ok and not exit_ok:
        tags.append("Both Weak")
    if entry_ok and float(exit_off.get("trades", 0) or 0) < 0.6 * float(baseline.get("trades", 0) or 0) and float(exit_off.get("avg_dur", 0.0) or 0.0) >= 12:
        tags.append("Trend-Following Candidate")
    if churn != float("inf") and float(churn or 0.0) >= 2.0:
        tags.append("Churn Trap")
    baseline_pnl = float(baseline.get("pnl", 0.0) or 0.0)
    if float(baseline.get("stop_pnl", 0.0) or 0.0) < -0.4 * abs(baseline_pnl if baseline_pnl else 1.0) and float(baseline.get("stop_n", 0) or 0) > 0.1 * max(float(baseline.get("trades", 0) or 0), 1.0):
        tags.append("Stop-Loss Bleeder")
    if float(derived.get("force_dependence", 0.0) or 0.0) >= 0.6:
        tags.append("Force-Exit Dependent")
    return tags or ["Neutral"]


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = {"tags": strategy_genome_tags(dict(payload.get("metrics_by_variant") or {}), dict(payload.get("scores") or {}))}
    output_packet = {
        "packet_type": "assembly.catalog_response.v1",
        "packet_version": "assembly.catalog_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "strategy-genome-tags",
        "brick_id": CONCEPT["id"],
        "kind": "diagnosis",
        "label": "Assigned strategy genome diagnosis tags.",
        "refs": [],
        "data": {"tags": len(value.get("tags") or [])},
    }]
