from __future__ import annotations

import unicodedata
from typing import Any


WINDOW_CONFUSABLES = str.maketrans({
    "А": "A", "В": "B", "Е": "E", "К": "K", "М": "M", "Н": "H", "О": "O", "Р": "P", "С": "C", "Т": "T", "Х": "X", "У": "Y",
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "у": "y", "х": "x", "к": "k", "м": "m", "н": "h", "в": "b", "т": "t",
})

CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.core.window_text_normalizer",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.value_request.v1"],
    "outputs": ["runtime.value_response.v1"],
    "requires": [],
    "provides": ["runtime.normalize_window_text"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["window", "text", "normalize"],
    "description": "Normalize window-title text with NFKC, confusable folding, and casefolding.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def normalize_window_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", str(value or ""))
    normalized = normalized.translate(WINDOW_CONFUSABLES)
    return normalized.casefold().strip()


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = input_packet.get("payload", {})
    value = normalize_window_text(str(payload.get("text") or ""))
    output_packet = {
        "packet_type": "runtime.value_response.v1",
        "packet_version": "runtime.value_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"text": value},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "window-text-normalized",
        "brick_id": CONCEPT["id"],
        "kind": "normalization",
        "label": "Normalized window text.",
        "refs": [],
        "data": {"length": len(output_packet["payload"]["text"])},
    }]
