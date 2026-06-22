from __future__ import annotations

from collections import defaultdict
from typing import Any


CONCEPT = {
    "api_version": "loom.concept.v1",
    "id": "research.ml_registry.family_biology_context_builder",
    "kind": "renderer",
    "version": "0.1.0",
    "deterministic": True,
    "inputs": ["research.registry_request.v1"],
    "outputs": ["research.registry_response.v1"],
    "requires": [],
    "provides": ["research.family_biology_context"],
    "side_effects": [],
    "ui_slots": [],
    "tags": ["research", "ml", "family", "lineage", "traits"],
    "description": "Build family-level biology views by attaching traits, parents, and temporal read models to each organism.",
}


def build_family_biology_context(
    families: list[dict[str, Any]] | None,
    registry: list[dict[str, Any]] | None,
    traits: list[dict[str, Any]] | None,
    lineage_edges: list[dict[str, Any]] | None,
    temporal_views: dict[str, Any] | None = None,
) -> dict[str, Any]:
    traits_by_strategy: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for trait in list(traits or []):
        row = dict(trait)
        traits_by_strategy[str(row.get("strategy_slug") or "")].append(row)
    parents_by_child: dict[str, list[str]] = defaultdict(list)
    for edge in list(lineage_edges or []):
        row = dict(edge)
        parents_by_child[str(row.get("child_slug") or "")].append(str(row.get("parent_slug") or ""))
    registry_rows = [dict(row) for row in (registry or [])]
    family_rows = []
    for family in list(families or []):
        fam = dict(family)
        members = [dict(item) for item in registry_rows if str(item.get("family_slug") or "") == str(fam.get("slug") or "")]
        for member in members:
            slug = str(member.get("slug") or "")
            member["traits"] = traits_by_strategy.get(slug, [])
            member["parents"] = [parent for parent in parents_by_child.get(slug, []) if parent]
            member["temporal"] = dict((temporal_views or {}).get(slug) or {})
        family_rows.append({**fam, "members": members})
    return {
        "families": family_rows,
        "family_count": len(family_rows),
        "strategy_count": len(registry_rows),
        "trait_count": len(list(traits or [])),
    }


def inspect() -> dict[str, Any]:
    return CONCEPT


def run(input_packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(input_packet.get("payload") or {})
    value = build_family_biology_context(
        families=[dict(item) for item in (payload.get("families") or []) if isinstance(item, dict)],
        registry=[dict(item) for item in (payload.get("registry") or []) if isinstance(item, dict)],
        traits=[dict(item) for item in (payload.get("traits") or []) if isinstance(item, dict)],
        lineage_edges=[dict(item) for item in (payload.get("lineage_edges") or []) if isinstance(item, dict)],
        temporal_views=dict(payload.get("temporal_views") or {}),
    )
    output_packet = {
        "packet_type": "research.registry_response.v1",
        "packet_version": "research.registry_response.v1",
        "trace_id": input_packet.get("trace_id", ""),
        "parent_trace_id": input_packet.get("trace_id", ""),
        "payload": value,
        "refs": [],
        "meta": {"provider": CONCEPT["id"]},
    }
    return {"ok": True, "output_packet": output_packet, "receipts": receipts(output_packet), "issues": [], "meta": {}}


def receipts(output_packet: dict[str, Any]) -> list[dict[str, Any]]:
    payload = output_packet.get("payload") or {}
    return [{
        "receipt_id": "family-biology-context-built",
        "brick_id": CONCEPT["id"],
        "kind": "view_build",
        "label": "Built family biology context.",
        "refs": [],
        "data": {
            "families": payload.get("family_count", 0),
            "strategies": payload.get("strategy_count", 0),
            "traits": payload.get("trait_count", 0),
        },
    }]
