from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.ball_context_evidence_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧭",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.ball_context_evidence_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "ball", "context", "evidence"],
    "description": "Package ball-context evidence with side raw/EMA/context surfaces, side and phase evidence, branch evidence, focus role, and multiplier/blocking state.",
}


def build_ball_context_evidence_packet(
    side_raw: dict[str, float] | None,
    side_ema: dict[str, float] | None,
    side_context: dict[str, float] | None,
    side_evidence: dict[str, float] | None,
    phase_evidence: dict[str, float] | None,
    branch_evidence: dict[str, float] | None,
    focus_label: str,
    focus_role: str,
    focus_multiplier: float,
    focus_blocked: bool,
    bias_strength: float,
) -> dict[str, Any]:
    return {
        "side_raw": {str(k): float(v) for k, v in dict(side_raw or {}).items()},
        "side_ema": {str(k): float(v) for k, v in dict(side_ema or {}).items()},
        "side_context": {str(k): float(v) for k, v in dict(side_context or {}).items()},
        "side_evidence": {str(k): float(v) for k, v in dict(side_evidence or {}).items()},
        "phase_evidence": {str(k): float(v) for k, v in dict(phase_evidence or {}).items()},
        "branch_evidence": {str(k): float(v) for k, v in dict(branch_evidence or {}).items()},
        "focus_label": str(focus_label),
        "focus_role": str(focus_role),
        "focus_multiplier": float(focus_multiplier),
        "focus_blocked": bool(focus_blocked),
        "bias_strength": float(bias_strength),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_ball_context_evidence_packet(
        side_raw=dict(payload.get("side_raw") or {}),
        side_ema=dict(payload.get("side_ema") or {}),
        side_context=dict(payload.get("side_context") or {}),
        side_evidence=dict(payload.get("side_evidence") or {}),
        phase_evidence=dict(payload.get("phase_evidence") or {}),
        branch_evidence=dict(payload.get("branch_evidence") or {}),
        focus_label=str(payload.get("focus_label") or ""),
        focus_role=str(payload.get("focus_role") or ""),
        focus_multiplier=float(payload.get("focus_multiplier") or 0.0),
        focus_blocked=bool(payload.get("focus_blocked")),
        bias_strength=float(payload.get("bias_strength") or 0.0),
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
        "receipt_id": "ball-context-evidence-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built ball-context evidence packet.",
        "refs": [],
        "data": {
            "focus_label": value.get("focus_label", ""),
            "focus_role": value.get("focus_role", ""),
            "focus_blocked": value.get("focus_blocked", False),
        },
    }]
