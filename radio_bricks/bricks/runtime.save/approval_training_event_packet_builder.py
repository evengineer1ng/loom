from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.save.approval_training_event_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧪",
    "deterministic": True,
    "inputs": ["runtime.save_request.v1"],
    "outputs": ["runtime.save_response.v1"],
    "requires": [],
    "provides": ["runtime.approval_training_event_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "save", "approval", "training", "event"],
    "description": "Package an approval-training forensic event with predicted action, decision state, source camera, reason codes, top candidates, thresholds, and feature/context snapshots.",
}


def build_approval_training_event_packet(
    event_id: str,
    session_id: str,
    profile_id: str,
    event_type: str,
    predicted_action: str,
    predicted_family: str,
    decision_state: str,
    decision_source_camera: str,
    decision_confidence: float,
    decision_margin: float,
    decision_reason_codes: list[str] | None,
    top_candidates: list[dict[str, object]] | None,
    thresholds: dict[str, object] | None,
    suppression_context: dict[str, object] | None,
) -> dict[str, Any]:
    return {
        "event_id": str(event_id),
        "session_id": str(session_id),
        "profile_id": str(profile_id),
        "event_type": str(event_type),
        "predicted_action": str(predicted_action),
        "predicted_family": str(predicted_family),
        "decision_state": str(decision_state),
        "decision_source_camera": str(decision_source_camera),
        "decision_confidence": float(decision_confidence),
        "decision_margin": float(decision_margin),
        "decision_reason_codes": [str(item) for item in (decision_reason_codes or [])],
        "top_candidates": list(top_candidates or []),
        "thresholds": dict(thresholds or {}),
        "suppression_context": dict(suppression_context or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_approval_training_event_packet(
        event_id=str(payload.get("event_id") or ""),
        session_id=str(payload.get("session_id") or ""),
        profile_id=str(payload.get("profile_id") or ""),
        event_type=str(payload.get("event_type") or ""),
        predicted_action=str(payload.get("predicted_action") or ""),
        predicted_family=str(payload.get("predicted_family") or ""),
        decision_state=str(payload.get("decision_state") or ""),
        decision_source_camera=str(payload.get("decision_source_camera") or ""),
        decision_confidence=float(payload.get("decision_confidence") or 0.0),
        decision_margin=float(payload.get("decision_margin") or 0.0),
        decision_reason_codes=list(payload.get("decision_reason_codes") or []),
        top_candidates=list(payload.get("top_candidates") or []),
        thresholds=dict(payload.get("thresholds") or {}),
        suppression_context=dict(payload.get("suppression_context") or {}),
    )
    output_packet = {
        "packet_type": "runtime.save_response.v1",
        "packet_version": "runtime.save_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "approval-training-event-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built approval-training event packet.",
        "refs": [],
        "data": {
            "event_type": value.get("event_type", ""),
            "predicted_action": value.get("predicted_action", ""),
            "decision_source_camera": value.get("decision_source_camera", ""),
        },
    }]
