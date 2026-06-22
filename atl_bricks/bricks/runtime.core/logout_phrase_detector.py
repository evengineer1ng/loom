from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.core.logout_phrase_detector",
    "kind": "analyzer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.analysis_request.v1"],
    "outputs": ["runtime.analysis_response.v1"],
    "requires": [],
    "provides": ["runtime.detect_logout_phrase"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "ocr", "watchdog", "phrase"],
    "description": "Scan OCR detections for logout or reconnect phrases with a confidence threshold.",
}


DEFAULT_LOGOUT_PHRASES = [
    "log in",
    "sign in",
    "session expired",
    "reconnect",
    "please login",
    "logged out",
]


def detect_logout_phrase(results: list[dict[str, Any]] | None, phrases: list[str] | None = None, min_confidence: float = 0.5) -> dict[str, Any]:
    phrase_list = [str(item).strip().lower() for item in (phrases or DEFAULT_LOGOUT_PHRASES) if str(item).strip()]
    for item in (results or []):
        text = str(item.get("text", "")).strip()
        lowered = text.lower()
        confidence = float(item.get("confidence", item.get("conf", 0.0)) or 0.0)
        for phrase in phrase_list:
            if phrase in lowered and confidence >= min_confidence:
                return {"matched": True, "phrase": phrase, "text": text, "confidence": confidence}
    return {"matched": False, "phrase": "", "text": "", "confidence": 0.0}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = detect_logout_phrase(
        results=[dict(item) for item in (payload.get("results") or []) if isinstance(item, dict)],
        phrases=[str(item) for item in (payload.get("phrases") or DEFAULT_LOGOUT_PHRASES)],
        min_confidence=float(payload.get("min_confidence", 0.5) or 0.5),
    )
    output_packet = {
        "packet_type": "runtime.analysis_response.v1",
        "packet_version": "runtime.analysis_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    payload = output_packet.get("payload") or {}
    return [{
        "receipt_id": "logout-phrase-scan",
        "brick_id": CONCEPT["id"],
        "kind": "analysis",
        "label": "Scanned OCR results for logout phrases.",
        "refs": [],
        "data": {"matched": bool(payload.get("matched")), "phrase": payload.get("phrase", "")},
    }]
