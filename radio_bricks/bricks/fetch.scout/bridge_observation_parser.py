from __future__ import annotations

import hashlib
import json
import time
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "fetch.scout.bridge_observation_parser",
    "kind": "parser",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["fetch.scout_request.v1"],
    "outputs": ["fetch.scout_response.v1"],
    "requires": [],
    "provides": ["fetch.scout_observation_candidate"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["fetch", "scout", "bridge", "observation"],
    "description": "Parse a bridge observation line into a normalized scout candidate without assigning airtime value.",
}


def parse_bridge_observation_line(raw_line: str, source: str, default_priority: float) -> dict[str, Any] | None:
    line = (raw_line or "").strip()
    if not line:
        return None
    try:
        payload = json.loads(line)
    except json.JSONDecodeError:
        payload = {"type": "log_line", "body": line}
    if not isinstance(payload, dict):
        payload = {"type": "log_line", "body": str(payload)}
    otype = str(payload.get("type") or "observation").strip() or "observation"
    title = str(payload.get("title") or otype.replace("_", " ")).strip()
    body = str(payload.get("body") or "").strip()
    try:
        priority = float(payload.get("priority")) if payload.get("priority") not in (None, "") else float(default_priority)
    except (ValueError, TypeError):
        priority = float(default_priority)
    try:
        ts = float(payload.get("ts")) if payload.get("ts") not in (None, "") else time.time()
    except (ValueError, TypeError):
        ts = time.time()
    raw_id = str(payload.get("id") or _sha1(f"{source}|{otype}|{title}|{body[:120]}|{ts}"))
    extra_tags = [str(tag) for tag in (payload.get("tags") or []) if isinstance(payload.get("tags"), list)]
    return {
        "post_id": f"{source}:{raw_id}",
        "source": source,
        "title": title[:300],
        "body": body[:2000],
        "priority": priority,
        "ts": ts,
        "type": otype,
        "tags": [source, otype, *extra_tags][:8],
    }


def _sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", "ignore")).hexdigest()[:16]


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = parse_bridge_observation_line(
        raw_line=str(payload.get("raw_line") or ""),
        source=str(payload.get("source") or "scout"),
        default_priority=float(payload.get("default_priority") or 60.0),
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


def receipts(value: dict[str, Any] | None) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "bridge-observation-parser",
        "brick_id": CONCEPT["id"],
        "kind": "parse",
        "label": "Parsed bridge observation line.",
        "refs": [],
        "data": {"parsed": value is not None, "type": None if value is None else value.get("type")},
    }]
