from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.recovery_capsule_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🛟",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.recovery_capsule_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "recovery", "capsule", "governor"],
    "description": "Package a recovery capsule with failure family, blocked strategies, facts, next safe action, recovery note, and mutation freeze state.",
}


def build_recovery_capsule_packet(
    subgoal: str,
    attempt_count: int,
    max_attempts: int,
    failure_family: str,
    blocked_strategies: list[str] | None,
    facts: list[str] | None,
    next_safe_action: str,
    recovery_note: str,
    freeze_mutation: bool,
) -> dict[str, Any]:
    return {
        "subgoal": str(subgoal),
        "attempt_count": int(attempt_count),
        "max_attempts": int(max_attempts),
        "failure_family": str(failure_family),
        "blocked_strategies": [str(item) for item in (blocked_strategies or [])],
        "facts": [str(item) for item in (facts or [])],
        "next_safe_action": str(next_safe_action),
        "recovery_note": str(recovery_note),
        "freeze_mutation": bool(freeze_mutation),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_recovery_capsule_packet(
        subgoal=str(payload.get("subgoal") or ""),
        attempt_count=int(payload.get("attempt_count") or 0),
        max_attempts=int(payload.get("max_attempts") or 0),
        failure_family=str(payload.get("failure_family") or ""),
        blocked_strategies=list(payload.get("blocked_strategies") or []),
        facts=list(payload.get("facts") or []),
        next_safe_action=str(payload.get("next_safe_action") or ""),
        recovery_note=str(payload.get("recovery_note") or ""),
        freeze_mutation=bool(payload.get("freeze_mutation")),
    )
    output_packet = {
        "packet_type": "runtime.binding_response.v1",
        "packet_version": "runtime.binding_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "recovery-capsule-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built recovery capsule packet.",
        "refs": [],
        "data": {
            "subgoal": value.get("subgoal", ""),
            "attempt_count": value.get("attempt_count", 0),
            "freeze_mutation": value.get("freeze_mutation", False),
        },
    }]
