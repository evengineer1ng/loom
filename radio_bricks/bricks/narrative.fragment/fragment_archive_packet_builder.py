from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "narrative.fragment.fragment_archive_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🗃️",
    "deterministic": True,
    "inputs": ["narrative.fragment_request.v1"],
    "outputs": ["narrative.fragment_response.v1"],
    "requires": [],
    "provides": ["narrative.fragment_archive_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["narrative", "fragment", "archive", "ordering", "read-model"],
    "description": "Package narrator-facing fragment archive output with discovered ordering, rendered titles, and gated body visibility.",
}


def build_fragment_archive_packet(
    total: int,
    discovered: int,
    discovery_order: list[str] | None,
    fragments: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "total": int(total),
        "discovered": int(discovered),
        "discovery_order": list(discovery_order or []),
        "fragments": [dict(fragment) for fragment in (fragments or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_fragment_archive_packet(
        total=int(payload.get("total") or 0),
        discovered=int(payload.get("discovered") or 0),
        discovery_order=list(payload.get("discovery_order") or []),
        fragments=list(payload.get("fragments") or []),
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
        "receipt_id": "fragment-archive-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built fragment-archive packet.",
        "refs": [],
        "data": {"total": value.get("total", 0), "discovered": value.get("discovered", 0)},
    }]
