from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.reconstruction.phase_result_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.reconstruction_request.v1"],
    "outputs": ["runtime.reconstruction_response.v1"],
    "requires": [],
    "provides": ["runtime.reconstruction_phase_result"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "reconstruction", "phase", "ritual"],
    "description": "Package one absence-reconstruction phase with health deltas, crossings, and event summaries.",
}


def build_phase_result(
    phase_name: str,
    phase_description: str,
    ticks_processed: int,
    health_before: float,
    health_after: float,
    years_elapsed: float,
    events_summary: list[str] | None,
    variable_crossings: list[str] | None,
    key_changes: dict[str, float] | None,
) -> dict[str, Any]:
    delta = float(health_after) - float(health_before)
    if delta > 2.0:
        trend = "rising"
    elif delta < -2.0:
        trend = "declining"
    else:
        trend = "stable"
    return {
        "phase_name": phase_name,
        "phase_description": phase_description,
        "ticks_processed": int(ticks_processed),
        "new_events_count": len(list(events_summary or [])),
        "events_summary": list(events_summary or []),
        "variable_crossings": list(variable_crossings or []),
        "health_before": round(float(health_before), 1),
        "health_after": round(float(health_after), 1),
        "health_trend": trend,
        "years_elapsed": round(float(years_elapsed), 2),
        "key_changes": dict(key_changes or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_phase_result(
        phase_name=str(payload.get("phase_name") or ""),
        phase_description=str(payload.get("phase_description") or ""),
        ticks_processed=int(payload.get("ticks_processed") or 0),
        health_before=float(payload.get("health_before") or 0.0),
        health_after=float(payload.get("health_after") or 0.0),
        years_elapsed=float(payload.get("years_elapsed") or 0.0),
        events_summary=list(payload.get("events_summary") or []),
        variable_crossings=list(payload.get("variable_crossings") or []),
        key_changes=dict(payload.get("key_changes") or {}),
    )
    output_packet = {
        "packet_type": "runtime.reconstruction_response.v1",
        "packet_version": "runtime.reconstruction_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "reconstruction-phase-result",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built reconstruction phase result.",
        "refs": [],
        "data": {"phase_name": value.get("phase_name", ""), "health_trend": value.get("health_trend", "")},
    }]
