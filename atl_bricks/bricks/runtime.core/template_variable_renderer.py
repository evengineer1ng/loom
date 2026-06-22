from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.core.template_variable_renderer",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.value_request.v1"],
    "outputs": ["runtime.value_response.v1"],
    "requires": [],
    "provides": ["runtime.render_template_vars"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["template", "text", "render"],
    "description": "Replace simple {var} placeholders in text from a flat context dict.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def render_vars(text: str, context: dict[str, Any]) -> str:
    if not isinstance(text, str):
        return ""
    out = text
    for key, value in context.items():
        out = out.replace(f"{{{key}}}", str(value))
    return out


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = input_packet.get("payload", {})
    rendered = render_vars(str(payload.get("text") or ""), dict(payload.get("context") or {}))
    output_packet = {
        "packet_type": "runtime.value_response.v1",
        "packet_version": "runtime.value_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"text": rendered},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "template-vars-rendered",
        "brick_id": CONCEPT["id"],
        "kind": "render",
        "label": "Rendered template variables into text.",
        "refs": [],
        "data": {"length": len(output_packet["payload"]["text"])},
    }]
