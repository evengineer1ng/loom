from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.trace.mobile_build_result_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧱",
    "deterministic": True,
    "inputs": ["runtime.trace_request.v1"],
    "outputs": ["runtime.trace_response.v1"],
    "requires": [],
    "provides": ["runtime.mobile_build_result_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "trace", "mobile", "build", "artifact", "delivery"],
    "description": "Package a mobile build result with variant, produced artifact path, and build-output telemetry.",
}


def build_mobile_build_result_packet(
    variant: str,
    artifact_path: str,
    output: str,
    delivery: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "variant": str(variant),
        "artifact_path": str(artifact_path),
        "output": str(output),
        "delivery": dict(delivery or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_mobile_build_result_packet(
        variant=str(payload.get("variant") or ""),
        artifact_path=str(payload.get("artifact_path") or ""),
        output=str(payload.get("output") or ""),
        delivery=dict(payload.get("delivery") or {}),
    )
    output_packet = {
        "packet_type": "runtime.trace_response.v1",
        "packet_version": "runtime.trace_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "mobile-build-result-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built mobile build-result packet.",
        "refs": [],
        "data": {
            "variant": value.get("variant", ""),
            "artifact_path": value.get("artifact_path", ""),
            "has_delivery": bool(value.get("delivery")),
        },
    }]
