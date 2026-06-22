from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.trace.plan_revision_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📚",
    "deterministic": True,
    "inputs": ["runtime.trace_request.v1"],
    "outputs": ["runtime.trace_response.v1"],
    "requires": [],
    "provides": ["runtime.plan_revision_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "trace", "plan", "revision", "snapshot", "history"],
    "description": "Package a plan revision record with change type, summary, full snapshot, and derived diff.",
}


def build_plan_revision_packet(
    revision_id: str,
    session_id: str,
    plan_id: str,
    change_type: str,
    summary: str,
    snapshot: dict[str, Any] | None,
    diff: dict[str, Any] | None,
    created_at: str,
) -> dict[str, Any]:
    return {
        "id": str(revision_id),
        "session_id": str(session_id),
        "plan_id": str(plan_id),
        "change_type": str(change_type),
        "summary": str(summary),
        "snapshot": dict(snapshot or {}),
        "diff": dict(diff or {}),
        "created_at": str(created_at),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_plan_revision_packet(
        revision_id=str(payload.get("id") or ""),
        session_id=str(payload.get("session_id") or ""),
        plan_id=str(payload.get("plan_id") or ""),
        change_type=str(payload.get("change_type") or ""),
        summary=str(payload.get("summary") or ""),
        snapshot=dict(payload.get("snapshot") or {}),
        diff=dict(payload.get("diff") or {}),
        created_at=str(payload.get("created_at") or ""),
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
        "receipt_id": "plan-revision-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built plan revision packet.",
        "refs": [],
        "data": {
            "change_type": value.get("change_type", ""),
            "has_diff": bool(value.get("diff")),
        },
    }]
