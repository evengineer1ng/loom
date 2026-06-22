from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "storage.sqlite.connection",
    "kind": "storage",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["storage.sqlite_request.v1"],
    "outputs": ["storage.sqlite_response.v1"],
    "requires": [],
    "provides": ["storage.sqlite_connect"],
    "side_effects": ["db_open"],
    "ui_slots": [],
    "tags": ["sqlite", "database", "connection"],
    "description": "Open a sqlite connection with row access enabled.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    if not input_packet.get("payload", {}).get("db_path"):
        return [{"code": "missing_db_path", "message": "payload.db_path is required."}]
    return []


def get_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    db_path = Path(str(input_packet["payload"]["db_path"]))
    conn = get_db(db_path)
    output_packet = {
        "packet_type": "storage.sqlite_response.v1",
        "packet_version": "storage.sqlite_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"db_path": str(db_path), "connection": conn},
        "refs": [str(db_path)],
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
            "receipt_id": "sqlite-opened",
            "brick_id": CONCEPT["id"],
            "kind": "db_open",
            "label": "Opened sqlite connection.",
            "refs": output_packet["refs"],
            "data": {"db_path": output_packet["payload"]["db_path"]},
        }
    ]
