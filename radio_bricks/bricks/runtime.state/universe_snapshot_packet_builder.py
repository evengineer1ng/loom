from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.state.universe_snapshot_packet_builder",
    "kind": "builder",
    "version": "0.1.0",
    "emoji": "🧊",
    "deterministic": True,
    "inputs": ["runtime.state_request.v1"],
    "outputs": ["runtime.state_response.v1"],
    "requires": [],
    "provides": ["runtime.universe_snapshot_packet"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "state", "forkuniverse", "snapshot"],
    "description": "Package a full ForkUniverse authoritative snapshot suitable for deterministic round-trip reload.",
}


def build_universe_snapshot_packet(
    universe_id: str,
    universe_title: str,
    canonical_seed: str,
    ruleset_version: str,
    time: dict[str, Any] | None,
    coefficients: dict[str, float] | None,
    macro_axes: list[dict[str, Any]] | None,
    characters: list[dict[str, Any]] | None,
    relationships: list[dict[str, Any]] | None,
    institutions: list[dict[str, Any]] | None,
    locations: list[dict[str, Any]] | None,
    obligations: list[dict[str, Any]] | None,
    threads: list[dict[str, Any]] | None,
    predictions: dict[str, Any] | None,
    memory: dict[str, Any] | None,
    ledger: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "universe_id": universe_id,
        "universe_title": universe_title,
        "canonical_seed": canonical_seed,
        "ruleset_version": ruleset_version,
        "time": dict(time or {}),
        "coefficients": {str(key): float(value) for key, value in (coefficients or {}).items()},
        "macro_axes": [dict(item) for item in (macro_axes or [])],
        "characters": [dict(item) for item in (characters or [])],
        "relationships": [dict(item) for item in (relationships or [])],
        "institutions": [dict(item) for item in (institutions or [])],
        "locations": [dict(item) for item in (locations or [])],
        "obligations": [dict(item) for item in (obligations or [])],
        "threads": [dict(item) for item in (threads or [])],
        "predictions": dict(predictions or {}),
        "memory": dict(memory or {}),
        "ledger": dict(ledger or {}),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_universe_snapshot_packet(
        universe_id=str(payload.get("universe_id") or ""),
        universe_title=str(payload.get("universe_title") or ""),
        canonical_seed=str(payload.get("canonical_seed") or ""),
        ruleset_version=str(payload.get("ruleset_version") or ""),
        time=dict(payload.get("time") or {}),
        coefficients=dict(payload.get("coefficients") or {}),
        macro_axes=list(payload.get("macro_axes") or []),
        characters=list(payload.get("characters") or []),
        relationships=list(payload.get("relationships") or []),
        institutions=list(payload.get("institutions") or []),
        locations=list(payload.get("locations") or []),
        obligations=list(payload.get("obligations") or []),
        threads=list(payload.get("threads") or []),
        predictions=dict(payload.get("predictions") or {}),
        memory=dict(payload.get("memory") or {}),
        ledger=dict(payload.get("ledger") or {}),
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
        "receipt_id": "universe-snapshot-packet",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built universe-snapshot packet.",
        "refs": [],
        "data": {"universe_id": value.get("universe_id", ""), "thread_count": len(value.get("threads", []))},
    }]
