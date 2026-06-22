from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "visual.capture.vision_client_plan_builder",
    "kind": "planner",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["visual.capture_request.v1"],
    "outputs": ["visual.capture_response.v1"],
    "requires": [],
    "provides": ["visual.vision_client_plan"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["visual", "capture", "vision", "client"],
    "description": "Build a vision-client plan for local Ollama or hosted API interpretation from visual model config.",
}


def build_vision_client_plan(config: dict[str, Any] | None) -> dict[str, Any]:
    cfg = dict(config or {})
    model_type = str(cfg.get("model_type") or "local")
    if model_type == "local":
        local_model = str(cfg.get("local_model") or "llava:latest")
        endpoint = local_model if local_model.startswith("http") else "http://localhost:11434"
        model = local_model if not local_model.startswith("http") else "llava:latest"
        return {"client_kind": "ollama", "endpoint": endpoint, "model": model}
    return {
        "client_kind": str(cfg.get("api_provider") or "openai"),
        "endpoint": str(cfg.get("api_endpoint") or ""),
        "model": str(cfg.get("api_model") or "gpt-4-vision-preview"),
        "api_key_present": bool(cfg.get("api_key")),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    value = build_vision_client_plan(dict(input_packet.get("payload") or {}))
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
        "receipt_id": "vision-client-plan",
        "brick_id": CONCEPT["id"],
        "kind": "plan",
        "label": "Built vision client plan.",
        "refs": [],
        "data": {"client_kind": value.get("client_kind", "")},
    }]
