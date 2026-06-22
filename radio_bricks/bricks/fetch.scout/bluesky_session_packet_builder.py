from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "fetch.scout.bluesky_session_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "☁️",
    "deterministic": True,
    "inputs": ["fetch.scout_request.v1"],
    "outputs": ["fetch.scout_response.v1"],
    "requires": [],
    "provides": ["fetch.bluesky_session_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["fetch", "scout", "bluesky", "session", "auth"],
    "description": "Package Bluesky session acquisition with cached token reuse, suffix retry behavior, and chosen API base.",
}


def build_bluesky_session_packet(
    identifier: str,
    token_present: bool,
    used_cached_token: bool,
    retried_with_suffix: bool,
    base_url: str,
) -> dict[str, Any]:
    return {
        "identifier": str(identifier),
        "token_present": bool(token_present),
        "used_cached_token": bool(used_cached_token),
        "retried_with_suffix": bool(retried_with_suffix),
        "base_url": str(base_url),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_bluesky_session_packet(
        identifier=str(payload.get("identifier") or ""),
        token_present=bool(payload.get("token_present")),
        used_cached_token=bool(payload.get("used_cached_token")),
        retried_with_suffix=bool(payload.get("retried_with_suffix")),
        base_url=str(payload.get("base_url") or ""),
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
        "receipt_id": "bluesky-session-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built Bluesky-session packet.",
        "refs": [],
        "data": {
            "identifier": value.get("identifier", ""),
            "token_present": value.get("token_present", False),
            "retried_with_suffix": value.get("retried_with_suffix", False),
        },
    }]
