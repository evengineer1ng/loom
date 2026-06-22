from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.inspect.structural_memory_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧱",
    "deterministic": True,
    "inputs": ["runtime.inspect_request.v1"],
    "outputs": ["runtime.inspect_response.v1"],
    "requires": [],
    "provides": ["runtime.structural_memory_packet"],
    "side_effects": [],
    "ui_slots": ["inspection.structural_memory"],
    "tags": ["runtime", "inspect", "structural_memory", "baseline", "scar", "era"],
    "description": "Package baseline shifts, institutional scars, era history, and sustained trackers into one structural-memory read model.",
}


def build_structural_memory_packet(
    baseline_shifts: list[dict[str, Any]] | None,
    institutional_scars: list[dict[str, Any]] | None,
    era_history: list[dict[str, Any]] | None,
    current_era: str,
    sustained_tracker: dict[str, Any] | None = None,
    net_baselines: dict[str, float] | None = None,
) -> dict[str, Any]:
    return {
        "baseline_shifts": list(baseline_shifts or []),
        "institutional_scars": list(institutional_scars or []),
        "era_history": list(era_history or []),
        "current_era": current_era,
        "sustained_tracker": dict(sustained_tracker or {}),
        "net_baselines": {str(key): float(value) for key, value in (net_baselines or {}).items()},
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_structural_memory_packet(
        baseline_shifts=list(payload.get("baseline_shifts") or []),
        institutional_scars=list(payload.get("institutional_scars") or []),
        era_history=list(payload.get("era_history") or []),
        current_era=str(payload.get("current_era") or ""),
        sustained_tracker=dict(payload.get("sustained_tracker") or {}),
        net_baselines=dict(payload.get("net_baselines") or {}),
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
        "receipt_id": "structural-memory-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built structural-memory inspection packet.",
        "refs": [],
        "data": {"current_era": value.get("current_era", ""), "baseline_shift_count": len(value.get("baseline_shifts", []))},
    }]
