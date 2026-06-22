from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "narrative.fragment.narrative_fragment_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📜",
    "deterministic": True,
    "inputs": ["narrative.fragment_request.v1"],
    "outputs": ["narrative.fragment_response.v1"],
    "requires": [],
    "provides": ["narrative.fragment_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["narrative", "fragment", "lore", "pool", "mountain"],
    "description": "Package a narrative fragment with type, mountain binding, and discovery-facing content metadata.",
}


def build_narrative_fragment_packet(
    fragment_id: str,
    fragment_type: str,
    title: str,
    mountain_code: str,
    text: str,
) -> dict[str, Any]:
    return {
        "fragment_id": fragment_id,
        "fragment_type": fragment_type,
        "title": title,
        "mountain_code": mountain_code,
        "text": text,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_narrative_fragment_packet(
        fragment_id=str(payload.get("fragment_id") or ""),
        fragment_type=str(payload.get("fragment_type") or ""),
        title=str(payload.get("title") or ""),
        mountain_code=str(payload.get("mountain_code") or ""),
        text=str(payload.get("text") or ""),
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
        "receipt_id": "narrative-fragment-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built narrative fragment packet.",
        "refs": [],
        "data": {"fragment_id": value.get("fragment_id", ""), "mountain_code": value.get("mountain_code", "")},
    }]
