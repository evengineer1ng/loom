from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "fetch.http_sync.retrying_signal_sender",
    "kind": "world_operator",
    "version": "0.1.0",
    "deterministic": False,
    "inputs": ["fetch.request.v1"],
    "outputs": ["fetch.response.v1"],
    "requires": [],
    "provides": ["fetch.prepare_retrying_signal_payload"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["fetch", "http", "signal", "retry"],
    "description": "Prepare a signal payload with normalized pair, timestamp, and signal id for retry-capable delivery loops.",
}


def norm_pair(pair: str) -> str:
    return str(pair or "").replace("/", "").replace("-", "").lower()


def prepare_retrying_signal_payload(payload: dict[str, Any] | None, now_iso: str | None = None, signal_id: str | None = None) -> dict[str, Any]:
    row = dict(payload or {})
    if "pair" in row:
        row["pair_raw"] = row["pair"]
        row["pair"] = norm_pair(str(row.get("pair") or ""))
    row["timestamp"] = str(now_iso or datetime.utcnow().isoformat())
    row["signal_id"] = str(signal_id or uuid4())
    return row


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = prepare_retrying_signal_payload(
        payload=dict(payload.get("value") or {}),
        now_iso=payload.get("now_iso"),
        signal_id=payload.get("signal_id"),
    )
    output_packet = {
        "packet_type": "fetch.response.v1",
        "packet_version": "fetch.response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "retrying-signal-payload-prepared",
        "brick_id": CONCEPT["id"],
        "kind": "artifact",
        "label": "Prepared signal payload for retrying sender.",
        "refs": [],
        "data": {"signal_id": value.get("signal_id", ""), "pair": value.get("pair", "")},
    }]
