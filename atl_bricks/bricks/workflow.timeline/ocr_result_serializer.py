from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "workflow.timeline.ocr_result_serializer",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["workflow.timeline_request.v1"],
    "outputs": ["workflow.timeline_response.v1"],
    "requires": [],
    "provides": ["workflow.serialize_ocr_results"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["workflow", "ocr", "serialization"],
    "description": "Serialize OCR tuples into stable JSON-ready result objects.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def serialize_ocr_results(results: list[Any]) -> list[dict[str, Any]]:
    serialized: list[dict[str, Any]] = []
    for bbox, text, conf in results:
        serialized.append({
            "text": str(text),
            "confidence": float(conf),
            "bbox": [[int(point[0]), int(point[1])] for point in bbox],
        })
    return serialized


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = input_packet.get("payload", {})
    value = serialize_ocr_results(list(payload.get("value") or []))
    output_packet = {
        "packet_type": "workflow.timeline_response.v1",
        "packet_version": "workflow.timeline_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"value": value},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "ocr-results-serialized",
        "brick_id": CONCEPT["id"],
        "kind": "conversion",
        "label": "Serialized OCR results.",
        "refs": [],
        "data": {"count": len(output_packet["payload"]["value"])},
    }]
