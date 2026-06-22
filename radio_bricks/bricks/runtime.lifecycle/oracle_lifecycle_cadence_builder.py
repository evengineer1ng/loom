from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.lifecycle.oracle_lifecycle_cadence_builder",
    "kind": "builder",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["runtime.lifecycle_request.v1"],
    "outputs": ["runtime.lifecycle_response.v1"],
    "requires": [],
    "provides": ["runtime.oracle_lifecycle_cadence"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "lifecycle", "oracle", "cadence"],
    "description": "Derive oracle wake/sleep cadence parameters from personality traits.",
}


def build_oracle_lifecycle_cadence(
    severity: float,
    doubt: float,
    charisma: float,
    paranoia: float,
    conviction: float,
) -> dict[str, Any]:
    severity_n = (float(severity) - 5.0) / 45.0
    doubt_n = (float(doubt) - 5.0) / 45.0
    charisma_n = (float(charisma) - 5.0) / 45.0
    paranoia_n = (float(paranoia) - 5.0) / 45.0
    conviction_n = (float(conviction) - 5.0) / 45.0

    sleep_mod = max(0.4, min(1.6, 1.0 - paranoia_n * 0.3 - severity_n * 0.2 + conviction_n * 0.15))
    active_mod = max(0.3, min(2.0, 1.0 + charisma_n * 0.4 - doubt_n * 0.35 - severity_n * 0.1))
    fatigue_factor = max(0.7, min(1.5, 1.0 + doubt_n * 0.2 - conviction_n * 0.1))

    return {
        "wake_interval_mean": 200.0 * sleep_mod,
        "wake_interval_variance": 60.0 * sleep_mod,
        "wake_duration_mean": 80.0 * active_mod,
        "wake_duration_variance": 20.0 * active_mod,
        "ramp_duration": max(5, int(20 + charisma_n * 10 - paranoia_n * 5)),
        "fatigue_factor": fatigue_factor,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_oracle_lifecycle_cadence(
        severity=float(payload.get("severity") or 5.0),
        doubt=float(payload.get("doubt") or 5.0),
        charisma=float(payload.get("charisma") or 5.0),
        paranoia=float(payload.get("paranoia") or 5.0),
        conviction=float(payload.get("conviction") or 5.0),
    )
    output_packet = {
        "packet_type": "runtime.lifecycle_response.v1",
        "packet_version": "runtime.lifecycle_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "oracle-lifecycle-cadence",
        "brick_id": CONCEPT["id"],
        "kind": "build",
        "label": "Built oracle lifecycle cadence packet.",
        "refs": [],
        "data": {"ramp_duration": value.get("ramp_duration", 0)},
    }]
