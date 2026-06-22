from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.sessions.deadcat_summary_packet_builder",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.session_request.v1"],
    "outputs": ["runtime.session_response.v1"],
    "requires": [],
    "provides": ["runtime.deadcat_summary_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "session", "deadcat", "summary"],
    "description": "Build a compact deadcat-anatomy summary packet from bucket stats, subtype counts, and obvious-loss timing.",
}


def build_deadcat_summary_packet(summary: dict[str, Any] | None, tag_conversion: list[dict[str, Any]] | None = None, subtypes: dict[str, Any] | None = None) -> dict[str, Any]:
    row = dict(summary or {})
    return {
        "trades": row.get("trades", 0),
        "win_pct": row.get("win_pct", 0.0),
        "avg_roi": row.get("avg_roi", 0.0),
        "total_pnl": row.get("total_pnl", 0.0),
        "avg_duration_candles": row.get("avg_duration_candles", 0.0),
        "mfe_med": row.get("mfe_med"),
        "mfe_avg": row.get("mfe_avg"),
        "mae_med": row.get("mae_med"),
        "mae_avg": row.get("mae_avg"),
        "long_count": row.get("long_count", 0),
        "short_count": row.get("short_count", 0),
        "had_prior_winner": row.get("had_prior_winner", 0),
        "obvious_earlier": row.get("obvious_earlier", 0),
        "tag_conversion": list(tag_conversion or []),
        "subtypes": dict(subtypes or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_deadcat_summary_packet(dict(payload.get("summary") or {}), list(payload.get("tag_conversion") or []), dict(payload.get("subtypes") or {}))
    output_packet = {
        "packet_type": "runtime.session_response.v1",
        "packet_version": "runtime.session_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"receipt_id": "deadcat-summary-packet", "brick_id": CONCEPT["id"], "kind": "report", "label": "Built deadcat summary packet.", "refs": [], "data": {"trades": value.get("trades", 0)}}]
