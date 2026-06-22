from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "visual.capture.vision_client_selection_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧿",
    "deterministic": True,
    "inputs": ["visual.capture_request.v1"],
    "outputs": ["visual.capture_response.v1"],
    "requires": [],
    "provides": ["visual.vision_client_selection_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["visual", "capture", "vision", "client", "model"],
    "description": "Package vision-client selection across local and API providers, including endpoint resolution, model choice, and provider family.",
}


def build_vision_client_selection_packet(
    model_type: str,
    provider: str,
    model: str,
    endpoint: str,
    uses_local_runtime: bool,
) -> dict[str, Any]:
    return {
        "model_type": str(model_type),
        "provider": str(provider),
        "model": str(model),
        "endpoint": str(endpoint),
        "uses_local_runtime": bool(uses_local_runtime),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_vision_client_selection_packet(
        model_type=str(payload.get("model_type") or ""),
        provider=str(payload.get("provider") or ""),
        model=str(payload.get("model") or ""),
        endpoint=str(payload.get("endpoint") or ""),
        uses_local_runtime=bool(payload.get("uses_local_runtime")),
    )
    output_packet = {
        "packet_type": "visual.capture_response.v1",
        "packet_version": "visual.capture_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "vision-client-selection-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built vision-client selection packet.",
        "refs": [],
        "data": {
            "provider": value.get("provider", ""),
            "model": value.get("model", ""),
            "uses_local_runtime": value.get("uses_local_runtime", False),
        },
    }]
