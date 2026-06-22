"""Pure `.loom` relationship model.

This module defines the current `.loom` meaning:

- a universe string,
- a set of existing `.oradio` nodes,
- and soulmate relationships between those nodes.

It is intentionally UI-free and dependency-free so both authoring surfaces and
players can share one source of truth without pulling in Tk, PIL, OpenCV, or
legacy station-manifest assumptions.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


def slugify_node(text: str) -> str:
    words = "".join(c if c.isalnum() or c.isspace() else " " for c in (text or "")).split()
    return "-".join(words[:6]).lower() or "untitled-node"


@dataclass(frozen=True)
class LoomNode:
    id: str
    label: str
    oradio: str
    soulmate: str = ""
    soulmates: Tuple[str, ...] = ()

    @classmethod
    def from_any(cls, raw: Any, index: int = 1) -> "LoomNode | None":
        if not isinstance(raw, dict):
            return None
        label = str(raw.get("label", "")).strip()
        oradio = str(raw.get("oradio", "")).strip()
        soulmate = str(raw.get("soulmate", "")).strip()
        raw_soulmates = raw.get("soulmates") or []
        soulmates: List[str] = []
        if isinstance(raw_soulmates, list):
            for item in raw_soulmates:
                value = str(item or "").strip()
                if value and value not in soulmates:
                    soulmates.append(value)
        if soulmate and soulmate not in soulmates:
            soulmates.append(soulmate)
        primary_soulmate = soulmate or (soulmates[0] if soulmates else "")
        if not label and not oradio:
            return None
        node_id = str(raw.get("id", "")).strip() or slugify_node(label or oradio or f"node-{index}")
        return cls(
            id=node_id,
            label=label or slugify_node(oradio or f"node-{index}"),
            oradio=oradio,
            soulmate=primary_soulmate,
            soulmates=tuple(soulmates),
        )

    def as_dict(self) -> Dict[str, str]:
        soulmate = self.soulmate or (self.soulmates[0] if self.soulmates else "")
        return {
            "id": self.id,
            "label": self.label,
            "oradio": self.oradio,
            "soulmate": soulmate,
            "soulmates": list(self.soulmates),
        }


@dataclass(frozen=True)
class LoomGraph:
    universe: str
    oradios: Tuple[LoomNode, ...]

    @classmethod
    def from_any(cls, universe: str, nodes: List[Dict[str, str]]) -> "LoomGraph":
        clean_nodes: List[LoomNode] = []
        for index, raw in enumerate(nodes, start=1):
            node = LoomNode.from_any(raw, index=index)
            if node is not None:
                clean_nodes.append(node)
        return cls(universe=universe.strip(), oradios=tuple(clean_nodes))

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "LoomGraph":
        raw = raw or {}
        universe = str(raw.get("universe", "")).strip()
        raw_nodes = raw.get("oradios") or raw.get("nodes") or []
        nodes = raw_nodes if isinstance(raw_nodes, list) else []
        return cls.from_any(universe, nodes)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "universe": self.universe,
            "oradios": [node.as_dict() for node in self.oradios],
        }


def declaration_text(universe: str, nodes: List[Dict[str, str]]) -> str:
    doc = LoomGraph.from_any(universe, nodes).as_dict()
    try:
        import yaml  # type: ignore

        return yaml.safe_dump(doc, sort_keys=False, allow_unicode=True)
    except ImportError:
        import json

        return json.dumps(doc, indent=2, ensure_ascii=False)


def declaration_size(universe: str, nodes: List[Dict[str, str]]) -> int:
    return len(declaration_text(universe, nodes).encode("utf-8"))


def load_declaration_text(text: str) -> Tuple[str, List[Dict[str, str]]]:
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
    except ImportError:
        import json

        data = json.loads(text)
    graph = LoomGraph.from_dict(data or {})
    return graph.universe, [node.as_dict() for node in graph.oradios]


def graph_nodes(universe: str, nodes: List[Dict[str, str]], width: int = 520, height: int = 280) -> List[Dict[str, Any]]:
    graph = LoomGraph.from_any(universe, nodes)
    if not graph.oradios:
        return []
    digest = hashlib.sha256(graph.universe.encode("utf-8")).hexdigest() if graph.universe else "0"
    angle_offset = (int(digest[:8], 16) % 360) * math.pi / 180.0
    cx, cy = width / 2.0, height / 2.0
    radius = min(width, height) * 0.34
    laid_out: List[Dict[str, Any]] = []
    count = max(1, len(graph.oradios))
    for index, node in enumerate(graph.oradios):
        angle = angle_offset + ((2 * math.pi * index) / count)
        laid_out.append(
            {
                **node.as_dict(),
                "x": cx + (radius * math.cos(angle)),
                "y": cy + (radius * math.sin(angle)),
            }
        )
    return laid_out
