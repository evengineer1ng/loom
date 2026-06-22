from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.simulation_driver_state_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎮",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.simulation_driver_state_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "simulation", "driver", "test"],
    "description": "Package simulation-driver state for test feeds that step through staged mission or game phases with internally generated telemetry snapshots.",
}


def build_simulation_driver_state_packet(
    phase: str,
    phase_elapsed_sec: float,
    state_snapshot: dict[str, Any] | None,
    source_system: str,
) -> dict[str, Any]:
    return {
        "phase": str(phase),
        "phase_elapsed_sec": float(phase_elapsed_sec),
        "state_snapshot": dict(state_snapshot or {}),
        "source_system": str(source_system),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_simulation_driver_state_packet(
        phase=str(payload.get("phase") or ""),
        phase_elapsed_sec=float(payload.get("phase_elapsed_sec") or 0.0),
        state_snapshot=dict(payload.get("state_snapshot") or {}),
        source_system=str(payload.get("source_system") or ""),
    )
    output_packet = {
        "packet_type": "runtime.state_response.v1",
        "packet_version": "runtime.state_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "simulation-driver-state-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built simulation-driver state packet.",
        "refs": [],
        "data": {
            "phase": value.get("phase", ""),
            "source_system": value.get("source_system", ""),
        },
    }]
