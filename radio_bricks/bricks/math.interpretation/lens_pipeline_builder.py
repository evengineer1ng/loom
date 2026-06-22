from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "math.interpretation.lens_pipeline_builder",
    "kind": "transformer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["math.interpretation_request.v1"],
    "outputs": ["math.interpretation_response.v1"],
    "requires": [],
    "provides": ["math.lens_pipeline_output"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["math", "interpretation", "lens"],
    "description": "Apply declared lens ops like type filtering, floor priority, boosting, retagging, and capping over normalized candidates.",
}


def apply_lens_pipeline(candidates: list[dict[str, Any]] | None, ops: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    rows = [dict(row) for row in (candidates or [])]
    for op in ops or []:
        name = str((op or {}).get("op") or "")
        if name == "drop_types":
            types = set(str(item) for item in ((op or {}).get("types") or []))
            rows = [row for row in rows if str(row.get("type") or "") not in types]
        elif name == "keep_types":
            types = set(str(item) for item in ((op or {}).get("types") or []))
            rows = [row for row in rows if str(row.get("type") or "") in types]
        elif name == "floor_priority":
            minimum = float((op or {}).get("min") or 0.0)
            rows = [row for row in rows if float(row.get("priority") or 0.0) >= minimum]
        elif name == "boost":
            types = set(str(item) for item in ((op or {}).get("types") or []))
            boost_to = float((op or {}).get("to") or 0.0)
            rows = [{**row, "priority": boost_to} if str(row.get("type") or "") in types else row for row in rows]
        elif name == "retag":
            extra = [str(item) for item in ((op or {}).get("add") or [])]
            rows = [{**row, "tags": list(row.get("tags") or []) + extra} for row in rows]
        elif name == "cap":
            limit = int((op or {}).get("n") or 0)
            rows = sorted(rows, key=lambda row: float(row.get("priority") or 0.0), reverse=True)[:limit]
    return rows


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = apply_lens_pipeline(
        candidates=list(payload.get("candidates") or []),
        ops=list(payload.get("ops") or []),
    )
    output_packet = {
        "packet_type": "math.interpretation_response.v1",
        "packet_version": "math.interpretation_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "lens-pipeline",
        "brick_id": CONCEPT["id"],
        "kind": "transform",
        "label": "Applied lens pipeline.",
        "refs": [],
        "data": {"count": len(value)},
    }]
