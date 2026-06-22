from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "fetch.scout.reddit_candidate_projection_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "👽",
    "deterministic": True,
    "inputs": ["fetch.scout_request.v1"],
    "outputs": ["fetch.scout_response.v1"],
    "requires": [],
    "provides": ["fetch.reddit_candidate_projection_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["fetch", "scout", "reddit", "candidate", "engagement"],
    "description": "Package a Reddit post projection with subreddit identity, mode, traction context, body framing, and candidate priority.",
}


def build_reddit_candidate_projection_packet(
    post_id: str,
    subreddit: str,
    title: str,
    body: str,
    author: str,
    score: int,
    comments: int,
    created_utc: float,
    mode: str,
    heur: float,
) -> dict[str, Any]:
    return {
        "post_id": str(post_id),
        "subreddit": str(subreddit),
        "title": str(title),
        "body": str(body),
        "author": str(author),
        "score": int(score),
        "comments": int(comments),
        "created_utc": float(created_utc),
        "mode": str(mode),
        "heur": float(heur),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_reddit_candidate_projection_packet(
        post_id=str(payload.get("post_id") or ""),
        subreddit=str(payload.get("subreddit") or ""),
        title=str(payload.get("title") or ""),
        body=str(payload.get("body") or ""),
        author=str(payload.get("author") or ""),
        score=int(payload.get("score") or 0),
        comments=int(payload.get("comments") or 0),
        created_utc=float(payload.get("created_utc") or 0.0),
        mode=str(payload.get("mode") or ""),
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
        "receipt_id": "reddit-candidate-projection-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built Reddit candidate-projection packet.",
        "refs": [],
        "data": {
            "post_id": value.get("post_id", ""),
            "subreddit": value.get("subreddit", ""),
            "mode": value.get("mode", ""),
        },
    }]
