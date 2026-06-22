from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "analytics.trades.v2_archive_matcher",
    "kind": "analyzer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["analytics.trades_request.v1"],
    "outputs": ["analytics.trades_response.v1"],
    "requires": [],
    "provides": ["analytics.find_v2_archive_match"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["analytics", "archives", "compare"],
    "description": "Find the newest archive matching a target universe key, whitelist set, and v2 exit-signature requirement.",
}


def find_v2_archive_match(archives: list[dict[str, Any]] | None, universe_key: str, whitelist: list[str] | None) -> dict[str, Any] | None:
    wanted = set(str(item) for item in (whitelist or []))
    for archive in list(archives or []):
        row = dict(archive)
        config = dict(row.get("config") or {})
        if str(config.get("universe_key") or "") != str(universe_key or ""):
            continue
        current_whitelist = set(str(item) for item in dict(config.get("exchange") or {}).get("pair_whitelist", []) or [])
        if current_whitelist != wanted:
            continue
        exit_reasons = {str(item) for item in (row.get("exit_reasons") or [])}
        if any(reason.startswith("deadcat_") and reason != "deadcat_exit" for reason in exit_reasons):
            return row
    return None


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = find_v2_archive_match(
        archives=[dict(item) for item in (payload.get("archives") or []) if isinstance(item, dict)],
        universe_key=str(payload.get("universe_key") or ""),
        whitelist=[str(item) for item in (payload.get("whitelist") or [])],
    )
    output_packet = {
        "packet_type": "analytics.trades_response.v1",
        "packet_version": "analytics.trades_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": value is not None, "output_packet": output_packet, "receipts": receipts(value), "issues": [] if value is not None else [{"code": "not_found", "message": "No v2 archive match found."}], "meta": {}}


def receipts(value: dict[str, Any] | None) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "v2-archive-match",
        "brick_id": CONCEPT["id"],
        "kind": "lookup",
        "label": "Matched a v2 archive candidate.",
        "refs": [],
        "data": {"archive": (value or {}).get("name", "")},
    }]
