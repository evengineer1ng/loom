"""The draft graph — wire-by-placement resolution for laid bricks.

You don't draw wires between bricks; you LAY them, and a packet-type match between two bricks
is the mortar. This module is the front-end-agnostic core of that idea: a :class:`DraftGraph`
holds the placed bricks, and :meth:`DraftGraph.resolve` infers the connections from types alone.

It answers the questions every stack visual (pyramid / wall / snap-column) needs:
- **bonds**: which brick's output feeds which brick's input (the mortar lines).
- **holes**: inputs/requirements nothing on the canvas satisfies — the Club's resolution surface.
- **ambiguities**: an input satisfiable by more than one placed brick (needs disambiguation).
- **strata**: the topological layers (a brick sits above the bricks it depends on); this is both
  the pyramid's rows and the kernel's run order.
- **cycle**: bricks that can't be layered because they feed each other.

Nothing here renders; a placement is just (brick, optional position). The visual model is a
skin over this resolution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .brick_kernel import Brick, BrickRegistry


@dataclass
class PlacedBrick:
    """One brick laid on the canvas. The same brick id may be placed multiple times, so each
    placement gets a unique ``instance_id``."""

    instance_id: str
    brick: Brick
    pos: Optional[Tuple[float, float]] = None  # canvas coords; unused by resolution
    config: Dict[str, Any] = field(default_factory=dict)  # tunable params (CONCEPT["params"])
    payload: Dict[str, Any] = field(default_factory=dict)  # editable packet payload for this placement


@dataclass
class Bond:
    """Inferred mortar: ``producer``'s output packet-type matches ``consumer``'s input."""

    producer: str   # instance_id
    consumer: str   # instance_id
    packet_type: str


@dataclass
class Resolution:
    """The full picture of a laid set of bricks, derived purely from types + capabilities."""

    bonds: List[Bond] = field(default_factory=list)
    holes: List[Tuple[str, str]] = field(default_factory=list)            # (instance_id, input packet-type)
    capability_holes: List[Tuple[str, str]] = field(default_factory=list)  # (instance_id, required capability)
    ambiguities: List[Tuple[str, str, List[str]]] = field(default_factory=list)  # (instance, type, producer instances)
    strata: List[List[str]] = field(default_factory=list)                 # topological layers of instance_ids
    cycle: List[str] = field(default_factory=list)                        # instances that couldn't be layered

    @property
    def ok(self) -> bool:
        """A draft is whole when nothing is unmet, nothing is tangled, nothing is ambiguous."""
        return not (self.holes or self.capability_holes or self.ambiguities or self.cycle)

    def summary(self) -> str:
        bits = [f"{len(self.bonds)} bond{'s' * (len(self.bonds) != 1)}"]
        if self.holes:
            bits.append(f"{len(self.holes)} hole{'s' * (len(self.holes) != 1)}")
        if self.capability_holes:
            bits.append(f"{len(self.capability_holes)} cap-hole")
        if self.ambiguities:
            bits.append(f"{len(self.ambiguities)} ambiguous")
        if self.cycle:
            bits.append(f"cycle×{len(self.cycle)}")
        if self.strata:
            bits.append(f"{len(self.strata)} strata")
        return " · ".join(bits)


class DraftGraph:
    """An ordered set of placed bricks whose connections are derived, never hand-stored."""

    def __init__(self, registry: Optional[BrickRegistry] = None):
        self.registry = registry
        self.placed: List[PlacedBrick] = []
        self._counters: Dict[str, int] = {}

    def place(self, brick: Brick, pos: Optional[Tuple[float, float]] = None) -> PlacedBrick:
        n = self._counters.get(brick.id, 0)
        self._counters[brick.id] = n + 1
        inst = PlacedBrick(instance_id=f"{brick.id}#{n}", brick=brick, pos=pos)
        self.placed.append(inst)
        return inst

    def remove(self, instance_id: str) -> bool:
        before = len(self.placed)
        self.placed = [p for p in self.placed if p.instance_id != instance_id]
        return len(self.placed) != before

    def move(self, instance_id: str, delta: int) -> bool:
        """Nudge a placement up/down in the list. The column is data-flow-ordered, but WITHIN a
        stratum (e.g. unbonded bricks) the order follows placement, so this re-sequences them."""
        idx = next((i for i, p in enumerate(self.placed) if p.instance_id == instance_id), None)
        if idx is None:
            return False
        j = max(0, min(len(self.placed) - 1, idx + delta))
        if j == idx:
            return False
        self.placed.insert(j, self.placed.pop(idx))
        return True

    def clear(self) -> None:
        self.placed = []
        self._counters = {}

    def _order_index(self) -> Dict[str, int]:
        return {p.instance_id: i for i, p in enumerate(self.placed)}

    def __len__(self) -> int:
        return len(self.placed)

    # ---- resolution -------------------------------------------------------
    def resolve(self) -> Resolution:
        """Derive bonds / holes / strata from the laid bricks and their declared types."""
        res = Resolution()

        # index: packet_type -> [producer instance_ids],  capability -> [provider instance_ids]
        emitters: Dict[str, List[str]] = {}
        providers: Dict[str, List[str]] = {}
        for p in self.placed:
            for t in p.brick.outputs:
                emitters.setdefault(t, []).append(p.instance_id)
            for cap in p.brick.provides:
                providers.setdefault(cap, []).append(p.instance_id)

        producers_of: Dict[str, set] = {p.instance_id: set() for p in self.placed}

        for consumer in self.placed:
            for t in consumer.brick.inputs:
                # a brick never feeds its own input
                srcs = [e for e in emitters.get(t, []) if e != consumer.instance_id]
                if not srcs:
                    res.holes.append((consumer.instance_id, t))
                    continue
                if len(srcs) > 1:
                    res.ambiguities.append((consumer.instance_id, t, list(srcs)))
                for src in srcs:
                    res.bonds.append(Bond(producer=src, consumer=consumer.instance_id, packet_type=t))
                    producers_of[consumer.instance_id].add(src)
            for cap in consumer.brick.requires:
                if not [pr for pr in providers.get(cap, []) if pr != consumer.instance_id]:
                    res.capability_holes.append((consumer.instance_id, cap))

        res.strata, res.cycle = self._layer(producers_of, self._order_index())
        return res

    @staticmethod
    def _layer(producers_of: Dict[str, set],
               order: Optional[Dict[str, int]] = None) -> Tuple[List[List[str]], List[str]]:
        """Kahn-style layering: a brick's stratum is one above its highest producer. Sources
        (no internal producers) form stratum 0; anything left over is a cycle. Within a stratum
        the order follows ``order`` (placement order) so manual move/rearrange is honored."""
        key = (lambda n: order.get(n, 0)) if order else (lambda n: n)
        remaining = set(producers_of)
        assigned: set = set()
        layers: List[List[str]] = []
        while remaining:
            ready = sorted((n for n in remaining if producers_of[n] <= assigned), key=key)
            if not ready:
                break  # remaining nodes feed each other — a cycle
            layers.append(ready)
            assigned |= set(ready)
            remaining -= set(ready)
        return layers, sorted(remaining, key=key)

    def run_order(self) -> List[str]:
        """Flattened topological order (instance_ids) for executing the draft via the kernel."""
        strata, _cycle = self._layer(
            {p.instance_id: {b.producer for b in self.resolve().bonds if b.consumer == p.instance_id}
             for p in self.placed},
            self._order_index(),
        )
        return [iid for layer in strata for iid in layer]


def _demo(root_path=None) -> None:
    """Lay a real producer→consumer pair from the brick trove and show the resolution."""
    from .brick_kernel import ATL_BRICKS
    reg = BrickRegistry.from_path(root_path or ATL_BRICKS)

    # find any real (producer, consumer) pair that shares a packet type
    avail = reg.available()
    pair = None
    for prod in avail:
        for con in avail:
            if con is prod:
                continue
            shared = set(prod.outputs) & set(con.inputs)
            if shared:
                pair = (prod, con, shared)
                break
        if pair:
            break

    g = DraftGraph(reg)
    if pair:
        prod, con, shared = pair
        g.place(prod)
        g.place(con)
        print(f"laid {prod.id}  ->  {con.id}   (mortar: {', '.join(shared)})")
    else:
        # fallback: just lay two bricks so holes/strata still demonstrate
        for b in avail[:2]:
            g.place(b)
        print("no type-sharing pair found; laid two unrelated bricks")

    res = g.resolve()
    print("resolution:", res.summary())
    for b in res.bonds:
        print(f"  bond  {b.producer}  --{b.packet_type}-->  {b.consumer}")
    for inst, t in res.holes[:6]:
        print(f"  hole  {inst}  needs  {t}   (Club resolves)")
    print("  strata:", res.strata)


if __name__ == "__main__":
    import sys
    _demo(sys.argv[1] if len(sys.argv) > 1 else None)
