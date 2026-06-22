from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.ball_state_snapshot_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🏀",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.ball_state_snapshot_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "ball", "snapshot", "context"],
    "description": "Package a basketball-context snapshot with ball side, phase, possession state, branch state, context confidence, and transfer/pass flags.",
}


def build_ball_state_snapshot_packet(
    enabled: bool,
    ball_side: str,
    ball_phase: str,
    possession_confidence: float,
    offense_context: float,
    movement_state: str,
    possession_state: str,
    branch_state: str,
    dribble_active: bool,
    pass_transition_active: bool,
    pass_transition_frames_left: int,
    triple_threat_active: bool,
    locomotion_score: float,
    transfer_active: bool,
    transfer_target: str,
    transfer_frames_left: int,
) -> dict[str, Any]:
    return {
        "enabled": bool(enabled),
        "ball_side": str(ball_side),
        "ball_phase": str(ball_phase),
        "possession_confidence": float(possession_confidence),
        "offense_context": float(offense_context),
        "movement_state": str(movement_state),
        "possession_state": str(possession_state),
        "branch_state": str(branch_state),
        "dribble_active": bool(dribble_active),
        "pass_transition_active": bool(pass_transition_active),
        "pass_transition_frames_left": int(pass_transition_frames_left),
        "triple_threat_active": bool(triple_threat_active),
        "locomotion_score": float(locomotion_score),
        "transfer_active": bool(transfer_active),
        "transfer_target": str(transfer_target),
        "transfer_frames_left": int(transfer_frames_left),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_ball_state_snapshot_packet(
        enabled=bool(payload.get("enabled")),
        ball_side=str(payload.get("ball_side") or ""),
        ball_phase=str(payload.get("ball_phase") or ""),
        possession_confidence=float(payload.get("possession_confidence") or 0.0),
        offense_context=float(payload.get("offense_context") or 0.0),
        movement_state=str(payload.get("movement_state") or ""),
        possession_state=str(payload.get("possession_state") or ""),
        branch_state=str(payload.get("branch_state") or ""),
        dribble_active=bool(payload.get("dribble_active")),
        pass_transition_active=bool(payload.get("pass_transition_active")),
        pass_transition_frames_left=int(payload.get("pass_transition_frames_left") or 0),
        triple_threat_active=bool(payload.get("triple_threat_active")),
        locomotion_score=float(payload.get("locomotion_score") or 0.0),
        transfer_active=bool(payload.get("transfer_active")),
        transfer_target=str(payload.get("transfer_target") or ""),
        transfer_frames_left=int(payload.get("transfer_frames_left") or 0),
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
        "receipt_id": "ball-state-snapshot-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built ball-state snapshot packet.",
        "refs": [],
        "data": {
            "ball_side": value.get("ball_side", ""),
            "ball_phase": value.get("ball_phase", ""),
            "possession_state": value.get("possession_state", ""),
        },
    }]
