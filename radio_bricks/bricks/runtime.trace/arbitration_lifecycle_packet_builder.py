from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.trace.arbitration_lifecycle_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🔁",
    "deterministic": True,
    "inputs": ["runtime.trace_request.v1"],
    "outputs": ["runtime.trace_response.v1"],
    "requires": [],
    "provides": ["runtime.arbitration_lifecycle_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "trace", "arbitration", "lifecycle", "recognition"],
    "description": "Package arbitration lifecycle state with stage, active/candidate labels, candidate dwell, hold/commit status, and cooldown surfaces.",
}


def build_arbitration_lifecycle_packet(
    stage: str,
    active_label: str,
    candidate_label: str,
    candidate_seconds: float,
    candidate_labels: list[str] | None,
    committed_label: str,
    hold_label: str,
    cooldown_labels: list[str] | None,
    cooldown_remaining: dict[str, float] | None,
) -> dict[str, Any]:
    return {
        "stage": str(stage),
        "active_label": str(active_label),
        "candidate_label": str(candidate_label),
        "candidate_seconds": float(candidate_seconds),
        "candidate_labels": [str(item) for item in (candidate_labels or [])],
        "committed_label": str(committed_label),
        "hold_label": str(hold_label),
        "cooldown_labels": [str(item) for item in (cooldown_labels or [])],
        "cooldown_remaining": {str(k): float(v) for k, v in dict(cooldown_remaining or {}).items()},
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_arbitration_lifecycle_packet(
        stage=str(payload.get("stage") or ""),
        active_label=str(payload.get("active_label") or ""),
        candidate_label=str(payload.get("candidate_label") or ""),
        candidate_seconds=float(payload.get("candidate_seconds") or 0.0),
        candidate_labels=list(payload.get("candidate_labels") or []),
        committed_label=str(payload.get("committed_label") or ""),
        hold_label=str(payload.get("hold_label") or ""),
        cooldown_labels=list(payload.get("cooldown_labels") or []),
        cooldown_remaining=dict(payload.get("cooldown_remaining") or {}),
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
        "receipt_id": "arbitration-lifecycle-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built arbitration lifecycle packet.",
        "refs": [],
        "data": {
            "stage": value.get("stage", ""),
            "active_label": value.get("active_label", ""),
            "candidate_seconds": value.get("candidate_seconds", 0.0),
        },
    }]
