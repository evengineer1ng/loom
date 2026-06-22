from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.judge_synthesis_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📜",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.judge_synthesis_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "inspect", "judge", "synthesis", "brief"],
    "description": "Package the courtroom judge's human-facing synthesis and free-agent brief as separate inspectable surfaces.",
}


def build_judge_synthesis_packet(synthesis: str, brief: str) -> dict[str, Any]:
    return {
        "synthesis": str(synthesis),
        "brief": str(brief),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_judge_synthesis_packet(
        synthesis=str(payload.get("synthesis") or ""),
        brief=str(payload.get("brief") or ""),
    )
    output_packet = {
        "packet_type": "runtime.inspect_response.v1",
        "packet_version": "runtime.inspect_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "judge-synthesis-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built judge synthesis packet.",
        "refs": [],
        "data": {
            "synthesis_length": len(value.get("synthesis", "")),
            "brief_length": len(value.get("brief", "")),
        },
    }]
