from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "analytics.trades.excursion_capture_analyzer",
    "kind": "analyzer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["analytics.trades_request.v1"],
    "outputs": ["analytics.trades_response.v1"],
    "requires": [],
    "provides": ["analytics.excursion_capture_by_exit"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["analytics", "trades", "mfe", "mae", "capture"],
    "description": "Summarize MFE, MAE, and capture ratio grouped by exit reason.",
}


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def excursion_capture_by_exit(trades: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    rows = [dict(item) for item in (trades or [])]
    reasons = sorted({str(row.get("exit_reason") or "") for row in rows})
    out: list[dict[str, Any]] = []
    for reason in reasons:
        bucket = [row for row in rows if str(row.get("exit_reason") or "") == reason]
        mfe = [float(row.get("mfe") or 0.0) for row in bucket]
        mae = [float(row.get("mae") or 0.0) for row in bucket]
        captures = [
            float(row.get("profit_ratio") or 0.0) / float(row.get("mfe") or 1.0)
            for row in bucket
            if float(row.get("mfe") or 0.0) != 0.0
        ]
        out.append({
            "exit_reason": reason,
            "count": len(bucket),
            "mfe_med": _median(mfe),
            "mfe_avg": sum(mfe) / len(mfe) if mfe else None,
            "mae_med": _median(mae),
            "mae_avg": sum(mae) / len(mae) if mae else None,
            "capture_med": _median(captures),
        })
    return out


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    value = excursion_capture_by_exit(input_packet.get("payload"))
    output_packet = {
        "packet_type": "analytics.trades_response.v1",
        "packet_version": "analytics.trades_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "excursion-capture-analysis",
        "brick_id": CONCEPT["id"],
        "kind": "analysis",
        "label": "Analyzed MFE/MAE/capture by exit reason.",
        "refs": [],
        "data": {"rows": len(value)},
    }]
