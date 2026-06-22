from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "narrative.fragment.fragment_selection_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧩",
    "deterministic": True,
    "inputs": ["narrative.fragment_request.v1"],
    "outputs": ["narrative.fragment_response.v1"],
    "requires": [],
    "provides": ["narrative.fragment_selection_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["narrative", "fragment", "selection", "mountains", "deterministic"],
    "description": "Package deterministic fragment-selection inputs and outputs derived from active mountain codes and seeded shuffling.",
}


def build_fragment_selection_packet(
    active_mountain_codes: list[str] | None,
    relevant_fragment_ids: list[str] | None,
    selection_seed_scope: str,
    selected_limit: int,
    selected_fragment_ids: list[str] | None,
) -> dict[str, Any]:
    return {
        "active_mountain_codes": list(active_mountain_codes or []),
        "relevant_fragment_ids": list(relevant_fragment_ids or []),
        "selection_seed_scope": selection_seed_scope,
        "selected_limit": int(selected_limit),
        "selected_fragment_ids": list(selected_fragment_ids or []),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_fragment_selection_packet(
        active_mountain_codes=list(payload.get("active_mountain_codes") or []),
        relevant_fragment_ids=list(payload.get("relevant_fragment_ids") or []),
        selection_seed_scope=str(payload.get("selection_seed_scope") or "fragment_selection"),
        selected_limit=int(payload.get("selected_limit") or 20),
        selected_fragment_ids=list(payload.get("selected_fragment_ids") or []),
    )
    output_packet = {
        "packet_type": "narrative.fragment_response.v1",
        "packet_version": "narrative.fragment_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "fragment-selection-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built fragment-selection packet.",
        "refs": [],
        "data": {"active_mountain_count": len(value.get("active_mountain_codes", [])), "selected_count": len(value.get("selected_fragment_ids", []))},
    }]
