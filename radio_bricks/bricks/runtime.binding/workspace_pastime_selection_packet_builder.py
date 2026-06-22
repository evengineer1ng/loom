from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.workspace_pastime_selection_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎟️",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.workspace_pastime_selection_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "workspace", "pastime", "selection"],
    "description": "Package a selected workspace pastime with matched candidate, selection time, and selection reason.",
}


def build_workspace_pastime_selection_packet(
    pastime: dict[str, Any] | None,
    candidate: dict[str, Any] | None,
    selected_at: str,
    selection_reason: str,
) -> dict[str, Any]:
    return {
        "pastime": dict(pastime or {}),
        "candidate": dict(candidate or {}),
        "selected_at": str(selected_at),
        "selection_reason": str(selection_reason),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_workspace_pastime_selection_packet(
        pastime=dict(payload.get("pastime") or {}),
        candidate=dict(payload.get("candidate") or {}),
        selected_at=str(payload.get("selected_at") or ""),
        selection_reason=str(payload.get("selection_reason") or ""),
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
        "receipt_id": "workspace-pastime-selection-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built workspace pastime-selection packet.",
        "refs": [],
        "data": {
            "selected_at": value.get("selected_at", ""),
            "selection_reason": value.get("selection_reason", ""),
        },
    }]
