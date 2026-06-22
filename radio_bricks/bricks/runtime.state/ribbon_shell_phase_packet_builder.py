from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.ribbon_shell_phase_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🖥️",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.ribbon_shell_phase_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "shell", "phase", "ribbon", "theme"],
    "description": "Package the ribbon shell state machine with phase, theme, activity timing, and overlay hint.",
}


def build_ribbon_shell_phase_packet(
    phase: str,
    theme_name: str,
    boot_started: float,
    last_activity: float,
    launch_flash_until: float,
    overlay_alpha_hint: float,
) -> dict[str, Any]:
    return {
        "phase": str(phase),
        "theme_name": str(theme_name),
        "boot_started": float(boot_started),
        "last_activity": float(last_activity),
        "launch_flash_until": float(launch_flash_until),
        "overlay_alpha_hint": float(overlay_alpha_hint),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_ribbon_shell_phase_packet(
        phase=str(payload.get("phase") or ""),
        theme_name=str(payload.get("theme_name") or ""),
        boot_started=float(payload.get("boot_started") or 0.0),
        last_activity=float(payload.get("last_activity") or 0.0),
        launch_flash_until=float(payload.get("launch_flash_until") or 0.0),
        overlay_alpha_hint=float(payload.get("overlay_alpha_hint") or 0.0),
    )
    output_packet = {
        "packet_type": "runtime.state_response.v1",
        "packet_version": "runtime.state_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "ribbon-shell-phase-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built ribbon shell phase packet.",
        "refs": [],
        "data": {
            "phase": value.get("phase", ""),
            "theme_name": value.get("theme_name", ""),
        },
    }]
