from __future__ import annotations

import hashlib
import random
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.determinism.seeded_rng_fork",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.determinism_request.v1"],
    "outputs": ["math.determinism_response.v1"],
    "requires": [],
    "provides": ["math.seeded_rng_fork"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "determinism", "rng", "fork"],
    "description": "Fork a deterministic random stream from a master seed and a namespace label.",
}


def fork_seeded_rng(seed: int, label: str, sample_count: int = 3) -> dict[str, Any]:
    h = hashlib.sha256(f"{int(seed)}:{label}".encode()).hexdigest()
    fork_seed = int(h[:16], 16)
    rng = random.Random(fork_seed)
    return {"seed": int(seed), "label": label, "fork_seed": fork_seed, "sample": [rng.random() for _ in range(max(int(sample_count), 0))]}


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = fork_seeded_rng(
        seed=int(payload.get("seed") or 0),
        label=str(payload.get("label") or ""),
        sample_count=int(payload.get("sample_count") or 3),
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
        "receipt_id": "seeded-rng-fork",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built seeded RNG fork.",
        "refs": [],
        "data": {"fork_seed": value.get("fork_seed", 0)},
    }]
