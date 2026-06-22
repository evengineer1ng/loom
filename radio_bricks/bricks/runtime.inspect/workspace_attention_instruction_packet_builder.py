from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.workspace_attention_instruction_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧭",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.workspace_attention_instruction_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "inspect", "workspace", "attention", "instruction", "scheduler"],
    "description": "Package a compiled workspace attention instruction with diff entries and scheduler-effect summaries.",
}


def build_workspace_attention_instruction_packet(
    workspace_id: str,
    workspace_name: str,
    instruction: str,
    applied: bool,
    profile: dict[str, Any] | None,
    diff: list[dict[str, Any]] | None,
    scheduler_effects: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "workspace_id": str(workspace_id),
        "workspace_name": str(workspace_name),
        "instruction": str(instruction),
        "applied": bool(applied),
        "profile": dict(profile or {}),
        "diff": [dict(entry) for entry in (diff or [])],
        "scheduler_effects": dict(scheduler_effects or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_workspace_attention_instruction_packet(
        workspace_id=str(payload.get("workspace_id") or ""),
        workspace_name=str(payload.get("workspace_name") or ""),
        instruction=str(payload.get("instruction") or ""),
        applied=bool(payload.get("applied")),
        profile=dict(payload.get("profile") or {}),
        diff=list(payload.get("diff") or []),
        scheduler_effects=dict(payload.get("scheduler_effects") or {}),
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
        "receipt_id": "workspace-attention-instruction-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built workspace attention-instruction packet.",
        "refs": [],
        "data": {
            "workspace_id": value.get("workspace_id", ""),
            "applied": value.get("applied", False),
            "diff_count": len(value.get("diff") or []),
        },
    }]
