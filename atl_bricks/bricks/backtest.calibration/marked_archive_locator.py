from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "backtest.calibration.marked_archive_locator",
    "kind": "analyzer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["backtest.sim_request.v1"],
    "outputs": ["backtest.sim_response.v1"],
    "requires": [],
    "provides": ["backtest.find_marked_archive"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["backtest", "archives", "markers"],
    "description": "Find the newest archive whose embedded config markers match a requested run cell.",
}


def find_marked_archive(archives: list[dict[str, Any]] | None, since_ts: float, strategy: str, universe: str, variant: str) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    best_ts = 0.0
    for archive in list(archives or []):
        row = dict(archive)
        modified_at = float(row.get("modified_at") or 0.0)
        if modified_at < since_ts - 5 or modified_at <= best_ts:
            continue
        config = dict(row.get("config") or {})
        if (
            str(config.get("pliers_variant") or "") == variant
            and str(config.get("pliers_strategy") or "") == strategy
            and str(config.get("pliers_universe") or "") == universe
        ):
            best = row
            best_ts = modified_at
    return best


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = find_marked_archive(
        archives=[dict(item) for item in (payload.get("archives") or []) if isinstance(item, dict)],
        since_ts=float(payload.get("since_ts") or 0.0),
        strategy=str(payload.get("strategy") or ""),
        universe=str(payload.get("universe") or ""),
        variant=str(payload.get("variant") or ""),
    )
    output_packet = {
        "packet_type": "backtest.sim_response.v1",
        "packet_version": "backtest.sim_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": value is not None, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [] if value is not None else [{"code": "not_found", "message": "No matching marked archive found."}], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    payload = output_packet.get("payload") or {}
    return [{
        "receipt_id": "marked-archive-located",
        "brick_id": CONCEPT["id"],
        "kind": "lookup",
        "label": "Located newest archive by config markers.",
        "refs": [],
        "data": {"archive": payload.get("name", "") if isinstance(payload, dict) else ""},
    }]
