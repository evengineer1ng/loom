from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.brick_manifest_entry_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📇",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.brick_manifest_entry_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "inspect", "brick", "manifest", "entry", "catalog"],
    "description": "Package one brick-manifest entry with family, medium, I/O, capabilities, tags, and availability.",
}


def build_brick_manifest_entry_packet(
    brick_id: str,
    family: str,
    kind: str,
    lang: str,
    emoji: str,
    deterministic: bool,
    inputs: list[str] | None,
    outputs: list[str] | None,
    requires: list[str] | None,
    provides: list[str] | None,
    side_effects: list[str] | None,
    tags: list[str] | None,
    description: str,
    available: bool,
) -> dict[str, Any]:
    return {
        "id": str(brick_id),
        "family": str(family),
        "kind": str(kind),
        "lang": str(lang),
        "emoji": str(emoji),
        "deterministic": bool(deterministic),
        "inputs": [str(item) for item in (inputs or [])],
        "outputs": [str(item) for item in (outputs or [])],
        "requires": [str(item) for item in (requires or [])],
        "provides": [str(item) for item in (provides or [])],
        "side_effects": [str(item) for item in (side_effects or [])],
        "tags": [str(item) for item in (tags or [])],
        "description": str(description),
        "available": bool(available),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_brick_manifest_entry_packet(
        brick_id=str(payload.get("id") or payload.get("brick_id") or ""),
        family=str(payload.get("family") or ""),
        kind=str(payload.get("kind") or ""),
        lang=str(payload.get("lang") or ""),
        emoji=str(payload.get("emoji") or ""),
        deterministic=bool(payload.get("deterministic")),
        inputs=list(payload.get("inputs") or []),
        outputs=list(payload.get("outputs") or []),
        requires=list(payload.get("requires") or []),
        provides=list(payload.get("provides") or []),
        side_effects=list(payload.get("side_effects") or []),
        tags=list(payload.get("tags") or []),
        description=str(payload.get("description") or ""),
        available=bool(payload.get("available")),
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
        "receipt_id": "brick-manifest-entry-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built brick manifest-entry packet.",
        "refs": [],
        "data": {
            "id": value.get("id", ""),
            "lang": value.get("lang", ""),
            "available": value.get("available", False),
        },
    }]
