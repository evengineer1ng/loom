from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.descriptor.oradio_descriptor_reader",
    "kind": "assembler",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["assembly.descriptor_request.v1"],
    "outputs": ["assembly.descriptor_response.v1"],
    "requires": [],
    "provides": ["assembly.oradio_descriptor_bundle"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "descriptor", "oradio"],
    "description": "Normalize an .oradio descriptor into world, telemetry, effector, binding, lens, surface, and club bundles.",
}


def read_oradio_descriptor(spec: dict[str, Any] | None) -> dict[str, Any]:
    data = dict(spec or {})
    worlds = []
    if isinstance(data.get("world"), dict):
        worlds.append(_world_decl(dict(data["world"])))
    for row in data.get("worlds", []) or []:
        if isinstance(row, dict):
            worlds.append(_world_decl(dict(row)))
    telemetry = [_telemetry_decl(dict(row)) for row in (data.get("telemetry", []) or []) if isinstance(row, dict)]
    effectors = [_effector_decl(dict(row)) for row in (data.get("effectors", []) or []) if isinstance(row, dict)]
    bindings = [_binding_decl(dict(row)) for row in (data.get("bindings", []) or []) if isinstance(row, dict)]
    names = [row["name"] for row in worlds] + [row["name"] for row in telemetry] + [row["name"] for row in effectors]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    return {
        "name": data.get("oradio") or data.get("name") or "untitled",
        "worlds": worlds,
        "telemetry": telemetry,
        "effectors": effectors,
        "bindings": bindings,
        "lens": data.get("lens"),
        "surfaces": list(data.get("surfaces", []) or []),
        "club": list(data.get("club", []) or []),
        "loom_notes": dict(data.get("loom_notes") or {}) if isinstance(data.get("loom_notes"), dict) else {},
        "duplicate_names": duplicates,
        "valid_minimum_shape": bool(worlds or telemetry),
    }


def _world_decl(data: dict[str, Any]) -> dict[str, Any]:
    organ = str(data.get("organ") or "")
    return {
        "organ": organ,
        "name": str(data.get("name") or organ),
        "params": {k: v for k, v in data.items() if k not in {"organ", "name"}},
    }


def _telemetry_decl(data: dict[str, Any]) -> dict[str, Any]:
    source = str(data.get("source") or "")
    return {
        "source": source,
        "name": str(data.get("name") or source),
        "binds": data.get("binds"),
        "params": {k: v for k, v in data.items() if k not in {"source", "name", "binds"}},
    }


def _effector_decl(data: dict[str, Any]) -> dict[str, Any]:
    kind = str(data.get("kind") or "")
    return {
        "kind": kind,
        "name": str(data.get("name") or kind),
        "params": {k: v for k, v in data.items() if k not in {"kind", "name"}},
    }


def _binding_decl(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "source": str(data.get("from") or ""),
        "target": str(data.get("to") or ""),
        "transform": str(data.get("transform") or ""),
        "name": str(data.get("name") or ""),
        "params": {k: v for k, v in data.items() if k not in {"from", "to", "transform", "name"}},
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    value = read_oradio_descriptor(dict(input_packet.get("payload") or {}))
    output_packet = {
        "packet_type": "assembly.descriptor_response.v1",
        "packet_version": "assembly.descriptor_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "oradio-descriptor-reader",
        "brick_id": CONCEPT["id"],
        "kind": "assembly",
        "label": "Read .oradio descriptor bundle.",
        "refs": [],
        "data": {"name": value.get("name", ""), "worlds": len(value.get("worlds", [])), "telemetry": len(value.get("telemetry", []))},
    }]
