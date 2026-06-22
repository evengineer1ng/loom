from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.trace.carrier_transition_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🌊",
    "deterministic": True,
    "inputs": ["runtime.trace_request.v1"],
    "outputs": ["runtime.trace_response.v1"],
    "requires": [],
    "provides": ["runtime.carrier_transition_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "trace", "carrier", "transition", "entry", "exit"],
    "description": "Package a deterministic carrier transition build with entry clip, exit clip, edge key, vigor, and render size.",
}


def build_carrier_transition_packet(
    loop_from: str,
    loop_to: str,
    dst_entry: str,
    dst_exit: str,
    edge_key: str,
    vigor: float,
    seconds: float | None,
    size: list[int] | tuple[int, int] | None,
) -> dict[str, Any]:
    return {
        "loop_from": str(loop_from),
        "loop_to": str(loop_to),
        "dst_entry": str(dst_entry),
        "dst_exit": str(dst_exit),
        "edge_key": str(edge_key),
        "vigor": float(vigor),
        "seconds": seconds,
        "size": list(size or []),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_carrier_transition_packet(
        loop_from=str(payload.get("loop_from") or ""),
        loop_to=str(payload.get("loop_to") or ""),
        dst_entry=str(payload.get("dst_entry") or ""),
        dst_exit=str(payload.get("dst_exit") or ""),
        edge_key=str(payload.get("edge_key") or ""),
        vigor=float(payload.get("vigor") or 0.0),
        seconds=payload.get("seconds"),
        size=payload.get("size"),
    )
    output_packet = {
        "packet_type": "runtime.trace_response.v1",
        "packet_version": "runtime.trace_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "carrier-transition-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built carrier transition packet.",
        "refs": [],
        "data": {
            "edge_key": value.get("edge_key", ""),
            "vigor": value.get("vigor", 0.0),
        },
    }]
