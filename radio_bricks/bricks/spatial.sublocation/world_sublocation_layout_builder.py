from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "spatial.sublocation.world_sublocation_layout_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧱",
    "deterministic": True,
    "inputs": ["spatial.sublocation_request.v1"],
    "outputs": ["spatial.sublocation_response.v1"],
    "requires": [],
    "provides": ["spatial.world_sublocation_layout_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["spatial", "sublocation", "world", "layout", "assembly"],
    "description": "Package world-level sublocation layout assembly keyed by node id, plus echo/trainer placement inputs used during generation.",
}


def build_world_sublocation_layout_packet(
    seed: int,
    node_ids: list[str] | None,
    echo_node_ids: list[str] | None,
    trainer_node_ids: list[str] | None,
    layouts_by_node: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "seed": int(seed),
        "node_ids": list(node_ids or []),
        "echo_node_ids": list(echo_node_ids or []),
        "trainer_node_ids": list(trainer_node_ids or []),
        "layouts_by_node": dict(layouts_by_node or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_world_sublocation_layout_packet(
        seed=int(payload.get("seed") or 0),
        node_ids=list(payload.get("node_ids") or []),
        echo_node_ids=list(payload.get("echo_node_ids") or []),
        trainer_node_ids=list(payload.get("trainer_node_ids") or []),
        layouts_by_node=dict(payload.get("layouts_by_node") or {}),
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
        "receipt_id": "world-sublocation-layout-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built world-sublocation layout packet.",
        "refs": [],
        "data": {"seed": value.get("seed", 0), "node_count": len(value.get("node_ids", []))},
    }]
