from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "music.flow.gpu_selection_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🖥️",
    "deterministic": True,
    "inputs": ["music.flow_request.v1"],
    "outputs": ["music.flow_response.v1"],
    "requires": [],
    "provides": ["music.gpu_selection_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["music", "flow", "gpu", "selection", "runtime"],
    "description": "Package detected GPU inventory and preferred-device selection logic for routing local model workloads.",
}


def build_gpu_selection_packet(
    gpus: list[dict[str, Any]] | None,
    preferred_gpu: dict[str, Any] | None,
    launcher_script_present: bool,
) -> dict[str, Any]:
    return {
        "gpus": [dict(item) for item in (gpus or [])],
        "preferred_gpu": dict(preferred_gpu or {}),
        "launcher_script_present": bool(launcher_script_present),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_gpu_selection_packet(
        gpus=list(payload.get("gpus") or []),
        preferred_gpu=dict(payload.get("preferred_gpu") or {}),
        launcher_script_present=bool(payload.get("launcher_script_present")),
    )
    output_packet = {
        "packet_type": "music.flow_response.v1",
        "packet_version": "music.flow_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "gpu-selection-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built GPU-selection packet.",
        "refs": [],
        "data": {
            "gpu_count": len(value.get("gpus", [])),
            "has_preferred_gpu": bool(value.get("preferred_gpu")),
            "launcher_script_present": value.get("launcher_script_present", False),
        },
    }]
