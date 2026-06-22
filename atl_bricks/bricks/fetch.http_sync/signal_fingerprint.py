from __future__ import annotations

import hashlib
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "fetch.http_sync.signal_fingerprint",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["fetch.http_request.v1"],
    "outputs": ["fetch.http_response.v1"],
    "requires": [],
    "provides": ["fetch.signal_fingerprint"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["signal", "fingerprint", "dedupe"],
    "description": "Create a stable fingerprint for deduplicating queued trading signals.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def fingerprint(signal: dict[str, Any]) -> str:
    key = f"{signal.get('bot')}|{signal.get('pair')}|{signal.get('side')}|{signal.get('action')}|{signal.get('timestamp')}"
    return hashlib.sha256(key.encode()).hexdigest()


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    signal = dict(input_packet.get("payload", {}).get("signal") or {})
    value = fingerprint(signal)
    output_packet = {
        "packet_type": "fetch.http_response.v1",
        "packet_version": "fetch.http_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"fingerprint": value},
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "signal-fingerprint-computed",
        "brick_id": CONCEPT["id"],
        "kind": "dedupe",
        "label": "Computed signal fingerprint.",
        "refs": [],
        "data": {"fingerprint": output_packet["payload"]["fingerprint"]},
    }]
