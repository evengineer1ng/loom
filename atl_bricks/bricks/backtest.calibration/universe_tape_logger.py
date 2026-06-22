from __future__ import annotations

import json
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "backtest.calibration.universe_tape_logger",
    "kind": "world_operator",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["backtest.sim_request.v1"],
    "outputs": ["backtest.sim_response.v1"],
    "requires": [],
    "provides": ["backtest.universe_tape_entry"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["backtest", "universe", "tape", "logging"],
    "description": "Emit one JSONL-ready universe tape record for a backtest day with universe name and member pairs.",
}


def universe_tape_entry(day: str, universe: str, members: list[str] | None) -> dict[str, Any]:
    pair_list = sorted(str(item) for item in (members or []))
    return {
        "date": str(day or ""),
        "universe": str(universe or ""),
        "count": len(pair_list),
        "pairs": pair_list,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = universe_tape_entry(str(payload.get("day") or ""), str(payload.get("universe") or ""), payload.get("members"))
    output_packet = {
        "packet_type": "backtest.sim_response.v1",
        "packet_version": "backtest.sim_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"record": value, "jsonl": json.dumps(value)},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(record: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "universe-tape-record",
        "brick_id": CONCEPT["id"],
        "kind": "artifact",
        "label": "Built universe tape record.",
        "refs": [],
        "data": {"count": record.get("count", 0), "universe": record.get("universe", "")},
    }]
