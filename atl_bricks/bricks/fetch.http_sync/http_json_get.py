from __future__ import annotations

from typing import Any

import httpx


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "fetch.http_sync.http_json_get",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": False,
    "inputs": ["fetch.http_request.v1"],
    "outputs": ["fetch.http_response.v1"],
    "requires": [],
    "provides": ["fetch.http_json_get"],
    "side_effects": ["network_read"],
    "ui_slots": [],
    "tags": ["http", "json", "get"],
    "description": "Perform an HTTP GET and decode a JSON response body.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    if not payload.get("url"):
        return [{"code": "missing_url", "message": "payload.url is required."}]
    return []


def api_get(client: httpx.Client, url: str, headers: dict[str, str] | None = None, timeout: float = 8.0) -> Any:
    response = client.get(url, headers=headers or {}, timeout=timeout)
    response.raise_for_status()
    return response.json()


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    url = str(payload["url"])
    headers = payload.get("headers") or {}
    timeout = float(payload.get("timeout_seconds") or 8.0)
    with httpx.Client() as client:
        value = api_get(client, url, headers=headers, timeout=timeout)
    output_packet = {
        "packet_type": "fetch.http_response.v1",
        "packet_version": "fetch.http_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"url": url, "json": value},
        "refs": [url],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {
        "ok": True,
        "output_packet": output_packet,
        "receipts": receipts(output_packet),
        "issues": [],
        "meta": {},
    }


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "receipt_id": "http-json-get",
            "brick_id": CONCEPT["id"],
            "kind": "network_read",
            "label": "Fetched JSON over HTTP GET.",
            "refs": output_packet["refs"],
            "data": {"url": output_packet["payload"]["url"]},
        }
    ]
