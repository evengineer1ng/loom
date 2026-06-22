from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.binding.repo_plugin_bootstrap_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🌱",
    "deterministic": True,
    "inputs": ["runtime.binding_request.v1"],
    "outputs": ["runtime.binding_response.v1"],
    "requires": [],
    "provides": ["runtime.repo_plugin_bootstrap_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "binding", "bootstrap", "plugins", "paths", "env"],
    "description": "Package the bootstrap roots and environment defaults that make vendored plugin organs importable at runtime.",
}


def build_repo_plugin_bootstrap_packet(
    repo_root: str,
    plugin_roots: list[str] | tuple[str, ...] | None,
    radio_os_root: str,
    radio_os_plugins: str,
) -> dict[str, Any]:
    return {
        "repo_root": str(repo_root),
        "plugin_roots": [str(item) for item in (plugin_roots or [])],
        "radio_os_root": str(radio_os_root),
        "radio_os_plugins": str(radio_os_plugins),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_repo_plugin_bootstrap_packet(
        repo_root=str(payload.get("repo_root") or ""),
        plugin_roots=list(payload.get("plugin_roots") or []),
        radio_os_root=str(payload.get("radio_os_root") or ""),
        radio_os_plugins=str(payload.get("radio_os_plugins") or ""),
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
        "receipt_id": "repo-plugin-bootstrap-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built repo plugin bootstrap packet.",
        "refs": [],
        "data": {
            "repo_root": value.get("repo_root", ""),
            "plugin_root_count": len(value.get("plugin_roots", [])),
        },
    }]
