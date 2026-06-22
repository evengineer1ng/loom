from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.genome.assembly_catalog_reader",
    "kind": "storage",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["storage.sqlite_request.v1"],
    "outputs": ["storage.sqlite_response.v1"],
    "requires": [],
    "provides": ["assembly.list_assemblies", "assembly.get_assembly", "assembly.compiled_artifact_get"],
    "side_effects": ["db_open", "db_read"],
    "ui_slots": [],
    "tags": ["assembly", "catalog", "artifact"],
    "description": "Read assembly records and compiled artifact records from the assembly catalog database.",
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


def list_assemblies(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute("SELECT * FROM team_assemblies ORDER BY display_name").fetchall()
    return [dict(row) for row in rows]


def get_assembly(conn: sqlite3.Connection, slug: str) -> dict[str, Any] | None:
    row = conn.execute("SELECT * FROM team_assemblies WHERE slug = ?", (slug,)).fetchone()
    return dict(row) if row else None


def assembly_for_team(conn: sqlite3.Connection, team_id: str) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT * FROM team_assemblies WHERE slug = ? OR source_team_id = ? LIMIT 1",
        (team_id, team_id),
    ).fetchone()
    return dict(row) if row else None


def compiled_artifact_get(conn: sqlite3.Connection, artifact_id: int | None) -> dict[str, Any] | None:
    if not artifact_id:
        return None
    row = conn.execute("SELECT * FROM compiled_artifacts WHERE id = ?", (int(artifact_id),)).fetchone()
    return dict(row) if row else None


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    db_path = Path(str(payload["db_path"]))
    operation = str(payload.get("operation") or "list_assemblies")
    with get_db(db_path) as conn:
        if operation == "get_assembly":
            value = get_assembly(conn, str(payload.get("slug") or ""))
        elif operation == "assembly_for_team":
            value = assembly_for_team(conn, str(payload.get("team_id") or ""))
        elif operation == "compiled_artifact_get":
            value = compiled_artifact_get(conn, payload.get("artifact_id"))
        else:
            value = list_assemblies(conn)
    output_packet = {
        "packet_type": "storage.sqlite_response.v1",
        "packet_version": "storage.sqlite_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"operation": operation, "value": value},
        "refs": [str(db_path)],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "assembly-catalog-read",
        "brick_id": CONCEPT["id"],
        "kind": "db_read",
        "label": "Read assembly catalog records.",
        "refs": output_packet["refs"],
        "data": {"operation": output_packet["payload"]["operation"]},
    }]
