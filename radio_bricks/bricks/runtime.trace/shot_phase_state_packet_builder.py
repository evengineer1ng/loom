from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.trace.shot_phase_state_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🏀",
    "deterministic": True,
    "inputs": ["runtime.trace_request.v1"],
    "outputs": ["runtime.trace_response.v1"],
    "requires": [],
    "provides": ["runtime.shot_phase_state_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "trace", "phase", "shot", "state"],
    "description": "Package phase-gated shot motion state with dominant side, current phase, active status, trigger readiness, and supporting metrics.",
}


def build_shot_phase_state_packet(
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
        "metrics": {str(key): float(value) for key, value in (metrics or {}).items()},
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_shot_phase_state_packet(
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
        "packet_type": "runtime.trace_response.v1",
        "packet_version": "runtime.trace_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "shot-phase-state-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built shot-phase state packet.",
        "refs": [],
        "data": {
            "label": value.get("label", ""),
            "phase": value.get("phase", ""),
            "triggered": value.get("triggered", False),
        },
    }]
