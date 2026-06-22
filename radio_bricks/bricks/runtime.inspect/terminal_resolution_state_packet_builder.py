from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.terminal_resolution_state_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "☄️",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.terminal_resolution_state_packet"],
    "side_effects": [],
    "ui_slots": ["inspection.terminal_resolution"],
    "tags": ["runtime", "inspect", "terminal", "collapse", "history"],
    "description": "Package terminal-resolution readiness, collapse tracking, and resolution history for UI or archive readers.",
}


def build_terminal_resolution_state_packet(
    collapse_duration: int,
    collapse_threshold: float,
    duration_min: int,
    material_state: str,
    health_composite: float,
    total_resolutions: int,
    resolutions: list[dict[str, Any]] | None,
    is_in_collapse: bool,
    ticks_until_eligible: int,
) -> dict[str, Any]:
    return {
        "collapse_duration": int(collapse_duration),
        "collapse_threshold": float(collapse_threshold),
        "duration_min": int(duration_min),
        "material_state": material_state,
        "health_composite": float(health_composite),
        "total_resolutions": int(total_resolutions),
        "resolutions": list(resolutions or []),
        "is_in_collapse": bool(is_in_collapse),
        "ticks_until_eligible": int(ticks_until_eligible),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_terminal_resolution_state_packet(
        collapse_duration=int(payload.get("collapse_duration") or 0),
        collapse_threshold=float(payload.get("collapse_threshold") or 0.0),
        duration_min=int(payload.get("duration_min") or 0),
        material_state=str(payload.get("material_state") or ""),
        health_composite=float(payload.get("health_composite") or 0.0),
        total_resolutions=int(payload.get("total_resolutions") or 0),
        resolutions=list(payload.get("resolutions") or []),
        is_in_collapse=bool(payload.get("is_in_collapse", False)),
        ticks_until_eligible=int(payload.get("ticks_until_eligible") or 0),
    )
    output_packet = {
        "packet_type": "runtime.inspect_response.v1",
        "packet_version": "runtime.inspect_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "terminal-resolution-state-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built terminal-resolution state packet.",
        "refs": [],
        "data": {"is_in_collapse": value.get("is_in_collapse", False), "total_resolutions": value.get("total_resolutions", 0)},
    }]
