from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.stt_backend_resolution_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🎙️",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.stt_backend_resolution_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "stt", "whisper", "speech"],
    "description": "Package speech-to-text backend resolution with preferred backend, whisper asset readiness, and fallback eligibility.",
}


def build_stt_backend_resolution_packet(
    requested_backend: str,
    whisper_bin_ready: bool,
    whisper_model_ready: bool,
    whisper_cpp_available: bool,
    speech_recognition_allowed: bool,
    resolved_backend: str,
) -> dict[str, Any]:
    return {
        "requested_backend": str(requested_backend),
        "whisper_bin_ready": bool(whisper_bin_ready),
        "whisper_model_ready": bool(whisper_model_ready),
        "whisper_cpp_available": bool(whisper_cpp_available),
        "speech_recognition_allowed": bool(speech_recognition_allowed),
        "resolved_backend": str(resolved_backend),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_stt_backend_resolution_packet(
        requested_backend=str(payload.get("requested_backend") or ""),
        whisper_bin_ready=bool(payload.get("whisper_bin_ready")),
        whisper_model_ready=bool(payload.get("whisper_model_ready")),
        whisper_cpp_available=bool(payload.get("whisper_cpp_available")),
        speech_recognition_allowed=bool(payload.get("speech_recognition_allowed")),
        resolved_backend=str(payload.get("resolved_backend") or ""),
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
        "receipt_id": "stt-backend-resolution-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built STT backend-resolution packet.",
        "refs": [],
        "data": {
            "requested_backend": value.get("requested_backend", ""),
            "resolved_backend": value.get("resolved_backend", ""),
        },
    }]
