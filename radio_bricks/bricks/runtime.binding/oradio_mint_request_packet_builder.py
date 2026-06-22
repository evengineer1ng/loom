from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.oradio_mint_request_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🏷️",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.oradio_mint_request_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "oradio", "mint", "request", "kernel"],
    "description": "Package the Bookmark export dialog inputs into a mint request with soulmates, draft bricks, and kernel intent.",
}


def build_oradio_mint_request_packet(
    source_video: str,
    oradio_id: str,
    title: str,
    declaration: str,
    soulmates: dict[str, list[str]] | None,
    bricks: list[str] | None,
    is_kernel: bool,
) -> dict[str, Any]:
    return {
        "source_video": str(source_video),
        "oradio_id": str(oradio_id),
        "title": str(title),
        "declaration": str(declaration),
        "soulmates": {str(key): [str(item) for item in value] for key, value in dict(soulmates or {}).items()},
        "bricks": [str(item) for item in (bricks or [])],
        "is_kernel": bool(is_kernel),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_oradio_mint_request_packet(
        source_video=str(payload.get("source_video") or ""),
        oradio_id=str(payload.get("oradio_id") or ""),
        title=str(payload.get("title") or ""),
        declaration=str(payload.get("declaration") or ""),
        soulmates=dict(payload.get("soulmates") or {}),
        bricks=list(payload.get("bricks") or []),
        is_kernel=bool(payload.get("is_kernel")),
    )
    output_packet = {
        "packet_type": "runtime.binding_response.v1",
        "packet_version": "runtime.binding_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "oradio-mint-request-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built oradio mint-request packet.",
        "refs": [],
        "data": {
            "oradio_id": value.get("oradio_id", ""),
            "is_kernel": value.get("is_kernel", False),
            "brick_count": len(value.get("bricks") or []),
        },
    }]
