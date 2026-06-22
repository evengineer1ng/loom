from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "fetch.scout.social_feed_item_projection_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🌐",
    "deterministic": True,
    "inputs": ["fetch.scout_request.v1"],
    "outputs": ["fetch.scout_response.v1"],
    "requires": [],
    "provides": ["fetch.social_feed_item_projection_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["fetch", "scout", "social", "feed", "projection"],
    "description": "Package a social-feed item projection with source identity, external id, headline, body, media/engagement metadata, and candidate priority.",
}


def build_social_feed_item_projection_packet(
    source: str,
    external_id: str,
    title: str,
    body: str,
    media_type: str,
    engagement_count: int,
    heur: float,
) -> dict[str, Any]:
    return {
        "source": str(source),
        "external_id": str(external_id),
        "title": str(title),
        "body": str(body),
        "media_type": str(media_type),
        "engagement_count": int(engagement_count),
        "heur": float(heur),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_social_feed_item_projection_packet(
        source=str(payload.get("source") or ""),
        external_id=str(payload.get("external_id") or ""),
        title=str(payload.get("title") or ""),
        body=str(payload.get("body") or ""),
        media_type=str(payload.get("media_type") or ""),
        engagement_count=int(payload.get("engagement_count") or 0),
        heur=float(payload.get("heur") or 0.0),
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
        "receipt_id": "social-feed-item-projection-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built social-feed item projection packet.",
        "refs": [],
        "data": {
            "source": value.get("source", ""),
            "external_id": value.get("external_id", ""),
            "engagement_count": value.get("engagement_count", 0),
        },
    }]
