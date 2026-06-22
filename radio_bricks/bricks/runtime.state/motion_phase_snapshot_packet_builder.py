from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.motion_phase_snapshot_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪜",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.motion_phase_snapshot_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "motion", "phase", "shot"],
    "description": "Package motion phase runtime state with phase, dominant side, active/ready flags, trigger state, and supporting metrics.",
}


def build_motion_phase_snapshot_packet(
    label: str,
    phase: str,
    dominant_side: str,
    score: float,
    active: bool,
    ready: bool,
    triggered: bool,
    metrics: dict[str, float] | None,
) -> dict[str, Any]:
    return {
        "label": str(label),
        "phase": str(phase),
        "dominant_side": str(dominant_side),
        "score": float(score),
        "active": bool(active),
        "ready": bool(ready),
        "triggered": bool(triggered),
        "metrics": {str(k): float(v) for k, v in dict(metrics or {}).items()},
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_motion_phase_snapshot_packet(
        label=str(payload.get("label") or ""),
        phase=str(payload.get("phase") or ""),
        dominant_side=str(payload.get("dominant_side") or ""),
        score=float(payload.get("score") or 0.0),
        active=bool(payload.get("active")),
        ready=bool(payload.get("ready")),
        triggered=bool(payload.get("triggered")),
        metrics=dict(payload.get("metrics") or {}),
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
        "receipt_id": "motion-phase-snapshot-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built motion-phase snapshot packet.",
        "refs": [],
        "data": {
            "label": value.get("label", ""),
            "phase": value.get("phase", ""),
            "triggered": value.get("triggered", False),
        },
    }]
