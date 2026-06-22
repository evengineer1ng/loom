from __future__ import annotations

import hashlib
import json
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.determinism.forkuniverse_canonical_seed_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🌱",
    "deterministic": True,
    "inputs": ["math.determinism_request.v1"],
    "outputs": ["math.determinism_response.v1"],
    "requires": [],
    "provides": ["math.forkuniverse_canonical_seed"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "determinism", "forkuniverse", "seed"],
    "description": "Build the ForkUniverse canonical seed from either an explicit custom seed or a stable request digest.",
}


def build_forkuniverse_canonical_seed(seed_mode: str, custom_seed: str, stable_request: dict[str, Any] | None) -> dict[str, Any]:
    custom = custom_seed.strip()
    if seed_mode in {"preset", "custom"} and custom:
        canonical_seed = custom
        source = "explicit"
    else:
        body = json.dumps(dict(stable_request or {}), sort_keys=True, separators=(",", ":"))
        canonical_seed = hashlib.sha256(body.encode("utf-8")).hexdigest()[:24]
        source = "derived"
    return {
        "seed_mode": seed_mode,
        "custom_seed": custom,
        "stable_request": dict(stable_request or {}),
        "canonical_seed": canonical_seed,
        "source": source,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_forkuniverse_canonical_seed(
        seed_mode=str(payload.get("seed_mode") or ""),
        custom_seed=str(payload.get("custom_seed") or ""),
        stable_request=dict(payload.get("stable_request") or {}),
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
        "receipt_id": "forkuniverse-canonical-seed",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built ForkUniverse canonical seed.",
        "refs": [],
        "data": {"canonical_seed": value.get("canonical_seed", ""), "source": value.get("source", "")},
    }]
