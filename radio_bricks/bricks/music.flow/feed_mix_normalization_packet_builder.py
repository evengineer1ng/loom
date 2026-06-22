from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "music.flow.feed_mix_normalization_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🥧",
    "deterministic": True,
    "inputs": ["music.flow_request.v1"],
    "outputs": ["music.flow_response.v1"],
    "requires": [],
    "provides": ["music.feed_mix_normalization_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["music", "flow", "mix", "normalization", "weights"],
    "description": "Package feed-mix normalization from raw weights into non-negative airtime fractions suitable for pie and slider sync.",
}


def build_feed_mix_normalization_packet(
    raw_weights: dict[str, Any] | None,
    normalized_weights: dict[str, Any] | None,
    excluded_sources: list[str] | None,
) -> dict[str, Any]:
    return {
        "raw_weights": dict(raw_weights or {}),
        "normalized_weights": dict(normalized_weights or {}),
        "excluded_sources": [str(item) for item in (excluded_sources or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_feed_mix_normalization_packet(
        raw_weights=dict(payload.get("raw_weights") or {}),
        normalized_weights=dict(payload.get("normalized_weights") or {}),
        excluded_sources=list(payload.get("excluded_sources") or []),
    )
    output_packet = {
        "packet_type": "music.flow_response.v1",
        "packet_version": "music.flow_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "feed-mix-normalization-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built feed-mix normalization packet.",
        "refs": [],
        "data": {
            "raw_count": len(value.get("raw_weights", {})),
            "normalized_count": len(value.get("normalized_weights", {})),
            "excluded_count": len(value.get("excluded_sources", [])),
        },
    }]
