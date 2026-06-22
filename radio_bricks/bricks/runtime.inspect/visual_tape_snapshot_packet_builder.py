from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.visual_tape_snapshot_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🫧",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.visual_tape_snapshot_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "inspect", "visual_tape", "snapshot", "family", "energy"],
    "description": "Package a visual tape snapshot with family energy, hue drift, particles, ripples, orbitals, and lineage.",
}


def build_visual_tape_snapshot_packet(
    tick: int,
    entries: int,
    total_energy: float,
    hue_shift: float,
    family_energy: dict[str, float] | None,
    breath: float,
    haze: float,
    zoom: float,
    bloom: float,
    veil: float,
    scanline_alpha: float,
    grain: float,
    glitch: float,
    prism: float,
    particles: list[dict[str, float]] | None,
    ripples: list[dict[str, float]] | None,
    orbitals: list[dict[str, float]] | None,
    lineage: list[list[str]] | None,
) -> dict[str, Any]:
    return {
        "tick": int(tick),
        "entries": int(entries),
        "total_energy": float(total_energy),
        "hue_shift": float(hue_shift),
        "family_energy": {str(key): float(value) for key, value in dict(family_energy or {}).items()},
        "breath": float(breath),
        "haze": float(haze),
        "zoom": float(zoom),
        "bloom": float(bloom),
        "veil": float(veil),
        "scanline_alpha": float(scanline_alpha),
        "grain": float(grain),
        "glitch": float(glitch),
        "prism": float(prism),
        "particles": [dict(item) for item in (particles or [])],
        "ripples": [dict(item) for item in (ripples or [])],
        "orbitals": [dict(item) for item in (orbitals or [])],
        "lineage": [list(item) for item in (lineage or [])],
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_visual_tape_snapshot_packet(
        tick=int(payload.get("tick") or 0),
        entries=int(payload.get("entries") or 0),
        total_energy=float(payload.get("total_energy") or 0.0),
        hue_shift=float(payload.get("hue_shift") or 0.0),
        family_energy=dict(payload.get("family_energy") or {}),
        breath=float(payload.get("breath") or 0.0),
        haze=float(payload.get("haze") or 0.0),
        zoom=float(payload.get("zoom") or 0.0),
        bloom=float(payload.get("bloom") or 0.0),
        veil=float(payload.get("veil") or 0.0),
        scanline_alpha=float(payload.get("scanline_alpha") or 0.0),
        grain=float(payload.get("grain") or 0.0),
        glitch=float(payload.get("glitch") or 0.0),
        prism=float(payload.get("prism") or 0.0),
        particles=list(payload.get("particles") or []),
        ripples=list(payload.get("ripples") or []),
        orbitals=list(payload.get("orbitals") or []),
        lineage=list(payload.get("lineage") or []),
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
        "receipt_id": "visual-tape-snapshot-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built visual tape snapshot packet.",
        "refs": [],
        "data": {
            "tick": value.get("tick", 0),
            "entries": value.get("entries", 0),
        },
    }]
