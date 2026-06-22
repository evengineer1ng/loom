from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.headless_profile_app_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🖥️",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.headless_profile_app_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "headless", "profile", "launcher"],
    "description": "Package the headless-app launch seam that injects the `--headless` flag before delegating into the profile app main entrypoint.",
}


def build_headless_profile_app_packet(
    forces_headless_flag: bool,
    delegated_entrypoint: str,
    argv_passthrough: bool,
) -> dict[str, Any]:
    return {
        "forces_headless_flag": bool(forces_headless_flag),
        "delegated_entrypoint": str(delegated_entrypoint),
        "argv_passthrough": bool(argv_passthrough),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_headless_profile_app_packet(
        forces_headless_flag=bool(payload.get("forces_headless_flag")),
        delegated_entrypoint=str(payload.get("delegated_entrypoint") or ""),
        argv_passthrough=bool(payload.get("argv_passthrough")),
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
        "receipt_id": "headless-profile-app-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built headless profile-app packet.",
        "refs": [],
        "data": {
            "forces_headless_flag": value.get("forces_headless_flag", False),
            "delegated_entrypoint": value.get("delegated_entrypoint", ""),
        },
    }]
