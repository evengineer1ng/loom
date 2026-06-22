from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "analytics.trades.blockparty_exit_summary_builder",
    "kind": "analyzer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["analytics.trades_request.v1"],
    "outputs": ["analytics.trades_response.v1"],
    "requires": [],
    "provides": ["analytics.blockparty_exit_summary"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["analytics", "trades", "blockparty", "exit"],
    "description": "Summarize Block Party leadership-flip, group-reversal, and time-stop exit counts.",
}


def blockparty_exit_summary(reasons: list[str] | None) -> dict[str, int]:
    rows = [str(item) for item in (reasons or [])]
    return {
        "leadership_flip": sum(1 for item in rows if item in {"bp_caught_up_long", "bp_caught_up_short"}),
        "group_reversal": sum(1 for item in rows if item in {"bp_group_rev_long", "bp_group_rev_short"}),
        "time_stop": sum(1 for item in rows if item == "bp_time_stop"),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    value = blockparty_exit_summary(input_packet.get("payload"))
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


def receipts(value: dict[str, int]) -> list[dict[str, Any]]:
    return [{"receipt_id": "blockparty-exit-summary", "brick_id": CONCEPT["id"], "kind": "analysis", "label": "Built Block Party exit summary.", "refs": [], "data": value}]
