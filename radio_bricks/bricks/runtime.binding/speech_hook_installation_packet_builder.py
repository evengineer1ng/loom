from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.speech_hook_installation_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪝",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.speech_hook_installation_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "speech", "hook", "install"],
    "description": "Package speech-hook installation state with target runtime, original handler availability, and duplicate-install guard outcome.",
}


def build_speech_hook_installation_packet(
    target_runtime: str,
    original_handler_present: bool,
    hook_already_installed: bool,
    hook_installed_now: bool,
) -> dict[str, Any]:
    return {
        "target_runtime": str(target_runtime),
        "original_handler_present": bool(original_handler_present),
        "hook_already_installed": bool(hook_already_installed),
        "hook_installed_now": bool(hook_installed_now),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_speech_hook_installation_packet(
        target_runtime=str(payload.get("target_runtime") or ""),
        original_handler_present=bool(payload.get("original_handler_present")),
        hook_already_installed=bool(payload.get("hook_already_installed")),
        hook_installed_now=bool(payload.get("hook_installed_now")),
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
        "receipt_id": "speech-hook-installation-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built speech-hook installation packet.",
        "refs": [],
        "data": {
            "target_runtime": value.get("target_runtime", ""),
            "hook_installed_now": value.get("hook_installed_now", False),
        },
    }]
