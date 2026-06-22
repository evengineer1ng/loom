from __future__ import annotations

from pathlib import Path
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.shell_manifest_from_oradio_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "📻",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.shell_manifest_from_oradio_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "inspect", "shell", "oradio", "manifest", "projection"],
    "description": "Project an `.oradio` descriptor into the shell-facing manifest shape used by the ribbon shell.",
}


def build_shell_manifest_from_oradio_packet(
    oradio_path: str,
    descriptor: dict[str, Any] | None,
    label: str = "",
) -> dict[str, Any]:
    descriptor_data = dict(descriptor or {})
    station_block = descriptor_data.get("station") if isinstance(descriptor_data.get("station"), dict) else {}
    derived_name = str(label or station_block.get("name") or descriptor_data.get("oradio") or Path(oradio_path).stem)
    return {
        "station": {
            "id": str(descriptor_data.get("oradio") or Path(oradio_path).stem),
            "name": derived_name,
            "description": str(station_block.get("description") or descriptor_data.get("declaration") or ""),
            "category": str(station_block.get("category") or ""),
            "ribbon": str(station_block.get("ribbon") or ""),
        },
        "oradio_path": str(oradio_path),
        "descriptor": descriptor_data,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_shell_manifest_from_oradio_packet(
        oradio_path=str(payload.get("oradio_path") or ""),
        descriptor=dict(payload.get("descriptor") or {}),
        label=str(payload.get("label") or ""),
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
        "receipt_id": "shell-manifest-from-oradio-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built shell manifest-from-oradio packet.",
        "refs": [],
        "data": {
            "oradio_path": value.get("oradio_path", ""),
            "station_id": ((value.get("station") or {}).get("id") or ""),
        },
    }]
