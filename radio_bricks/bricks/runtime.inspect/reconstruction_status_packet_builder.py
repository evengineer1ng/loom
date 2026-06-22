from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.reconstruction_status_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🏗️",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.reconstruction_status_packet"],
    "side_effects": [],
    "ui_slots": ["inspection.reconstruction"],
    "tags": ["runtime", "inspect", "reconstruction", "phases", "progress"],
    "description": "Package ritual reconstruction progress, phase index, and completed phase results into a read model.",
}


def build_reconstruction_status_packet(
    status: str,
    pending: bool,
    progress: float | None = None,
    phase_index: int | None = None,
    total_phases: int | None = None,
    ticks_consumed: int | None = None,
    total_ticks: int | None = None,
    complete: bool | None = None,
    phases_completed: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "status": status,
        "pending": bool(pending),
        "progress": None if progress is None else float(progress),
        "phase_index": None if phase_index is None else int(phase_index),
        "total_phases": None if total_phases is None else int(total_phases),
        "ticks_consumed": None if ticks_consumed is None else int(ticks_consumed),
        "total_ticks": None if total_ticks is None else int(total_ticks),
        "complete": None if complete is None else bool(complete),
        "phases_completed": list(phases_completed or []),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_reconstruction_status_packet(
        status=str(payload.get("status") or ""),
        pending=bool(payload.get("pending", False)),
        progress=payload.get("progress"),
        phase_index=payload.get("phase_index"),
        total_phases=payload.get("total_phases"),
        ticks_consumed=payload.get("ticks_consumed"),
        total_ticks=payload.get("total_ticks"),
        complete=payload.get("complete"),
        phases_completed=list(payload.get("phases_completed") or []),
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
        "receipt_id": "reconstruction-status-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built reconstruction-status packet.",
        "refs": [],
        "data": {"status": value.get("status", ""), "pending": value.get("pending", False)},
    }]
