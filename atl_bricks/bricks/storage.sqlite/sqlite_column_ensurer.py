from __future__ import annotations

import sqlite3
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "storage.sqlite.column_ensurer",
    "kind": "storage",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["storage.sqlite_request.v1"],
    "outputs": ["storage.sqlite_response.v1"],
    "requires": ["storage.sqlite_connect"],
    "provides": ["storage.sqlite_ensure_column"],
    "side_effects": ["db_write"],
    "ui_slots": [],
    "tags": ["sqlite", "schema", "migration"],
    "description": "Ensure a column exists in a sqlite table and add it if missing.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    missing = [
        field
        for field in ("connection", "table_name", "column_name", "ddl")
        if field not in payload or payload.get(field) in ("", None)
    ]
    if missing:
        return [{"code": "missing_fields", "message": f"Missing payload fields: {', '.join(missing)}"}]
    return []


def ensure_column(conn: sqlite3.Connection, table_name: str, column_name: str, ddl: str) -> bool:
    columns = [row[1] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()]
    if column_name not in columns:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {ddl}")
        return True
    return False


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    added = ensure_column(
        payload["connection"],
        str(payload["table_name"]),
        str(payload["column_name"]),
        str(payload["ddl"]),
    )
    output_packet = {
        "packet_type": "storage.sqlite_response.v1",
        "packet_version": "storage.sqlite_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {
            "table_name": str(payload["table_name"]),
            "column_name": str(payload["column_name"]),
            "added": added,
        },
        "refs": [str(payload["table_name"])],
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
    action = "Added sqlite column." if output_packet["payload"]["added"] else "Column already present."
    return [
        {
            "receipt_id": "sqlite-column-ensured",
            "brick_id": CONCEPT["id"],
            "kind": "schema_change",
            "label": action,
            "refs": output_packet["refs"],
            "data": {
                "table_name": output_packet["payload"]["table_name"],
                "column_name": output_packet["payload"]["column_name"],
                "added": output_packet["payload"]["added"],
            },
        }
    ]
