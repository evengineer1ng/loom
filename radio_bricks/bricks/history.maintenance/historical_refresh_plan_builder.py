from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "history.maintenance.historical_refresh_plan_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["history.maintenance_request.v1"],
    "outputs": ["history.maintenance_response.v1"],
    "requires": [],
    "provides": ["history.historical_refresh_plan"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["history", "maintenance", "refresh", "plan"],
    "description": "Plan a bulk historical refresh over teams and drivers after major simulation milestones.",
}


def build_historical_refresh_plan(team_names: list[str] | None, driver_names: list[str] | None, tick: int) -> dict[str, Any]:
    teams = [str(name) for name in (team_names or []) if str(name)]
    drivers = [str(name) for name in (driver_names or []) if str(name)]
    team_tasks = [{"team_name": name, "tasks": ["career_totals", "peak_valley", "momentum_metrics"]} for name in teams]
    driver_tasks = [{"driver_name": name, "tasks": ["career_stats"]} for name in drivers]
    return {
        "tick": int(tick),
        "team_tasks": team_tasks,
        "driver_tasks": driver_tasks,
        "team_count": len(team_tasks),
        "driver_count": len(driver_tasks),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_historical_refresh_plan(
        team_names=list(payload.get("team_names") or []),
        driver_names=list(payload.get("driver_names") or []),
        tick=int(payload.get("tick") or 0),
    )
    output_packet = {
        "packet_type": "history.maintenance_response.v1",
        "packet_version": "history.maintenance_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "historical-refresh-plan",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built historical refresh plan.",
        "refs": [],
        "data": {"team_count": value.get("team_count", 0), "driver_count": value.get("driver_count", 0)},
    }]
