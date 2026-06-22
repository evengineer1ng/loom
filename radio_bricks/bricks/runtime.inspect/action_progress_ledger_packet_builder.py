from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.action_progress_ledger_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📋",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.action_progress_ledger_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "inspect", "ledger", "progress", "agent-loop"],
    "description": "Package action-progress ledger state with discovery budget, verification progress, artifacts, and evidence snippets from the agent loop.",
}


def build_action_progress_ledger_packet(
    action_mode: bool,
    discovery_budget: int,
    discovery_steps: int,
    files_read: int,
    symbols_found: int,
    files_modified: int,
    tests_run: int,
    artifacts_created: int,
    evidence: list[str] | None,
) -> dict[str, Any]:
    return {
        "action_mode": bool(action_mode),
        "discovery_budget": int(discovery_budget),
        "discovery_steps": int(discovery_steps),
        "files_read": int(files_read),
        "symbols_found": int(symbols_found),
        "files_modified": int(files_modified),
        "tests_run": int(tests_run),
        "artifacts_created": int(artifacts_created),
        "evidence": [str(item) for item in (evidence or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_action_progress_ledger_packet(
        action_mode=bool(payload.get("action_mode")),
        discovery_budget=int(payload.get("discovery_budget") or 0),
        discovery_steps=int(payload.get("discovery_steps") or 0),
        files_read=int(payload.get("files_read") or 0),
        symbols_found=int(payload.get("symbols_found") or 0),
        files_modified=int(payload.get("files_modified") or 0),
        tests_run=int(payload.get("tests_run") or 0),
        artifacts_created=int(payload.get("artifacts_created") or 0),
        evidence=list(payload.get("evidence") or []),
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
        "receipt_id": "action-progress-ledger-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built action-progress ledger packet.",
        "refs": [],
        "data": {
            "discovery_steps": value.get("discovery_steps", 0),
            "files_modified": value.get("files_modified", 0),
            "tests_run": value.get("tests_run", 0),
        },
    }]
