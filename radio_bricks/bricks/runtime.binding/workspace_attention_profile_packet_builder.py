from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.workspace_attention_profile_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎚️",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.workspace_attention_profile_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "workspace", "attention", "profile", "policy"],
    "description": "Package a workspace attention profile with mode, budgets, pastime allowances, and rationale fields.",
}


def build_workspace_attention_profile_packet(
    profile_id: str,
    workspace_id: str,
    baseline_priority: int,
    current_attention_level: int,
    mode: str,
    max_idle_budget: int,
    allowed_pastime_types: list[str] | None,
    notification_threshold: str,
    freshness_target: str,
    review_at: str | None,
    expires_at: str | None,
    user_rationale: str,
    created_at: str,
    updated_at: str,
) -> dict[str, Any]:
    return {
        "id": str(profile_id),
        "workspace_id": str(workspace_id),
        "baseline_priority": int(baseline_priority),
        "current_attention_level": int(current_attention_level),
        "mode": str(mode),
        "max_idle_budget": int(max_idle_budget),
        "allowed_pastime_types": [str(item) for item in (allowed_pastime_types or [])],
        "notification_threshold": str(notification_threshold),
        "freshness_target": str(freshness_target),
        "review_at": review_at,
        "expires_at": expires_at,
        "user_rationale": str(user_rationale),
        "created_at": str(created_at),
        "updated_at": str(updated_at),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_workspace_attention_profile_packet(
        profile_id=str(payload.get("id") or ""),
        workspace_id=str(payload.get("workspace_id") or ""),
        baseline_priority=int(payload.get("baseline_priority") or 0),
        current_attention_level=int(payload.get("current_attention_level") or 0),
        mode=str(payload.get("mode") or ""),
        max_idle_budget=int(payload.get("max_idle_budget") or 0),
        allowed_pastime_types=list(payload.get("allowed_pastime_types") or []),
        notification_threshold=str(payload.get("notification_threshold") or ""),
        freshness_target=str(payload.get("freshness_target") or ""),
        review_at=payload.get("review_at"),
        expires_at=payload.get("expires_at"),
        user_rationale=str(payload.get("user_rationale") or ""),
        created_at=str(payload.get("created_at") or ""),
        updated_at=str(payload.get("updated_at") or ""),
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
        "receipt_id": "workspace-attention-profile-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built workspace attention-profile packet.",
        "refs": [],
        "data": {
            "workspace_id": value.get("workspace_id", ""),
            "mode": value.get("mode", ""),
            "baseline_priority": value.get("baseline_priority", 0),
        },
    }]
