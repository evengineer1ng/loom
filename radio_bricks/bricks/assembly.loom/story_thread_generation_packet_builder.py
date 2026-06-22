from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.loom.story_thread_generation_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🪡",
    "deterministic": True,
    "inputs": ["assembly.loom_request.v1"],
    "outputs": ["assembly.loom_response.v1"],
    "requires": [],
    "provides": ["assembly.story_thread_generation_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "loom", "forkuniverse", "thread", "generation"],
    "description": "Package the generated story-thread rows assembled from concept thread prompts, templates, participants, and heat/confidence biases.",
}


def build_story_thread_generation_packet(
    brief_seed: str,
    target_count: int,
    threads: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "brief_seed": brief_seed,
        "target_count": int(target_count),
        "threads": [dict(item) for item in (threads or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_story_thread_generation_packet(
        brief_seed=str(payload.get("brief_seed") or ""),
        target_count=int(payload.get("target_count") or 0),
        threads=list(payload.get("threads") or []),
    )
    output_packet = {
        "packet_type": "assembly.loom_response.v1",
        "packet_version": "assembly.loom_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "story-thread-generation-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built story-thread generation packet.",
        "refs": [],
        "data": {"target_count": value.get("target_count", 0), "row_count": len(value.get("threads", []))},
    }]
