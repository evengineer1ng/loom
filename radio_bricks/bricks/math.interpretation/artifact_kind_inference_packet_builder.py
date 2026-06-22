from __future__ import annotations

from pathlib import Path
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.interpretation.artifact_kind_inference_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧮",
    "deterministic": True,
    "inputs": ["math.interpretation_request.v1"],
    "outputs": ["math.interpretation_response.v1"],
    "requires": [],
    "provides": ["math.artifact_kind_inference_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "interpretation", "artifact", "mime", "extension", "classification"],
    "description": "Infer an artifact kind from filename extension and mime type using deterministic delivery rules.",
}


def build_artifact_kind_inference_packet(file_name: str, mime_type: str) -> dict[str, Any]:
    extension = Path(file_name).suffix.lower()
    normalized_mime_type = str(mime_type or "").lower()
    artifact_kind = "apk" if extension == ".apk" or normalized_mime_type == "application/vnd.android.package-archive" else "binary"
    return {
        "file_name": str(file_name),
        "mime_type": str(mime_type),
        "extension": extension,
        "artifact_kind": artifact_kind,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_artifact_kind_inference_packet(
        file_name=str(payload.get("file_name") or ""),
        mime_type=str(payload.get("mime_type") or ""),
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
        "receipt_id": "artifact-kind-inference-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built artifact-kind inference packet.",
        "refs": [],
        "data": {
            "artifact_kind": value.get("artifact_kind", ""),
            "extension": value.get("extension", ""),
        },
    }]
