from __future__ import annotations

import base64
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "fetch.http_sync.basic_auth_header",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["fetch.auth_request.v1"],
    "outputs": ["fetch.auth_response.v1"],
    "requires": [],
    "provides": ["fetch.build_basic_auth_header"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["http", "auth", "basic"],
    "description": "Build a HTTP Basic Authorization header from username and password.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    if "username" not in payload or "password" not in payload:
        return [{"code": "missing_credentials", "message": "payload.username and payload.password are required."}]
    return []


def build_auth_header(username: str, password: str) -> dict[str, str]:
    raw = f"{username}:{password}"
    token = base64.b64encode(raw.encode("ascii")).decode("ascii")
    return {"Authorization": f"Basic {token}"}


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    header = build_auth_header(str(payload.get("username", "")), str(payload.get("password", "")))
    output_packet = {
        "packet_type": "fetch.auth_response.v1",
        "packet_version": "fetch.auth_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"headers": header},
        "refs": [],
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
            "receipt_id": "basic-auth-header-built",
            "brick_id": CONCEPT["id"],
            "kind": "header_build",
            "label": "Built HTTP Basic auth header.",
            "refs": [],
            "data": {"header_keys": sorted(output_packet["payload"]["headers"].keys())},
        }
    ]
