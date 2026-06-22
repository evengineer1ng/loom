from __future__ import annotations

import hashlib
import json
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.determinism.stable_request_hash_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧮",
    "deterministic": True,
    "inputs": ["math.determinism_request.v1"],
    "outputs": ["math.determinism_response.v1"],
    "requires": [],
    "provides": ["math.stable_request_hash"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "determinism", "hash", "request"],
    "description": "Build a stable sha256-prefixed hash from a canonical seed, ruleset family, and normalized request payload.",
}


def build_stable_request_hash(canonical_seed: str, ruleset_family: str, request_payload: dict[str, Any] | None) -> dict[str, Any]:
    payload = {
        "canonical_seed": canonical_seed,
        "ruleset_family": ruleset_family,
        "request": dict(request_payload or {}),
    }
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return {
        "hash_input": payload,
        "seed_hash": "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest(),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_stable_request_hash(
        canonical_seed=str(payload.get("canonical_seed") or ""),
        ruleset_family=str(payload.get("ruleset_family") or ""),
        request_payload=dict(payload.get("request_payload") or {}),
    )
    output_packet = {
        "packet_type": "math.determinism_response.v1",
        "packet_version": "math.determinism_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "stable-request-hash",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built stable request hash.",
        "refs": [],
        "data": {"seed_hash": value.get("seed_hash", "")},
    }]
