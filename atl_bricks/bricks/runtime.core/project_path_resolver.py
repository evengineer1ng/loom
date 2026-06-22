from __future__ import annotations

from pathlib import Path
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.core.project_path_resolver",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.path_request.v1"],
    "outputs": ["runtime.path_response.v1"],
    "requires": [],
    "provides": ["runtime.resolve_project_path"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["path", "filesystem", "project"],
    "description": "Resolve optional relative paths against a provided project root.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    if "path" not in payload:
        return [{"code": "missing_path", "message": "payload.path is required."}]
    if not payload.get("project_root"):
        return [{"code": "missing_project_root", "message": "payload.project_root is required."}]
    return []


def resolve_path(path_str: str | None, project_root: Path) -> Path | None:
    if not path_str:
        return None
    path = Path(path_str)
    if not path.is_absolute():
        path = project_root / path
    return path


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    resolved = resolve_path(str(payload.get("path") or ""), Path(str(payload["project_root"])))
    output_packet = {
        "packet_type": "runtime.path_response.v1",
        "packet_version": "runtime.path_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"resolved_path": str(resolved) if resolved else ""},
        "refs": [str(resolved)] if resolved else [],
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
            "receipt_id": "project-path-resolved",
            "brick_id": CONCEPT["id"],
            "kind": "path_resolution",
            "label": "Resolved path against project root.",
            "refs": output_packet["refs"],
            "data": {"resolved_path": output_packet["payload"]["resolved_path"]},
        }
    ]
