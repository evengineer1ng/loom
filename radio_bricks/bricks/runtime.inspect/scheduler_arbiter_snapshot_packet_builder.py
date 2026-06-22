from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.scheduler_arbiter_snapshot_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📇",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.scheduler_arbiter_snapshot_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "inspect", "scheduler", "arbiter", "snapshot"],
    "description": "Package an arbiter snapshot with ranked eligible candidates, active runs, attention profile, and selected work for the moment.",
}


def build_scheduler_arbiter_snapshot_packet(
    workspace_id: str,
    selected_candidate: dict[str, Any] | None,
    ranked_candidates: list[dict[str, Any]] | None,
    idle_tier: int,
    active_run_session_ids: list[str] | None,
    attention_profile: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "workspace_id": str(workspace_id),
        "selected_candidate": dict(selected_candidate or {}),
        "ranked_candidates": [dict(item) for item in (ranked_candidates or [])],
        "idle_tier": int(idle_tier),
        "active_run_session_ids": [str(item) for item in (active_run_session_ids or [])],
        "attention_profile": dict(attention_profile or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_scheduler_arbiter_snapshot_packet(
        workspace_id=str(payload.get("workspace_id") or ""),
        selected_candidate=dict(payload.get("selected_candidate") or {}),
        ranked_candidates=list(payload.get("ranked_candidates") or []),
        idle_tier=int(payload.get("idle_tier") or 0),
        active_run_session_ids=list(payload.get("active_run_session_ids") or []),
        attention_profile=dict(payload.get("attention_profile") or {}),
    )
    output_packet = {
        "packet_type": "runtime.inspect_response.v1",
        "packet_version": "runtime.inspect_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "scheduler-arbiter-snapshot-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built scheduler arbiter snapshot packet.",
        "refs": [],
        "data": {
            "workspace_id": value.get("workspace_id", ""),
            "candidate_count": len(value.get("ranked_candidates", [])),
        },
    }]
