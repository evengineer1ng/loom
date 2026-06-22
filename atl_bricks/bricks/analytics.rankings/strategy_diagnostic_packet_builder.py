from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "analytics.rankings.strategy_diagnostic_packet_builder",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["analytics.rankings_request.v1"],
    "outputs": ["analytics.rankings_response.v1"],
    "requires": [],
    "provides": ["analytics.strategy_diagnostic_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["analytics", "rankings", "diagnostic"],
    "description": "Build per-strategy diagnostic packets across universes and variants.",
}


VARIANTS = ["baseline", "exit_off", "profit_only", "custom_exit_off"]


def build_strategy_diagnostic_packet(strategy: str, cells: dict[str, dict[str, Any]] | None, genome_tags: dict[str, list[str]] | None = None) -> dict[str, Any]:
    rows = dict(cells or {})
    tags_by_universe = dict(genome_tags or {})
    universes = []
    for universe, variants in rows.items():
        entry = {"universe": universe, "genome": list(tags_by_universe.get(universe) or []), "variants": []}
        for variant in VARIANTS:
            if variant not in dict(variants or {}):
                continue
            metrics = dict(variants[variant] or {})
            worst = sorted(dict(metrics.get("exits") or {}).items(), key=lambda item: float(dict(item[1]).get("pnl", 0.0)))[:3]
            entry["variants"].append({
                "variant": variant,
                "pnl": metrics.get("pnl"),
                "pnl_pct": metrics.get("pnl_pct"),
                "trades": metrics.get("trades"),
                "win": metrics.get("win"),
                "pf": metrics.get("pf"),
                "dd": metrics.get("dd"),
                "avg_dur": metrics.get("avg_dur"),
                "armed_pnl": metrics.get("armed_pnl"),
                "narmed_pnl": metrics.get("narmed_pnl"),
                "force_pnl": metrics.get("force_pnl"),
                "stop_pnl": metrics.get("stop_pnl"),
                "worst_exits": [{"exit_reason": key, **dict(value)} for key, value in worst],
            })
        universes.append(entry)
    return {"strategy": strategy, "universes": universes}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_strategy_diagnostic_packet(
        strategy=str(payload.get("strategy") or ""),
        cells=dict(payload.get("cells") or {}),
        genome_tags=dict(payload.get("genome_tags") or {}),
    )
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
    return [{"receipt_id": "strategy-diagnostic-packet", "brick_id": CONCEPT["id"], "kind": "report", "label": "Built strategy diagnostic packet.", "refs": [], "data": {"universes": len(value.get("universes") or [])}}]
