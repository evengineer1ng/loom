from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "analytics.trades.blockparty_reason_side_summary_builder",
    "kind": "analyzer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["analytics.trades_request.v1"],
    "outputs": ["analytics.trades_response.v1"],
    "requires": [],
    "provides": ["analytics.blockparty_reason_side_summary"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["analytics", "trades", "blockparty", "exit", "side"],
    "description": "Summarize Block Party exit reasons by reason family and long-short side.",
}


def build_blockparty_reason_side_summary(reasons: list[str] | None) -> dict[str, Any]:
    rows = [str(item) for item in (reasons or [])]
    summary = {
        "time_stop": {"long": 0, "short": 0, "unknown": 0},
        "leadership_flip": {"long": 0, "short": 0, "unknown": 0},
        "group_reversal": {"long": 0, "short": 0, "unknown": 0},
    }
    for reason in rows:
        side = "long" if reason.endswith("_long") else "short" if reason.endswith("_short") else "unknown"
        if reason == "bp_time_stop":
            summary["time_stop"][side] += 1
        elif reason in {"bp_caught_up_long", "bp_caught_up_short"}:
            summary["leadership_flip"][side] += 1
        elif reason in {"bp_group_rev_long", "bp_group_rev_short"}:
            summary["group_reversal"][side] += 1
    return summary


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    value = build_blockparty_reason_side_summary(input_packet.get("payload"))
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


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "blockparty-reason-side-summary",
        "brick_id": CONCEPT["id"],
        "kind": "analysis",
        "label": "Built Block Party reason-side summary.",
        "refs": [],
        "data": value,
    }]
