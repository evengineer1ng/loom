from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.core.file_hasher_sha256",
    "kind": "storage",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["storage.file_request.v1"],
    "outputs": ["storage.file_hash.v1"],
    "requires": [],
    "provides": ["storage.sha256_file"],
    "side_effects": ["file_read"],
    "ui_slots": [],
    "tags": ["file", "hash", "sha256"],
    "description": "Compute the SHA-256 digest of a file.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    if not input_packet.get("payload", {}).get("path"):
        return [{"code": "missing_path", "message": "payload.path is required."}]
    return []


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    path = Path(str(input_packet["payload"]["path"]))
    digest = sha256_file(path)
    output_packet = {
        "packet_type": "storage.file_hash.v1",
        "packet_version": "storage.file_hash.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"path": str(path), "sha256": digest},
        "refs": [str(path)],
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
            "receipt_id": "sha256-file-hashed",
            "brick_id": CONCEPT["id"],
            "kind": "file_read",
            "label": "Computed SHA-256 file digest.",
            "refs": output_packet["refs"],
            "data": {"sha256": output_packet["payload"]["sha256"]},
        }
    ]
