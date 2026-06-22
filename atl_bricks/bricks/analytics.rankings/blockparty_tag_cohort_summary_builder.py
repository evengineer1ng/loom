from __future__ import annotations

from collections import defaultdict
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "analytics.rankings.blockparty_tag_cohort_summary_builder",
    "kind": "analyzer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["analytics.rankings_request.v1"],
    "outputs": ["analytics.rankings_response.v1"],
    "requires": [],
    "provides": ["analytics.blockparty_tag_cohort_summary"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["analytics", "rankings", "blockparty", "tags", "cohort"],
    "description": "Summarize Block Party tag cohorts by long-short prefix, encoded group state, and cohort-level averages.",
}


def _parse_tag(tag: str) -> dict[str, Any]:
    parts = str(tag or "").split("_")
    side = "long" if parts and parts[0] == "BPL" else "short" if parts and parts[0] == "BPS" else "unknown"
    metrics = {"group": None, "group_fast": None, "breadth_pct": None, "member_count": None}
    for part in parts[1:]:
        if part.startswith("g"):
            try:
                metrics["group"] = float(part[1:])
            except ValueError:
                pass
        elif part.startswith("gf"):
            raw = part[2:]
            if raw != "na":
                try:
                    metrics["group_fast"] = float(raw)
                except ValueError:
                    pass
        elif part.startswith("brd"):
            try:
                metrics["breadth_pct"] = float(part[3:])
            except ValueError:
                pass
        elif part.startswith("n"):
            try:
                metrics["member_count"] = int(part[1:])
            except ValueError:
                pass
    return {"side": side, **metrics}


def build_blockparty_tag_cohort_summary(rows: list[dict[str, Any]] | None) -> dict[str, Any]:
    cohorts: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows or []:
        tag = str((row or {}).get("enter_tag") or "")
        if not tag.startswith("BP"):
            continue
        cohorts[tag[:3]].append(_parse_tag(tag))

    summary = {}
    for cohort, items in cohorts.items():
        count = len(items)
        groups = [item["group"] for item in items if item["group"] is not None]
        breadths = [item["breadth_pct"] for item in items if item["breadth_pct"] is not None]
        sizes = [item["member_count"] for item in items if item["member_count"] is not None]
        summary[cohort] = {
            "count": count,
            "side": items[0]["side"] if items else "unknown",
            "avg_group": sum(groups) / len(groups) if groups else None,
            "avg_breadth_pct": sum(breadths) / len(breadths) if breadths else None,
            "avg_member_count": sum(sizes) / len(sizes) if sizes else None,
            "strong_group_tags": sum(1 for item in items if item["group"] is not None and abs(float(item["group"])) >= 2.0),
        }
    return summary


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    value = build_blockparty_tag_cohort_summary(input_packet.get("payload"))
    output_packet = {
        "packet_type": "analytics.rankings_response.v1",
        "packet_version": "analytics.rankings_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(value), "issues": [], "meta": {}}


def receipts(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "receipt_id": "blockparty-tag-cohort-summary",
        "brick_id": CONCEPT["id"],
        "kind": "analysis",
        "label": "Built Block Party tag cohort summary.",
        "refs": [],
        "data": {"cohorts": list(value.keys())},
    }]
