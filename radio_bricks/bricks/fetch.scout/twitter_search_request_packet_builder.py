from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "fetch.scout.twitter_search_request_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🐦",
    "deterministic": True,
    "inputs": ["fetch.scout_request.v1"],
    "outputs": ["fetch.scout_response.v1"],
    "requires": [],
    "provides": ["fetch.twitter_search_request_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["fetch", "scout", "twitter", "search", "query"],
    "description": "Package a Twitter recent-search request with bearer-token presence, hashtag query, retweet exclusion, and max-results cap.",
}


def build_twitter_search_request_packet(
    hashtag: str,
    query: str,
    max_results: int,
    has_bearer_token: bool,
) -> dict[str, Any]:
    return {
        "hashtag": str(hashtag),
        "query": str(query),
        "max_results": int(max_results),
        "has_bearer_token": bool(has_bearer_token),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_twitter_search_request_packet(
        hashtag=str(payload.get("hashtag") or ""),
        query=str(payload.get("query") or ""),
        max_results=int(payload.get("max_results") or 0),
        has_bearer_token=bool(payload.get("has_bearer_token")),
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
        "receipt_id": "twitter-search-request-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built Twitter search-request packet.",
        "refs": [],
        "data": {
            "hashtag": value.get("hashtag", ""),
            "max_results": value.get("max_results", 0),
            "has_bearer_token": value.get("has_bearer_token", False),
        },
    }]
