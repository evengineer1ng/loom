from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "runtime.terminal.terminal_outcome_classifier",
    "kind": "classifier",
    "version": "0.1.0",
    "emoji": "⚖️",
    "deterministic": True,
    "inputs": ["runtime.terminal_request.v1"],
    "outputs": ["runtime.terminal_response.v1"],
    "requires": [],
    "provides": ["runtime.terminal_outcome_classification"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["runtime", "terminal", "classifier", "collapse", "outcome"],
    "description": "Classify which terminal outcome is currently eligible from collapse duration, prior resolutions, and threshold conditions.",
}


TERMINAL_OUTCOME_RULES = {
    "REBIRTH_NASCENT": {
        "collapse_duration_min": 200,
        "min_prior_resolutions": 2,
        "conditions": {"labor_pool_max": 35.0},
    },
    "SOVEREIGNTY_LOST": {
        "collapse_duration_min": 200,
        "min_prior_resolutions": 0,
        "conditions": {
            "external_threat_min": 65.0,
            "enforcement_capacity_max": 20.0,
            "institutional_strength_max": 15.0,
        },
    },
    "KINGDOM_FRAGMENTED": {
        "collapse_duration_min": 200,
        "min_prior_resolutions": 0,
        "conditions": {
            "cohesion_max": 15.0,
            "legitimacy_max": 15.0,
            "class_tension_min": 50.0,
        },
    },
}


def classify_terminal_outcome(
    outcome_name: str,
    collapse_duration: int,
    prior_resolutions: int,
    metrics: dict[str, float] | None,
    duration_escalation_per_resolution: int = 150,
) -> dict[str, Any]:
    rule = TERMINAL_OUTCOME_RULES.get(outcome_name, {})
    metrics_map = {str(key): float(value) for key, value in (metrics or {}).items()}
    base_duration = int(rule.get("collapse_duration_min", 0))
    effective_min = base_duration + int(prior_resolutions) * int(duration_escalation_per_resolution)
    checks: list[dict[str, Any]] = []
    eligible = int(prior_resolutions) >= int(rule.get("min_prior_resolutions", 0))
    if int(collapse_duration) < effective_min:
        eligible = False
    for condition_name, threshold in dict(rule.get("conditions") or {}).items():
        metric_name = condition_name.removesuffix("_min").removesuffix("_max")
        actual = float(metrics_map.get(metric_name, 0.0))
        if condition_name.endswith("_min"):
            passed = actual >= float(threshold)
        else:
            passed = actual <= float(threshold)
        checks.append({
            "condition": condition_name,
            "metric": metric_name,
            "threshold": float(threshold),
            "actual": actual,
            "passed": passed,
        })
        if not passed:
            eligible = False
    return {
        "outcome": outcome_name,
        "collapse_duration": int(collapse_duration),
        "prior_resolutions": int(prior_resolutions),
        "effective_min_duration": effective_min,
        "eligible": eligible,
        "checks": checks,
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = classify_terminal_outcome(
        outcome_name=str(payload.get("outcome_name") or ""),
        collapse_duration=int(payload.get("collapse_duration") or 0),
        prior_resolutions=int(payload.get("prior_resolutions") or 0),
        metrics=dict(payload.get("metrics") or {}),
        duration_escalation_per_resolution=int(payload.get("duration_escalation_per_resolution") or 150),
    )
    output_packet = {
        "packet_type": "runtime.terminal_response.v1",
        "packet_version": "runtime.terminal_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "terminal-outcome-classification",
        "brick_id": CONCEPT["id"],
        "kind": "classify",
        "label": "Classified terminal-outcome eligibility.",
        "refs": [],
        "data": {"outcome": value.get("outcome", ""), "eligible": value.get("eligible", False)},
    }]
