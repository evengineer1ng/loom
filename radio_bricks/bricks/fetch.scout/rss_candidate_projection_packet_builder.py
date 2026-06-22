from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "fetch.scout.rss_candidate_projection_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📰",
    "deterministic": True,
    "inputs": ["fetch.scout_request.v1"],
    "outputs": ["fetch.scout_response.v1"],
    "requires": [],
    "provides": ["fetch.rss_candidate_projection_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["fetch", "scout", "rss", "candidate", "projection"],
    "description": "Package normalized RSS item projection with cleaned title and summary, source site, publish time, deep-fetch enrichment, and persistent seen-id handling.",
}


def build_rss_candidate_projection_packet(
    post_id: str,
    title: str,
    summary: str,
    source_site: str,
    published_ts: int,
    deep_fetch_used: bool,
) -> dict[str, Any]:
    return {
        "post_id": str(post_id),
        "title": str(title),
        "summary": str(summary),
        "source_site": str(source_site),
        "published_ts": int(published_ts),
        "deep_fetch_used": bool(deep_fetch_used),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_rss_candidate_projection_packet(
        post_id=str(payload.get("post_id") or ""),
        title=str(payload.get("title") or ""),
        summary=str(payload.get("summary") or ""),
        source_site=str(payload.get("source_site") or ""),
        published_ts=int(payload.get("published_ts") or 0),
        deep_fetch_used=bool(payload.get("deep_fetch_used")),
    )
    output_packet = {
        "packet_type": "fetch.scout_response.v1",
        "packet_version": "fetch.scout_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "rss-candidate-projection-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built RSS-candidate projection packet.",
        "refs": [],
        "data": {
            "post_id": value.get("post_id", ""),
            "source_site": value.get("source_site", ""),
            "deep_fetch_used": value.get("deep_fetch_used", False),
        },
    }]
