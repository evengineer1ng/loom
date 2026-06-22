from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.interpretation.plan_revision_diff_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🔎",
    "deterministic": True,
    "inputs": ["math.interpretation_request.v1"],
    "outputs": ["math.interpretation_response.v1"],
    "requires": [],
    "provides": ["math.plan_revision_diff_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "interpretation", "plan", "revision", "diff", "change"],
    "description": "Package the structured diff between plan snapshots, including field changes, item deltas, and next-item movement.",
}


def build_plan_revision_diff_packet(
    changed_fields: list[str] | None,
    item_ids_added: list[str] | None,
    item_ids_removed: list[str] | None,
    item_ids_updated: list[str] | None,
    next_item_changed: bool,
) -> dict[str, Any]:
    return {
        "changed_fields": [str(item) for item in (changed_fields or [])],
        "item_ids_added": [str(item) for item in (item_ids_added or [])],
        "item_ids_removed": [str(item) for item in (item_ids_removed or [])],
        "item_ids_updated": [str(item) for item in (item_ids_updated or [])],
        "next_item_changed": bool(next_item_changed),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_plan_revision_diff_packet(
        changed_fields=list(payload.get("changed_fields") or []),
        item_ids_added=list(payload.get("item_ids_added") or []),
        item_ids_removed=list(payload.get("item_ids_removed") or []),
        item_ids_updated=list(payload.get("item_ids_updated") or []),
        next_item_changed=bool(payload.get("next_item_changed")),
    )
    output_packet = {
        "packet_type": "math.interpretation_response.v1",
        "packet_version": "math.interpretation_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "plan-revision-diff-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built plan revision-diff packet.",
        "refs": [],
        "data": {
            "changed_field_count": len(value.get("changed_fields") or []),
            "next_item_changed": value.get("next_item_changed", False),
        },
    }]
