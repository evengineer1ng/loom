from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.vessel_snapshot_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🚀",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.vessel_snapshot_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "vessel", "snapshot", "telemetry"],
    "description": "Package KSP vessel snapshots with flight phase, orbital metrics, resource fractions, targeting, EVA, and atmospheric state.",
}


def build_vessel_snapshot_packet(
    name: str,
    situation: str,
    flight_phase: str,
    altitude_m: float,
    apoapsis_m: float,
    periapsis_m: float,
    speed_ms: float,
    fuel_pct: float,
    electric_pct: float,
    target_dist_m: float,
) -> dict[str, Any]:
    return {
        "name": str(name),
        "situation": str(situation),
        "flight_phase": str(flight_phase),
        "altitude_m": float(altitude_m),
        "apoapsis_m": float(apoapsis_m),
        "periapsis_m": float(periapsis_m),
        "speed_ms": float(speed_ms),
        "fuel_pct": float(fuel_pct),
        "electric_pct": float(electric_pct),
        "target_dist_m": float(target_dist_m),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_vessel_snapshot_packet(
        name=str(payload.get("name") or ""),
        situation=str(payload.get("situation") or ""),
        flight_phase=str(payload.get("flight_phase") or ""),
        altitude_m=float(payload.get("altitude_m") or 0.0),
        apoapsis_m=float(payload.get("apoapsis_m") or 0.0),
        periapsis_m=float(payload.get("periapsis_m") or 0.0),
        speed_ms=float(payload.get("speed_ms") or 0.0),
        fuel_pct=float(payload.get("fuel_pct") or 0.0),
        electric_pct=float(payload.get("electric_pct") or 0.0),
        target_dist_m=float(payload.get("target_dist_m") or 0.0),
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
        "receipt_id": "vessel-snapshot-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built vessel-snapshot packet.",
        "refs": [],
        "data": {
            "name": value.get("name", ""),
            "flight_phase": value.get("flight_phase", ""),
            "altitude_m": value.get("altitude_m", 0.0),
        },
    }]
