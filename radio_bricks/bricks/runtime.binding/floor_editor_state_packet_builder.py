from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.floor_editor_state_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎛️",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.floor_editor_state_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "floor", "editor", "state"],
    "description": "Package live floor-editor state with selected label, active field, formula field, tabs, and save status.",
}


def build_floor_editor_state_packet(
    labels: list[str] | None,
    selected_index: int,
    selected_label: str,
    active_field: str,
    formula_field: str,
    tabs: list[str] | None,
    last_save_ok: bool | None,
) -> dict[str, Any]:
    return {
        "labels": [str(item) for item in (labels or [])],
        "selected_index": int(selected_index),
        "selected_label": str(selected_label),
        "active_field": str(active_field),
        "formula_field": str(formula_field),
        "tabs": [str(item) for item in (tabs or [])],
        "last_save_ok": None if last_save_ok is None else bool(last_save_ok),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_floor_editor_state_packet(
        labels=list(payload.get("labels") or []),
        selected_index=int(payload.get("selected_index") or 0),
        selected_label=str(payload.get("selected_label") or ""),
        active_field=str(payload.get("active_field") or ""),
        formula_field=str(payload.get("formula_field") or ""),
        tabs=list(payload.get("tabs") or []),
        last_save_ok=payload.get("last_save_ok"),
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
        "receipt_id": "floor-editor-state-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built floor-editor state packet.",
        "refs": [],
        "data": {
            "selected_label": value.get("selected_label", ""),
            "active_field": value.get("active_field", ""),
            "formula_field": value.get("formula_field", ""),
        },
    }]
