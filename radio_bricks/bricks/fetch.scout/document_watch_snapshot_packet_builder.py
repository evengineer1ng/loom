from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "fetch.scout.document_watch_snapshot_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📄",
    "deterministic": True,
    "inputs": ["fetch.scout_request.v1"],
    "outputs": ["fetch.scout_response.v1"],
    "requires": [],
    "provides": ["fetch.document_watch_snapshot_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["fetch", "scout", "document", "watch", "snapshot"],
    "description": "Package a watched-document snapshot with logical name, path, text hash, character cap, and change timestamp.",
}


def build_document_watch_snapshot_packet(
    name: str,
    path: str,
    text_hash: str,
    updated_ts: int,
    max_chars: int,
) -> dict[str, Any]:
    return {
        "name": str(name),
        "path": str(path),
        "text_hash": str(text_hash),
        "updated_ts": int(updated_ts),
        "max_chars": int(max_chars),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_document_watch_snapshot_packet(
        name=str(payload.get("name") or ""),
        path=str(payload.get("path") or ""),
        text_hash=str(payload.get("text_hash") or ""),
        updated_ts=int(payload.get("updated_ts") or 0),
        max_chars=int(payload.get("max_chars") or 0),
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
        "receipt_id": "document-watch-snapshot-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built document watch-snapshot packet.",
        "refs": [],
        "data": {
            "name": value.get("name", ""),
            "path": value.get("path", ""),
            "updated_ts": value.get("updated_ts", 0),
        },
    }]
