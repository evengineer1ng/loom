from __future__ import annotations

import json
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.genome.graft_compatibility",
    "kind": "scorer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["assembly.compatibility_request.v1"],
    "outputs": ["assembly.compatibility_response.v1"],
    "requires": [],
    "provides": ["assembly.genome_graft_compatibility"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "genome", "compatibility"],
    "description": "Score native, plausible, or incompatible genome grafts from declared indicators and custom data keys.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    if "entry" not in payload or "exit" not in payload:
        return [{"code": "missing_organs", "message": "payload.entry and payload.exit are required."}]
    return []


def genome_json_list(genome: dict[str, Any] | None, field: str) -> list[str]:
    if not genome:
        return []
    try:
        return list(json.loads(genome.get(field) or "[]"))
    except Exception:
        return []


def genome_graft_compatibility(
    entry: dict[str, Any] | None,
    exit_: dict[str, Any] | None,
    mgmt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    organs = [o for o in (entry, exit_, mgmt) if o]
    families = sorted({str(o.get("family_slug") or "") for o in organs if o.get("family_slug")})
    native = len(families) <= 1

    produced_ind = set(genome_json_list(entry, "required_indicators")) if entry else set()
    needed_ind: set[str] = set()
    for o in (exit_, mgmt):
        if o:
            needed_ind |= set(genome_json_list(o, "required_indicators"))
    missing_ind = sorted(needed_ind - produced_ind)

    exit_cd = set(genome_json_list(exit_, "requires_custom_data_keys")) if exit_ else set()
    producers_cd: set[str] = set()
    for o in (entry, mgmt):
        if o:
            producers_cd |= set(genome_json_list(o, "requires_custom_data_keys"))
    missing_cd = sorted(exit_cd - producers_cd)

    findings: list[str] = []
    if native:
        status = "native"
        findings.append("All organs come from one source strategy - native organism, runs as authored.")
    elif missing_ind or missing_cd:
        status = "incompatible"
        if missing_ind:
            findings.append(
                "Exit or management read indicator columns the entry does not produce: "
                + ", ".join(missing_ind) + "."
            )
        if missing_cd:
            findings.append(
                "Exit requires custom_data not maintained by the chosen entry or management: "
                + ", ".join(missing_cd) + "."
            )
    else:
        status = "plausible"
        findings.append(
            "No missing indicator columns or custom_data detected - graft is plausible but unverified."
        )
    return {
        "status": status,
        "native": native,
        "families": families,
        "missing_indicators": missing_ind,
        "missing_custom_data": missing_cd,
        "findings": findings,
    }


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    result = genome_graft_compatibility(payload.get("entry"), payload.get("exit"), payload.get("management"))
    output_packet = {
        "packet_type": "assembly.compatibility_response.v1",
        "packet_version": "assembly.compatibility_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": result,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "genome-graft-compatibility-scored",
        "brick_id": CONCEPT["id"],
        "kind": "analytics",
        "label": "Scored genome graft compatibility.",
        "refs": [],
        "data": {"status": output_packet["payload"]["status"], "native": output_packet["payload"]["native"]},
    }]
