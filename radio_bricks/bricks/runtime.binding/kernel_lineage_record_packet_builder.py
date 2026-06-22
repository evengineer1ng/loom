from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.kernel_lineage_record_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧬",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.kernel_lineage_record_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "kernel", "lineage", "ancestry", "trust"],
    "description": "Package the lineage record that ties an oradio or kernel to a root kernel, parent kernel, and mint scope.",
}


def build_kernel_lineage_record_packet(
    root_kernel_id: str,
    parent_kernel_id: str,
    issuer_oradio_id: str,
    generation: int,
    mint_scope: str,
) -> dict[str, Any]:
    return {
        "root_kernel_id": str(root_kernel_id),
        "parent_kernel_id": str(parent_kernel_id),
        "issuer_oradio_id": str(issuer_oradio_id),
        "generation": int(generation),
        "mint_scope": str(mint_scope),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_kernel_lineage_record_packet(
        root_kernel_id=str(payload.get("root_kernel_id") or ""),
        parent_kernel_id=str(payload.get("parent_kernel_id") or ""),
        issuer_oradio_id=str(payload.get("issuer_oradio_id") or ""),
        generation=int(payload.get("generation") or 0),
        mint_scope=str(payload.get("mint_scope") or ""),
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
        "receipt_id": "kernel-lineage-record-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built kernel lineage-record packet.",
        "refs": [],
        "data": {
            "root_kernel_id": value.get("root_kernel_id", ""),
            "generation": value.get("generation", 0),
            "mint_scope": value.get("mint_scope", ""),
        },
    }]
