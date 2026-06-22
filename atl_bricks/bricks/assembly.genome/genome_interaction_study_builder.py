from __future__ import annotations

import math
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.genome.interaction_study_builder",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["assembly.catalog_request.v1"],
    "outputs": ["assembly.catalog_response.v1"],
    "requires": [],
    "provides": ["assembly.genome_interaction_study"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "genome", "interaction"],
    "description": "Build pair synergy/antagonism and simple trait correlations from genome evidence and wind-tunnel rows.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    if not isinstance(payload.get("evidence"), list) or not isinstance(payload.get("genomes"), list) or not isinstance(payload.get("tunnel"), list):
        return [{"code": "missing_inputs", "message": "payload.evidence, payload.genomes, and payload.tunnel must be lists."}]
    return []


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def pearson(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 3:
        return None
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0 or dy == 0:
        return None
    return round(num / (dx * dy), 2)


def genome_interaction_study(evidence: list[dict[str, Any]], genomes: list[dict[str, Any]], tunnel: list[dict[str, Any]]) -> dict[str, Any]:
    name_by_slug = {g["slug"]: g["name"] for g in genomes if g.get("slug")}
    combo: dict[tuple[str, str], list[float]] = {}
    for row in evidence:
        en, ex = row.get("entry_key"), row.get("exit_key")
        if en and ex:
            combo.setdefault((str(en), str(ex)), []).append(float(row.get("pnl") or 0))
    if not combo:
        return {"pairs": [], "synergy": [], "antagonism": [], "correlations": [], "n_combos": 0}
    observed = {key: mean(vals) for key, vals in combo.items()}
    global_mean = mean(list(observed.values()))
    entry_marg: dict[str, list[float]] = {}
    exit_marg: dict[str, list[float]] = {}
    for (en, ex), value in observed.items():
        entry_marg.setdefault(en, []).append(value)
        exit_marg.setdefault(ex, []).append(value)
    em = {k: mean(v) for k, v in entry_marg.items()}
    xm = {k: mean(v) for k, v in exit_marg.items()}
    pairs = []
    for (en, ex), obs in observed.items():
        expected = em[en] + xm[ex] - global_mean
        pairs.append({
            "entry": name_by_slug.get(en, en),
            "exit": name_by_slug.get(ex, ex),
            "entry_slug": en,
            "exit_slug": ex,
            "observed": round(obs, 2),
            "expected": round(expected, 2),
            "interaction": round(obs - expected, 2),
            "n": len(combo[(en, ex)]),
        })
    pairs.sort(key=lambda row: row["interaction"], reverse=True)
    entries = [g for g in tunnel if g.get("kind") == "entry"]
    exits = [g for g in tunnel if g.get("kind") == "exit"]
    correlations = []
    r1 = pearson([g["metrics"]["trades_mean"] for g in entries], [g["metrics"]["pnl"] for g in entries]) if entries else None
    if r1 is not None:
        correlations.append({"label": "Entry churn (trades) vs P&L", "r": r1, "n": len(entries)})
    r2 = pearson([g["metrics"]["win_rate"] for g in exits], [g["metrics"]["pnl"] for g in exits]) if exits else None
    if r2 is not None:
        correlations.append({"label": "Exit win-rate vs P&L", "r": r2, "n": len(exits)})
    return {
        "pairs": pairs,
        "synergy": pairs[:5],
        "antagonism": pairs[-5:][::-1],
        "correlations": correlations,
        "global_mean": round(global_mean, 2),
        "n_combos": len(observed),
    }


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    value = genome_interaction_study(list(payload["evidence"]), list(payload["genomes"]), list(payload["tunnel"]))
    output_packet = {
        "packet_type": "assembly.catalog_response.v1",
        "packet_version": "assembly.catalog_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "genome-interaction-study-built",
        "brick_id": CONCEPT["id"],
        "kind": "view_build",
        "label": "Built genome interaction study.",
        "refs": [],
        "data": {"pairs": len(output_packet["payload"].get("pairs", []))},
    }]
