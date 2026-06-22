from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.transform_router",
    "kind": "router",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.binding_transform_output"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "transform"],
    "description": "Route normalized candidates through declared binding transforms into target input events.",
}


def route_binding_transform(kind: str, candidate: dict[str, Any] | None, scene_from: str = "title") -> dict[str, Any] | None:
    cand = dict(candidate or {})
    ctype = str(cand.get("type") or "")
    if kind == "presence_to_signal":
        if ctype != "presence":
            return None
        return {"intent": "presence", "node": cand.get("title"), "magnitude": cand.get("priority")}
    if kind == "frame_to_observation":
        if ctype != "frame":
            return None
        scene = cand.get("title") if scene_from == "title" else (cand.get("tags") or [None])[-1]
        return {"observation": cand.get("body"), "scene": scene}
    if kind == "presence_to_speech":
        if ctype != "presence":
            return None
        return {"text": f"Someone just entered the {cand.get('title')}."}
    if kind == "action_to_button":
        if ctype != "action":
            return None
        return {"button": cand.get("title")}
    raise KeyError(f"unknown transform kind {kind!r}")


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = route_binding_transform(
        kind=str(payload.get("kind") or ""),
        candidate=dict(payload.get("candidate") or {}),
        scene_from=str(payload.get("scene_from") or "title"),
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


def receipts(value: dict[str, Any] | None) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "transform-router",
        "brick_id": CONCEPT["id"],
        "kind": "routing",
        "label": "Routed binding transform.",
        "refs": [],
        "data": {"emitted": value is not None},
    }]
