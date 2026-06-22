from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "fetch.scout.alert_content_normalization_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🚨",
    "deterministic": True,
    "inputs": ["fetch.scout_request.v1"],
    "outputs": ["fetch.scout_response.v1"],
    "requires": [],
    "provides": ["fetch.alert_content_normalization_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["fetch", "scout", "alert", "normalization", "rss"],
    "description": "Package normalized alert content with cleaned title/body, fallback path, and link-garbage suppression outcome.",
}


def build_alert_content_normalization_packet(
    post_id: str,
    title: str,
    body: str,
    used_content_field: bool,
    used_title_fallback: bool,
    body_was_link_garbage: bool,
) -> dict[str, Any]:
    return {
        "post_id": str(post_id),
        "title": str(title),
        "body": str(body),
        "used_content_field": bool(used_content_field),
        "used_title_fallback": bool(used_title_fallback),
        "body_was_link_garbage": bool(body_was_link_garbage),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_alert_content_normalization_packet(
        post_id=str(payload.get("post_id") or ""),
        title=str(payload.get("title") or ""),
        body=str(payload.get("body") or ""),
        used_content_field=bool(payload.get("used_content_field")),
        used_title_fallback=bool(payload.get("used_title_fallback")),
        body_was_link_garbage=bool(payload.get("body_was_link_garbage")),
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
        "receipt_id": "alert-content-normalization-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built alert content-normalization packet.",
        "refs": [],
        "data": {
            "post_id": value.get("post_id", ""),
            "used_title_fallback": value.get("used_title_fallback", False),
            "body_was_link_garbage": value.get("body_was_link_garbage", False),
        },
    }]
