from __future__ import annotations

from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "assembly.genome.wind_tunnel_builder",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["assembly.catalog_request.v1"],
    "outputs": ["assembly.catalog_response.v1"],
    "requires": [],
    "provides": ["assembly.genome_wind_tunnel"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["assembly", "genome", "wind-tunnel"],
    "description": "Aggregate genome evidence into wind-tunnel metrics and derived trait tags.",
}


def inspect() -> dict[str, Any]:
    return CONCEPT


def validate(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    payload = input_packet.get("payload", {})
    if not isinstance(payload.get("evidence"), list) or not isinstance(payload.get("genomes"), list):
        return [{"code": "missing_inputs", "message": "payload.evidence and payload.genomes must be lists."}]
    return []


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def derive_genome_traits(kind: str, metrics: dict[str, float]) -> list[dict[str, str]]:
    traits: list[dict[str, str]] = []
    if metrics["pnl"] > 0 and metrics["win_rate"] >= 55:
        traits.append({"trait": "Reliable Winner", "polarity": "favorable"})
    if metrics["avg_roi"] > 1.0:
        traits.append({"trait": "High ROI", "polarity": "favorable"})
    if metrics["trades_mean"] >= 20:
        traits.append({"trait": "High Churn", "polarity": "neutral"})
    if metrics["avg_hold"] >= 240:
        traits.append({"trait": "Long Hold", "polarity": "neutral"})
    if metrics["max_dd"] >= 10:
        traits.append({"trait": "Drawdown-Heavy", "polarity": "unfavorable"})
    if kind == "management" and metrics["max_dd"] < 5:
        traits.append({"trait": "Risk Dampener", "polarity": "favorable"})
    return traits


def genome_wind_tunnel(evidence: list[dict[str, Any]], genomes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    name_by_slug = {g["slug"]: g for g in genomes if g.get("slug")}
    by_genome: dict[str, dict[str, Any]] = {}
    for row in evidence:
        for kind in ("entry", "exit", "management"):
            slug = row.get(f"{kind}_key")
            if not slug:
                continue
            agg = by_genome.setdefault(slug, {"kind": kind, "pnl": [], "win_rate": [], "avg_roi": [], "trades": [], "max_dd": [], "avg_hold": [], "tiers": set()})
            agg["pnl"].append(float(row.get("pnl") or 0))
            agg["win_rate"].append(float(row.get("win_rate") or 0))
            agg["avg_roi"].append(float(row.get("avg_roi") or 0))
            agg["trades"].append(int(row.get("trades") or 0))
            agg["max_dd"].append(float(row.get("max_drawdown") or 0))
            agg["avg_hold"].append(float(row.get("avg_hold") or 0))
            agg["tiers"].add(str(row.get("tier") or ""))
    out: list[dict[str, Any]] = []
    for slug, agg in by_genome.items():
        meta = name_by_slug.get(slug, {})
        metrics = {
            "pnl": round(mean(agg["pnl"]), 2),
            "win_rate": round(mean(agg["win_rate"]), 1),
            "avg_roi": round(mean(agg["avg_roi"]), 2),
            "trades_mean": round(mean(agg["trades"]), 0),
            "trades_total": int(sum(agg["trades"])),
            "max_dd": round(mean(agg["max_dd"]), 1),
            "avg_hold": round(mean(agg["avg_hold"]), 0),
        }
        grade = "mixed" if len(agg["tiers"]) > 1 else next(iter(agg["tiers"]), "ghost")
        out.append({
            "slug": slug,
            "name": meta.get("name", slug),
            "kind": agg["kind"],
            "family": meta.get("family_slug", ""),
            "combos": len(agg["pnl"]),
            "grade": grade,
            "metrics": metrics,
            "traits": derive_genome_traits(agg["kind"], metrics),
        })
    order = {"entry": 0, "exit": 1, "management": 2}
    out.sort(key=lambda row: (order.get(row["kind"], 9), -row["metrics"]["pnl"]))
    return out


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    issues = validate(input_packet, context)
    if issues:
        return {"ok": False, "output_packet": {}, "receipts": [], "issues": issues, "meta": {}}
    payload = input_packet["payload"]
    value = genome_wind_tunnel(list(payload["evidence"]), list(payload["genomes"]))
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
        "receipt_id": "genome-wind-tunnel-built",
        "brick_id": CONCEPT["id"],
        "kind": "view_build",
        "label": "Built genome wind-tunnel read model.",
        "refs": [],
        "data": {"count": len(output_packet["payload"])},
    }]
