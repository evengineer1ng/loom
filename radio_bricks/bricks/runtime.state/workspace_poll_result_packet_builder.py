from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.workspace_poll_result_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📡",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.workspace_poll_result_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "workspace", "poll", "result"],
    "description": "Package one workspace runtime poll result with candidate pool, selected candidate, selected pastime, and any emitted signal.",
}


def build_workspace_poll_result_packet(
    workspace_id: str,
    candidates: list[dict[str, Any]] | None,
    selected_candidate: dict[str, Any] | None,
    selected_pastime: dict[str, Any] | None,
    emitted_signal: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "workspace_id": str(workspace_id),
        "candidates": [dict(item) for item in (candidates or [])],
        "selected_candidate": dict(selected_candidate or {}),
        "selected_pastime": dict(selected_pastime or {}),
        "emitted_signal": dict(emitted_signal or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_workspace_poll_result_packet(
        workspace_id=str(payload.get("workspace_id") or ""),
        candidates=list(payload.get("candidates") or []),
        selected_candidate=dict(payload.get("selected_candidate") or {}),
        selected_pastime=dict(payload.get("selected_pastime") or {}),
        emitted_signal=dict(payload.get("emitted_signal") or {}),
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
        "receipt_id": "workspace-poll-result-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built workspace poll-result packet.",
        "refs": [],
        "data": {
            "workspace_id": value.get("workspace_id", ""),
            "candidate_count": len(value.get("candidates", [])),
        },
    }]
