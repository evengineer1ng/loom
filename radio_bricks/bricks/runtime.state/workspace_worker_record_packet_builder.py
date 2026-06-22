from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.workspace_worker_record_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "👷",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.workspace_worker_record_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "workspace", "worker", "record"],
    "description": "Package a workspace worker record with candidate types, signal types, queue counts, open-signal counts, and top candidate/signal summaries.",
}


def build_workspace_worker_record_packet(
    name: str,
    label: str,
    description: str,
    candidate_types: list[str] | None,
    signal_types: list[str] | None,
    queue_count: int,
    open_signal_count: int,
    status: str,
    top_candidate: dict[str, Any] | None,
    top_signal: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "name": str(name),
        "label": str(label),
        "description": str(description),
        "candidate_types": [str(item) for item in (candidate_types or [])],
        "signal_types": [str(item) for item in (signal_types or [])],
        "queue_count": int(queue_count),
        "open_signal_count": int(open_signal_count),
        "status": str(status),
        "top_candidate": dict(top_candidate or {}),
        "top_signal": dict(top_signal or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_workspace_worker_record_packet(
        name=str(payload.get("name") or ""),
        label=str(payload.get("label") or ""),
        description=str(payload.get("description") or ""),
        candidate_types=list(payload.get("candidate_types") or []),
        signal_types=list(payload.get("signal_types") or []),
        queue_count=int(payload.get("queue_count") or 0),
        open_signal_count=int(payload.get("open_signal_count") or 0),
        status=str(payload.get("status") or ""),
        top_candidate=dict(payload.get("top_candidate") or {}),
        top_signal=dict(payload.get("top_signal") or {}),
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
        "receipt_id": "workspace-worker-record-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built workspace worker-record packet.",
        "refs": [],
        "data": {
            "name": value.get("name", ""),
            "queue_count": value.get("queue_count", 0),
            "open_signal_count": value.get("open_signal_count", 0),
        },
    }]
