from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "analytics.rankings.churn_warning_report_builder",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["analytics.rankings_request.v1"],
    "outputs": ["analytics.rankings_response.v1"],
    "requires": [],
    "provides": ["analytics.churn_warning_report"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["analytics", "rankings", "churn"],
    "description": "Build churn and overtrading warning rows from baseline and exit-off metrics.",
}


def build_churn_warning_report(scored: dict[str, dict[str, Any]] | None) -> list[dict[str, Any]]:
    rows = dict(scored or {})
    order = sorted(
        rows.keys(),
        key=lambda name: -(99 if dict(rows[name].get("d") or {}).get("churn_amp") == float("inf") else float(dict(rows[name].get("d") or {}).get("churn_amp", 0.0) or 0.0)),
    )
    out = []
    for name in order:
        metrics = dict(rows[name].get("m") or {})
        derived = dict(rows[name].get("d") or {})
        churn = derived.get("churn_amp")
        if churn is None:
            continue
        out.append({
            "strategy": name,
            "churn_amp": churn,
            "base_tpd": dict(metrics.get("baseline") or {}).get("tpd"),
            "exitoff_tpd": dict(metrics.get("exit_off") or {}).get("tpd"),
            "flag": "CHURN TRAP" if churn != float("inf") and float(churn or 0.0) >= 2.0 else "",
        })
    return out


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    value = build_churn_warning_report(dict(input_packet.get("payload") or {}))
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
    return [{"receipt_id": "churn-warning-report", "brick_id": CONCEPT["id"], "kind": "report", "label": "Built churn warning report.", "refs": [], "data": {"rows": len(value)}}]
