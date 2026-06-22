from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.economy.position_signature_summary_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧬",
    "deterministic": True,
    "inputs": ["runtime.economy_request.v1"],
    "outputs": ["runtime.economy_response.v1"],
    "requires": [],
    "provides": ["runtime.position_signature_summary_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "economy", "positions", "signature", "summary"],
    "description": "Package open-position signature and human summary surfaces for change detection and narrator-facing portfolio descriptions.",
}


def build_position_signature_summary_packet(
    signature: str,
    summary: str,
    positions: list[dict[str, Any]] | None,
    max_positions_in_summary: int,
) -> dict[str, Any]:
    return {
        "signature": str(signature),
        "summary": str(summary),
        "positions": [dict(item) for item in (positions or [])],
        "max_positions_in_summary": int(max_positions_in_summary),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_position_signature_summary_packet(
        signature=str(payload.get("signature") or ""),
        summary=str(payload.get("summary") or ""),
        positions=list(payload.get("positions") or []),
        max_positions_in_summary=int(payload.get("max_positions_in_summary") or 0),
    )
    output_packet = {
        "packet_type": "runtime.economy_response.v1",
        "packet_version": "runtime.economy_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "position-signature-summary-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built position-signature summary packet.",
        "refs": [],
        "data": {
            "signature": value.get("signature", ""),
            "position_count": len(value.get("positions", [])),
            "max_positions_in_summary": value.get("max_positions_in_summary", 0),
        },
    }]
