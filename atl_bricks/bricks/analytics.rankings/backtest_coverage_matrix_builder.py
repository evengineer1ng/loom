from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "analytics.rankings.backtest_coverage_matrix_builder",
    "kind": "analyzer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["analytics.rankings_request.v1"],
    "outputs": ["analytics.rankings_response.v1"],
    "requires": [],
    "provides": ["analytics.backtest_coverage_matrix"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["analytics", "rankings", "backtest", "coverage", "matrix"],
    "description": "Build a backtest coverage matrix that classifies each strategy-universe cell as queued, running, complete, stale, or missing.",
}


def _parse_iso_utc(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value))
    except Exception:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _cell_state(strategy_key: str, universe_key: str, active_jobs: dict[tuple[str, str], str], latest_valid: dict[tuple[str, str], dict[str, Any]], current_hashes: dict[str, str], stale_hours: float, now_iso: str) -> str:
    active = active_jobs.get((strategy_key, universe_key))
    if active:
        return str(active)
    row = latest_valid.get((strategy_key, universe_key))
    if not row:
        return "missing"
    current_hash = str(current_hashes.get(strategy_key) or "")
    recorded_hash = str(row.get("strategy_hash") or "")
    if current_hash and recorded_hash and current_hash != recorded_hash:
        return "stale"
    created = _parse_iso_utc(row.get("created_at"))
    now_dt = _parse_iso_utc(now_iso) or datetime.now(timezone.utc)
    if created is None:
        return "stale"
    age_hours = (now_dt - created).total_seconds() / 3600.0
    return "stale" if age_hours >= float(stale_hours) else "complete"


def build_backtest_coverage_matrix(organisms: list[dict[str, Any]] | None, universes: list[str] | None, active_jobs: dict[tuple[str, str], str] | None, result_rows: list[dict[str, Any]] | None, current_hashes: dict[str, str] | None, stale_hours: float, now_iso: str) -> dict[str, Any]:
    orgs = [dict(item) for item in (organisms or [])]
    universe_keys = [str(item) for item in (universes or [])]
    active = {(str(k[0]), str(k[1])): str(v) for k, v in dict(active_jobs or {}).items()}
    hashes = {str(k): str(v) for k, v in dict(current_hashes or {}).items()}
    latest_valid: dict[tuple[str, str], dict[str, Any]] = {}
    for row in result_rows or []:
        current = dict(row)
        if str(current.get("validity_status", "valid")) != "valid":
            continue
        key = (str(current.get("strategy_key") or ""), str(current.get("universe_key") or ""))
        if key not in latest_valid:
            latest_valid[key] = current

    coverage = {"complete": 0, "stale": 0, "missing": 0, "queued": 0, "running": 0}
    rows = []
    for org in orgs:
        strategy_key = str(org.get("key") or "")
        cells = []
        for universe_key in universe_keys:
            state = _cell_state(strategy_key, universe_key, active, latest_valid, hashes, stale_hours, now_iso)
            coverage[state] = coverage.get(state, 0) + 1
            result = latest_valid.get((strategy_key, universe_key), {})
            cells.append({
                "universe_key": universe_key,
                "state": state,
                "pnl": result.get("total_pnl"),
                "run_id": result.get("run_id", ""),
            })
        rows.append({"strategy_key": strategy_key, "strategy_name": org.get("name") or strategy_key, "cells": cells})
    return {"coverage": coverage, "rows": rows, "universe_count": len(universe_keys), "strategy_count": len(orgs)}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    raw_jobs = payload.get("active_jobs") or {}
    active_jobs = {}
    if isinstance(raw_jobs, dict):
        for key, value in raw_jobs.items():
            if isinstance(key, str) and "|" in key:
                left, right = key.split("|", 1)
                active_jobs[(left, right)] = value
    value = build_backtest_coverage_matrix(
        organisms=list(payload.get("organisms") or []),
        universes=list(payload.get("universes") or []),
        active_jobs=active_jobs,
        result_rows=list(payload.get("result_rows") or []),
        current_hashes=dict(payload.get("current_hashes") or {}),
        stale_hours=float(payload.get("stale_hours") or 24.0),
        now_iso=str(payload.get("now_iso") or ""),
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
    return [{
        "receipt_id": "backtest-coverage-matrix",
        "brick_id": CONCEPT["id"],
        "kind": "analysis",
        "label": "Built backtest coverage matrix.",
        "refs": [],
        "data": value.get("coverage", {}),
    }]
