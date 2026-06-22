from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.trace.recognition_diagnostics_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧠",
    "deterministic": True,
    "inputs": ["runtime.trace_request.v1"],
    "outputs": ["runtime.trace_response.v1"],
    "requires": [],
    "provides": ["runtime.recognition_diagnostics_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "trace", "recognition", "diagnostics", "decision"],
    "description": "Package full recognition diagnostics with score ladders, decision state, evidence, gesture progress, suppression, lifecycle, and ball-state context.",
}


def build_recognition_diagnostics_packet(
    timestamp: float,
    class_scores: dict[str, float] | None,
    motion_scores: dict[str, float] | None,
    best_label: str,
    best_variant: str,
    best_score: float,
    runner_up_label: str,
    runner_up_variant: str,
    runner_up_score: float,
    idle_score: float,
    unknown_score: float,
    ambiguity_margin: float,
    null_margin: float,
    tracking_quality: float,
    state: str,
    decision: str,
    reason: str,
    committed_label: str,
    committed_variant: str,
    best_evidence: list[dict[str, Any]] | None,
    runner_up_evidence: list[dict[str, Any]] | None,
    active_poses: list[str] | None,
    fired_motions: list[str] | None,
    pose_gate_status: list[dict[str, Any]] | None,
    matched_gestures: list[str] | None,
    gesture_progress: dict[str, str] | None,
    phase_triggers: list[str] | None,
    suppressed_labels: list[str] | None,
    motion_states: dict[str, dict[str, Any]] | None,
    lifecycle: dict[str, Any] | None,
    ball_state: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "timestamp": float(timestamp),
        "class_scores": {str(key): float(value) for key, value in (class_scores or {}).items()},
        "motion_scores": {str(key): float(value) for key, value in (motion_scores or {}).items()},
        "best_label": str(best_label),
        "best_variant": str(best_variant),
        "best_score": float(best_score),
        "runner_up_label": str(runner_up_label),
        "runner_up_variant": str(runner_up_variant),
        "runner_up_score": float(runner_up_score),
        "idle_score": float(idle_score),
        "unknown_score": float(unknown_score),
        "ambiguity_margin": float(ambiguity_margin),
        "null_margin": float(null_margin),
        "tracking_quality": float(tracking_quality),
        "state": str(state),
        "decision": str(decision),
        "reason": str(reason),
        "committed_label": str(committed_label),
        "committed_variant": str(committed_variant),
        "best_evidence": [dict(item) for item in (best_evidence or [])],
        "runner_up_evidence": [dict(item) for item in (runner_up_evidence or [])],
        "active_poses": [str(item) for item in (active_poses or [])],
        "fired_motions": [str(item) for item in (fired_motions or [])],
        "pose_gate_status": [dict(item) for item in (pose_gate_status or [])],
        "matched_gestures": [str(item) for item in (matched_gestures or [])],
        "gesture_progress": {str(key): str(value) for key, value in (gesture_progress or {}).items()},
        "phase_triggers": [str(item) for item in (phase_triggers or [])],
        "suppressed_labels": [str(item) for item in (suppressed_labels or [])],
        "motion_states": {str(key): dict(value) for key, value in (motion_states or {}).items()},
        "lifecycle": dict(lifecycle or {}),
        "ball_state": dict(ball_state or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_recognition_diagnostics_packet(
        timestamp=float(payload.get("timestamp") or 0.0),
        class_scores=dict(payload.get("class_scores") or {}),
        motion_scores=dict(payload.get("motion_scores") or {}),
        best_label=str(payload.get("best_label") or ""),
        best_variant=str(payload.get("best_variant") or ""),
        best_score=float(payload.get("best_score") or 0.0),
        runner_up_label=str(payload.get("runner_up_label") or ""),
        runner_up_variant=str(payload.get("runner_up_variant") or ""),
        runner_up_score=float(payload.get("runner_up_score") or 0.0),
        idle_score=float(payload.get("idle_score") or 0.0),
        unknown_score=float(payload.get("unknown_score") or 0.0),
        ambiguity_margin=float(payload.get("ambiguity_margin") or 0.0),
        null_margin=float(payload.get("null_margin") or 0.0),
        tracking_quality=float(payload.get("tracking_quality") or 0.0),
        state=str(payload.get("state") or ""),
        decision=str(payload.get("decision") or ""),
        reason=str(payload.get("reason") or ""),
        committed_label=str(payload.get("committed_label") or ""),
        committed_variant=str(payload.get("committed_variant") or ""),
        best_evidence=list(payload.get("best_evidence") or []),
        runner_up_evidence=list(payload.get("runner_up_evidence") or []),
        active_poses=list(payload.get("active_poses") or []),
        fired_motions=list(payload.get("fired_motions") or []),
        pose_gate_status=list(payload.get("pose_gate_status") or []),
        matched_gestures=list(payload.get("matched_gestures") or []),
        gesture_progress=dict(payload.get("gesture_progress") or {}),
        phase_triggers=list(payload.get("phase_triggers") or []),
        suppressed_labels=list(payload.get("suppressed_labels") or []),
        motion_states=dict(payload.get("motion_states") or {}),
        lifecycle=dict(payload.get("lifecycle") or {}),
        ball_state=dict(payload.get("ball_state") or {}),
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
        "receipt_id": "recognition-diagnostics-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built recognition diagnostics packet.",
        "refs": [],
        "data": {
            "decision": value.get("decision", ""),
            "best_label": value.get("best_label", ""),
            "suppressed_count": len(value.get("suppressed_labels", [])),
        },
    }]
