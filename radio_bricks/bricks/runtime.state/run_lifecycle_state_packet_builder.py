from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.run_lifecycle_state_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🏃",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.run_lifecycle_state_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "run", "lifecycle", "manager"],
    "description": "Package run lifecycle state with run id, session id, status, turn number, max turns, error, and completion timestamps.",
}


def build_run_lifecycle_state_packet(
    run_id: str,
    session_id: str,
    status: str,
    turn_number: int,
    max_turns: int,
    error: str,
    created_at: str,
    completed_at: str,
) -> dict[str, Any]:
    return {
        "run_id": str(run_id),
        "session_id": str(session_id),
        "status": str(status),
        "turn_number": int(turn_number),
        "max_turns": int(max_turns),
        "error": str(error),
        "created_at": str(created_at),
        "completed_at": str(completed_at),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_run_lifecycle_state_packet(
        run_id=str(payload.get("run_id") or ""),
        session_id=str(payload.get("session_id") or ""),
        status=str(payload.get("status") or ""),
        turn_number=int(payload.get("turn_number") or 0),
        max_turns=int(payload.get("max_turns") or 0),
        error=str(payload.get("error") or ""),
        created_at=str(payload.get("created_at") or ""),
        completed_at=str(payload.get("completed_at") or ""),
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
        "receipt_id": "run-lifecycle-state-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built run lifecycle-state packet.",
        "refs": [],
        "data": {
            "status": value.get("status", ""),
            "turn_number": value.get("turn_number", 0),
        },
    }]
