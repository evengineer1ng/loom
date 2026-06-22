from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "spatial.sublocation.subpage_layout_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🗂️",
    "deterministic": True,
    "inputs": ["spatial.sublocation_request.v1"],
    "outputs": ["spatial.sublocation_response.v1"],
    "requires": [],
    "provides": ["spatial.subpage_layout_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["spatial", "sublocation", "layout", "pages", "r-unit"],
    "description": "Package a full Neikos R-Unit subpage layout with paged sublocations and exit-label metadata.",
}


def build_subpage_layout_packet(
    node_id: str,
    node_name: str,
    mountain: str,
    r_unit_label: str,
    total_pages: int,
    total_sublocations: int,
    exit_count: int,
    pages: list[list[dict[str, Any]]] | None,
    exits: list[dict[str, Any]] | None,
    current_page: int | None = None,
) -> dict[str, Any]:
    packet = {
        "node_id": node_id,
        "node_name": node_name,
        "mountain": mountain,
        "r_unit_label": r_unit_label,
        "total_pages": int(total_pages),
        "total_sublocations": int(total_sublocations),
        "exit_count": int(exit_count),
        "pages": [[dict(item) for item in page] for page in (pages or [])],
        "exits": [dict(item) for item in (exits or [])],
    }
    if current_page is not None:
        packet["current_page"] = int(current_page)
    return packet


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_subpage_layout_packet(
        node_id=str(payload.get("node_id") or ""),
        node_name=str(payload.get("node_name") or ""),
        mountain=str(payload.get("mountain") or ""),
        r_unit_label=str(payload.get("r_unit_label") or ""),
        total_pages=int(payload.get("total_pages") or 0),
        total_sublocations=int(payload.get("total_sublocations") or 0),
        exit_count=int(payload.get("exit_count") or 0),
        pages=list(payload.get("pages") or []),
        exits=list(payload.get("exits") or []),
        current_page=payload.get("current_page"),
    )
    output_packet = {
        "packet_type": "spatial.sublocation_response.v1",
        "packet_version": "spatial.sublocation_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "subpage-layout-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built subpage-layout packet.",
        "refs": [],
        "data": {"node_id": value.get("node_id", ""), "total_pages": value.get("total_pages", 0)},
    }]
