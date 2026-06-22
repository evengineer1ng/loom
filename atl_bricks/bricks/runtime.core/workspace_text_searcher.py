from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.core.workspace_text_searcher",
    "kind": "storage",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["storage.search_request.v1"],
    "outputs": ["storage.search_response.v1"],
    "requires": [],
    "provides": ["storage.search_workspace_files"],
    "side_effects": ["file_read", "directory_walk"],
    "ui_slots": [],
    "tags": ["workspace", "search", "files"],
    "description": "Search a workspace for keyword-matching text-like files and return scored excerpts.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    if not payload.get("project_root"):
        return [{"code": "missing_project_root", "message": "payload.project_root is required."}]
    if not isinstance(payload.get("keywords"), list):
        return [{"code": "missing_keywords", "message": "payload.keywords must be a list."}]
    return []


def read_textish_file(path: Path, max_chars: int = 3000) -> str:
    suffix = path.suffix.lower()
    try:
        if suffix == ".ipynb":
            payload = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
            parts: list[str] = []
            for cell in payload.get("cells", [])[:8]:
                source = cell.get("source", [])
                if isinstance(source, list):
                    parts.append("".join(source))
                elif isinstance(source, str):
                    parts.append(source)
            return "\n".join(parts)[:max_chars]
        return path.read_text(encoding="utf-8", errors="ignore")[:max_chars]
    except Exception:
        return ""


def gather_file_record(path: Path, label: str | None = None, max_chars: int = 2200) -> dict[str, Any]:
    return {
        "label": label or path.name,
        "path": str(path),
        "exists": path.exists(),
        "excerpt": read_textish_file(path, max_chars=max_chars) if path.exists() else "",
    }


def search_workspace_files(project_root: Path, keywords: list[str], limit: int = 6) -> list[dict[str, Any]]:
    allowed_suffixes = {".py", ".json", ".md", ".txt", ".yml", ".yaml", ".ipynb", ".log"}
    skip_parts = {"__pycache__", ".git", ".venv", "node_modules"}
    normalized = [token.lower() for token in keywords if token and len(token) > 2]
    if not normalized:
        return []
    results: list[tuple[int, Path]] = []
    for path in project_root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in skip_parts for part in path.parts):
            continue
        if path.suffix.lower() not in allowed_suffixes:
            continue
        text_target = str(path.relative_to(project_root)).lower()
        score = 0
        for token in normalized:
            if token in text_target:
                score += 4
        if score == 0:
            content = read_textish_file(path, max_chars=2500).lower()
            for token in normalized:
                if token in content:
                    score += 1
        if score:
            results.append((score, path))
    results.sort(key=lambda item: (-item[0], str(item[1])))
    unique: list[dict[str, Any]] = []
    seen: set[str] = set()
    for _, path in results:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        unique.append(gather_file_record(path))
        if len(unique) >= limit:
            break
    return unique


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    root = Path(str(payload["project_root"]))
    keywords = [str(token) for token in payload.get("keywords", [])]
    limit = int(payload.get("limit") or 6)
    records = search_workspace_files(root, keywords, limit=limit)
    output_packet = {
        "packet_type": "storage.search_response.v1",
        "packet_version": "storage.search_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": {"project_root": str(root), "records": records, "count": len(records)},
        "refs": [str(root)],
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
            "receipt_id": "workspace-search-complete",
            "brick_id": CONCEPT["id"],
            "kind": "search",
            "label": "Searched workspace files by keyword.",
            "refs": output_packet["refs"],
            "data": {"count": output_packet["payload"]["count"]},
        }
    ]
