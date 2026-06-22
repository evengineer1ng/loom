from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.embedding_dataset_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪟",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.embedding_dataset_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "inspect", "embedding", "dataset", "windows"],
    "description": "Package embedded dataset rows with latent coordinates, labels, take ids, and window starts for downstream analysis.",
}


def build_embedding_dataset_packet(rows: list[dict[str, Any]] | None) -> dict[str, Any]:
    return {"rows": [dict(item) for item in (rows or [])]}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_embedding_dataset_packet(rows=list(payload.get("rows") or []))
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
        "receipt_id": "embedding-dataset-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built embedding-dataset packet.",
        "refs": [],
        "data": {
            "row_count": len(value.get("rows", [])),
        },
    }]
