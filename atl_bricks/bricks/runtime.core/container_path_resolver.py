from __future__ import annotations

from pathlib import Path
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.core.container_path_resolver",
    "kind": "bridge",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.io_request.v1"],
    "outputs": ["runtime.io_response.v1"],
    "requires": [],
    "provides": ["runtime.resolve_container_path"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "path", "container"],
    "description": "Resolve relative paths against likely container roots while preserving absolute paths.",
}


def resolve_container_path(raw: str, roots: list[str] | None = None) -> str:
    path = Path(str(raw or ""))
    if path.is_absolute():
        return str(path)
    for root in [Path(item) for item in (roots or ["/freqtrade", str(Path.cwd())])]:
        candidate = root / path
        if candidate.exists():
            return str(candidate)
    return str(Path("/freqtrade") / path)


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = {"path": resolve_container_path(str(payload.get("raw") or ""), roots=[str(item) for item in (payload.get("roots") or [])])}
    output_packet = {
        "packet_type": "runtime.io_response.v1",
        "packet_version": "runtime.io_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    payload = output_packet.get("payload") or {}
    return [{
        "receipt_id": "container-path-resolved",
        "brick_id": CONCEPT["id"],
        "kind": "resolution",
        "label": "Resolved container-relative path.",
        "refs": [],
        "data": {"path": payload.get("path", "")},
    }]
