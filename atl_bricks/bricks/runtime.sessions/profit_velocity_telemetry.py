from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.sessions.profit_velocity_telemetry",
    "kind": "record",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.session_request.v1"],
    "outputs": ["runtime.session_response.v1"],
    "requires": [],
    "provides": ["runtime.update_profit_velocity_telemetry"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "session", "telemetry", "velocity"],
    "description": "Update per-trade profit telemetry with smoothed velocity and running max profit.",
}


def update_profit_velocity_telemetry(state: dict[str, Any] | None, current_profit: float, timestamp: float, velocity_alpha: float) -> dict[str, Any]:
    tel = dict(state or {"last": current_profit, "ts": None, "vel": 0.0, "max": current_profit})
    if tel.get("ts") is not None:
        dp = float(current_profit) - float(tel.get("last", 0.0))
        dt = float(timestamp) - float(tel.get("ts", 0.0))
        inst_vel = (dp / dt) if dt > 0 else 0.0
        tel["vel"] = float(velocity_alpha) * inst_vel + (1.0 - float(velocity_alpha)) * float(tel.get("vel", 0.0))
    tel["last"] = float(current_profit)
    tel["ts"] = float(timestamp)
    tel["max"] = max(float(tel.get("max", current_profit)), float(current_profit))
    return tel


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = update_profit_velocity_telemetry(
        state=dict(payload.get("state") or {}),
        current_profit=float(payload.get("current_profit") or 0.0),
        timestamp=float(payload.get("timestamp") or 0.0),
        velocity_alpha=float(payload.get("velocity_alpha") or 0.0),
    )
    output_packet = {
        "packet_type": "runtime.session_response.v1",
        "packet_version": "runtime.session_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"receipt_id": "profit-velocity-telemetry", "brick_id": CONCEPT["id"], "kind": "record", "label": "Updated profit velocity telemetry.", "refs": [], "data": {"vel": value.get("vel", 0.0), "max": value.get("max", 0.0)}}]
