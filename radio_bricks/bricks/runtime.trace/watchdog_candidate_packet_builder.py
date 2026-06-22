from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.trace.watchdog_candidate_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🐕",
    "deterministic": True,
    "inputs": ["runtime.trace_request.v1"],
    "outputs": ["runtime.trace_response.v1"],
    "requires": [],
    "provides": ["runtime.watchdog_candidate_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "trace", "watchdog", "candidate", "rollover"],
    "description": "Package a rollover-needed watchdog work candidate with high urgency, low interruptibility, and successor pressure semantics.",
}


def build_watchdog_candidate_packet(
    candidate_id: str,
    session_id: str,
    priority: int,
    urgency: int,
    compute_cost: int,
    interruptibility: str,
    cooldown: int,
    foreground_blocking: bool,
    title: str,
    summary: str,
    metadata: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "candidate_id": str(candidate_id),
        "session_id": str(session_id),
        "priority": int(priority),
        "urgency": int(urgency),
        "compute_cost": int(compute_cost),
        "interruptibility": str(interruptibility),
        "cooldown": int(cooldown),
        "foreground_blocking": bool(foreground_blocking),
        "title": str(title),
        "summary": str(summary),
        "metadata": dict(metadata or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_watchdog_candidate_packet(
        candidate_id=str(payload.get("candidate_id") or ""),
        session_id=str(payload.get("session_id") or ""),
        priority=int(payload.get("priority") or 0),
        urgency=int(payload.get("urgency") or 0),
        compute_cost=int(payload.get("compute_cost") or 0),
        interruptibility=str(payload.get("interruptibility") or ""),
        cooldown=int(payload.get("cooldown") or 0),
        foreground_blocking=bool(payload.get("foreground_blocking")),
        title=str(payload.get("title") or ""),
        summary=str(payload.get("summary") or ""),
        metadata=dict(payload.get("metadata") or {}),
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
        "receipt_id": "watchdog-candidate-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built watchdog candidate packet.",
        "refs": [],
        "data": {
            "session_id": value.get("session_id", ""),
            "foreground_blocking": value.get("foreground_blocking", False),
        },
    }]
