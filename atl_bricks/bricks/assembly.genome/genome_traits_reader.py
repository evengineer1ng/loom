from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.genome.traits_reader",
    "kind": "storage",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["storage.sqlite_request.v1"],
    "outputs": ["storage.sqlite_response.v1"],
    "requires": [],
    "provides": ["assembly.genome_traits_for"],
    "side_effects": ["db_open", "db_read"],
    "ui_slots": [],
    "tags": ["assembly", "genome", "traits"],
    "description": "Read stored genome trait rows for a genome slug.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    missing = [field for field in ("db_path", "slug") if not payload.get(field)]
    if missing:
        return [{"code": "missing_fields", "message": f"Missing payload fields: {', '.join(missing)}"}]
    return []


def get_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def genome_traits_for(conn: sqlite3.Connection, slug: str) -> list[dict[str, Any]]:
    rows = conn.execute("SELECT * FROM genome_traits WHERE genome_slug = ? ORDER BY trait", (slug,)).fetchall()
    return [dict(row) for row in rows]


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    db_path = Path(str(payload["db_path"]))
    with get_db(db_path) as conn:
        value = genome_traits_for(conn, str(payload["slug"]))
    output_packet = {
        "packet_type": "storage.sqlite_response.v1",
        "packet_version": "storage.sqlite_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"value": value},
        "refs": [str(db_path)],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "genome-traits-read",
        "brick_id": CONCEPT["id"],
        "kind": "db_read",
        "label": "Read genome traits.",
        "refs": output_packet["refs"],
        "data": {"count": len(output_packet["payload"]["value"])},
    }]
