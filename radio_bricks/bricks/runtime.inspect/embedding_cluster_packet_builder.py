from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.embedding_cluster_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🫧",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.embedding_cluster_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "inspect", "embedding", "cluster", "analysis"],
    "description": "Package clustering analysis over latent embeddings with chosen method, cluster count, and annotated rows.",
}


def build_embedding_cluster_packet(method: str, n_clusters: int, rows: list[dict[str, Any]] | None) -> dict[str, Any]:
    return {
        "method": str(method),
        "n_clusters": int(n_clusters),
        "rows": [dict(item) for item in (rows or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_embedding_cluster_packet(
        method=str(payload.get("method") or ""),
        n_clusters=int(payload.get("n_clusters") or 0),
        rows=list(payload.get("rows") or []),
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
        "receipt_id": "embedding-cluster-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built embedding-cluster packet.",
        "refs": [],
        "data": {
            "method": value.get("method", ""),
            "row_count": len(value.get("rows", [])),
        },
    }]
