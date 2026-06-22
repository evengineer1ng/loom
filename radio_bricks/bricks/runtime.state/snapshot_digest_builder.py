from __future__ import annotations

import hashlib
import json
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.snapshot_digest_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🔐",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.snapshot_digest_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "forkuniverse", "digest"],
    "description": "Build a stable digest for a ForkUniverse snapshot to verify deterministic round-trip identity.",
}


def build_snapshot_digest(snapshot: dict[str, Any] | None) -> dict[str, Any]:
    body = json.dumps(dict(snapshot or {}), sort_keys=True, separators=(",", ":"), default=str)
    return {"digest": hashlib.sha256(body.encode("utf-8")).hexdigest()}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_snapshot_digest(snapshot=dict(payload.get("snapshot") or {}))
    output_packet = {
        "packet_type": "runtime.state_response.v1",
        "packet_version": "runtime.state_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "snapshot-digest-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built snapshot-digest packet.",
        "refs": [],
        "data": {"digest": value.get("digest", "")},
    }]
