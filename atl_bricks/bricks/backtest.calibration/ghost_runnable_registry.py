from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "backtest.calibration.ghost_runnable_registry",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["backtest.sim_request.v1"],
    "outputs": ["backtest.sim_response.v1"],
    "requires": [],
    "provides": ["backtest.ghost_runnable_genomes"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["backtest", "ghost", "registry"],
    "description": "Describe which entry and exit evaluator slugs are runnable in the ghost simulator.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def ghost_runnable_genomes(entry_evaluators: list[str], exit_evaluators: list[str]) -> dict[str, list[str]]:
    return {"entry": sorted(entry_evaluators), "exit": sorted(exit_evaluators) + ["(any -> approximated as stop-only)"]}


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = input_packet.get("payload", {})
    value = ghost_runnable_genomes(list(payload.get("entry_evaluators") or []), list(payload.get("exit_evaluators") or []))
    output_packet = {
        "packet_type": "backtest.sim_response.v1",
        "packet_version": "backtest.sim_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "ghost-runnable-registry-built",
        "brick_id": CONCEPT["id"],
        "kind": "view_build",
        "label": "Built ghost runnable genome registry.",
        "refs": [],
        "data": {"entry": len(output_packet["payload"]["entry"]), "exit": len(output_packet["payload"]["exit"])},
    }]
