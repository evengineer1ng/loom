from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.genome.catalog_reader",
    "kind": "storage",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["storage.sqlite_request.v1"],
    "outputs": ["storage.sqlite_response.v1"],
    "requires": [],
    "provides": ["assembly.list_genomes", "assembly.get_genome", "assembly.genome_versions_for"],
    "side_effects": ["db_open", "db_read"],
    "ui_slots": [],
    "tags": ["assembly", "genome", "catalog"],
    "description": "Read genome records and genome version records from the assembly catalog database.",
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


def list_genomes(conn: sqlite3.Connection, genome_kind: str | None = None) -> list[dict[str, Any]]:
    if genome_kind:
        rows = conn.execute(
            "SELECT * FROM genomes WHERE genome_kind = ? ORDER BY family_slug, name",
            (genome_kind,),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM genomes ORDER BY genome_kind, family_slug, name").fetchall()
    return [dict(row) for row in rows]


def get_genome(conn: sqlite3.Connection, slug: str) -> dict[str, Any] | None:
    row = conn.execute("SELECT * FROM genomes WHERE slug = ?", (slug,)).fetchone()
    return dict(row) if row else None


def genome_versions_for(conn: sqlite3.Connection, genome_slug: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT * FROM genome_versions WHERE genome_slug = ? ORDER BY version_number DESC",
        (genome_slug,),
    ).fetchall()
    return [dict(row) for row in rows]


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    db_path = Path(str(payload["db_path"]))
    operation = str(payload.get("operation") or "list_genomes")
    with get_db(db_path) as conn:
        if operation == "get_genome":
            value = get_genome(conn, str(payload.get("slug") or ""))
        elif operation == "genome_versions_for":
            value = genome_versions_for(conn, str(payload.get("genome_slug") or ""))
        else:
            value = list_genomes(conn, str(payload.get("genome_kind") or "") or None)
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
        "receipt_id": "genome-catalog-read",
        "brick_id": CONCEPT["id"],
        "kind": "db_read",
        "label": "Read genome catalog records.",
        "refs": output_packet["refs"],
        "data": {"operation": output_packet["payload"]["operation"]},
    }]
