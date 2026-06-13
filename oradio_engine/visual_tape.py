"""Append-only visual causes for the Loom player."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from oradio_engine.contract import NormalizedCandidate

from oradio_engine.visual_index import VisualIndex

Address = Tuple[Any, ...]

DEFAULT_VISUAL_FAMILIES = (
    "color_drift",
    "breath",
    "particles",
    "ripples",
    "bloom",
    "scanlines",
    "veil",
    "orbitals",
)


def _hash_unit(*parts: Any) -> float:
    raw = hashlib.sha256(":".join(str(part) for part in parts).encode("utf-8")).digest()
    return int.from_bytes(raw[:4], "big") / 0xFFFFFFFF


@dataclass(frozen=True)
class VisualTapeEvent:
    tick: int
    family: str
    source: str
    address: Address
    energy: float
    hue_hint: float
    lineage: Tuple[str, ...] = ()
    payload: Dict[str, Any] = field(default_factory=dict)
    seq: int = 0


@dataclass
class VisualTapeSnapshot:
    tick: int
    entries: int
    total_energy: float
    hue_shift: float
    family_energy: Dict[str, float]
    breath: float
    haze: float
    zoom: float
    bloom: float
    veil: float
    scanline_alpha: float
    grain: float
    glitch: float
    prism: float
    particles: List[Dict[str, float]]
    ripples: List[Dict[str, float]]
    orbitals: List[Dict[str, float]]
    lineage: List[Tuple[str, ...]]


class VisualTapeLog:
    """Append-only visual event log."""

    def __init__(self) -> None:
        self._events: List[VisualTapeEvent] = []
        self._next_seq = 1

    def append(self, event: VisualTapeEvent) -> VisualTapeEvent:
        stamped = VisualTapeEvent(
            tick=int(event.tick),
            family=event.family,
            source=event.source,
            address=tuple(event.address),
            energy=float(event.energy),
            hue_hint=float(event.hue_hint),
            lineage=tuple(event.lineage),
            payload=dict(event.payload),
            seq=self._next_seq,
        )
        self._next_seq += 1
        self._events.append(stamped)
        return stamped

    def extend(self, events: Iterable[VisualTapeEvent]) -> List[VisualTapeEvent]:
        return [self.append(event) for event in events]

    def clear(self) -> None:
        self._events.clear()
        self._next_seq = 1

    def through(self, tick: int) -> List[VisualTapeEvent]:
        return [event for event in self._events if event.tick <= tick]

    def recent(self, limit: int = 6) -> List[VisualTapeEvent]:
        return self._events[-limit:]

    def __len__(self) -> int:
        return len(self._events)


def descriptor_visual_families(descriptor: Dict[str, Any]) -> List[str]:
    visual = descriptor.get("visual") if isinstance(descriptor.get("visual"), dict) else {}
    tape = visual.get("tape") if isinstance(visual.get("tape"), dict) else {}
    families = tape.get("families")
    if isinstance(families, list):
        cleaned = [str(item).strip() for item in families if str(item).strip()]
        if cleaned:
            return cleaned
    return list(DEFAULT_VISUAL_FAMILIES)


def candidate_to_visual_events(
    candidate: NormalizedCandidate,
    tick: int,
    *,
    families: Sequence[str],
) -> List[VisualTapeEvent]:
    energy = max(0.05, float(candidate.priority))
    hue_hint = (_hash_unit(candidate.post_id, candidate.source, candidate.type) * 2.0) - 1.0
    base_lineage = (
        f"candidate:{candidate.post_id}",
        f"source:{candidate.source}",
        f"type:{candidate.type}",
        f"tick:{tick}",
    )
    events: List[VisualTapeEvent] = []
    for family in families:
        events.append(
            VisualTapeEvent(
                tick=tick,
                family=family,
                source=candidate.source,
                address=("t", tick, "candidate", candidate.post_id, "family", family),
                energy=energy,
                hue_hint=hue_hint,
                lineage=base_lineage,
                payload={
                    "title": candidate.title,
                    "priority": candidate.priority,
                    "body": candidate.body,
                },
            )
        )
    return events


def build_visual_snapshot(
    log: VisualTapeLog,
    index: VisualIndex,
    tick: int,
    *,
    width: int,
    height: int,
) -> VisualTapeSnapshot:
    events = log.through(tick)
    total_energy = sum(event.energy for event in events)
    family_energy: Dict[str, float] = {}
    for event in events:
        family_energy[event.family] = family_energy.get(event.family, 0.0) + event.energy
    energy_scale = min(1.0, total_energy / 18.0) if events else 0.0
    hue_shift = 0.0
    if total_energy:
        hue_shift = max(
            -0.9,
            min(0.9, sum(event.hue_hint * event.energy for event in events) / total_energy),
        )
    breath_energy = family_energy.get("breath", 0.0)
    veil_energy = family_energy.get("veil", 0.0)
    bloom_energy = family_energy.get("bloom", 0.0)
    particle_energy = family_energy.get("particles", 0.0) + family_energy.get("embers", 0.0)
    ripple_energy = family_energy.get("ripples", 0.0)
    orbital_energy = family_energy.get("orbitals", 0.0)
    glitch_energy = family_energy.get("glitch", 0.0)
    prism_energy = family_energy.get("prisms", 0.0)
    grain_energy = family_energy.get("grain", 0.0)
    scanline_energy = family_energy.get("scanlines", 0.0)
    zoom_energy = breath_energy + (0.35 * family_energy.get("color_drift", 0.0)) + (0.4 * bloom_energy)

    breath = 0.16 + min(0.84, breath_energy / 12.0 + total_energy / 80.0)
    haze = min(0.42, veil_energy / 18.0 + total_energy / 120.0)
    zoom = 1.0 + min(0.11, zoom_energy / 70.0)
    bloom = min(0.7, bloom_energy / 14.0)
    veil = min(0.55, veil_energy / 14.0)
    scanline_alpha = min(0.3, scanline_energy / 24.0)
    grain = min(0.32, grain_energy / 18.0)
    glitch = min(0.35, glitch_energy / 16.0)
    prism = min(0.45, prism_energy / 18.0)

    particle_count = min(56, 8 + len(events) // 2 + int(particle_energy * 3))
    particles: List[Dict[str, float]] = []
    for idx in range(particle_count):
        point = index.particle(tick // 2, idx)
        warm = 0.35 + (0.65 * _hash_unit("warm", tick, idx))
        particles.append(
            {
                "x": point["u"] * width,
                "y": point["v"] * height,
                "r": 2.0 + (8.0 * point["w"] * max(0.25, breath)),
                "alpha": 0.10 + (0.34 * point["z"] * max(0.18, energy_scale)),
                "warm": warm,
            }
        )

    ripples: List[Dict[str, float]] = []
    for event in [item for item in events if item.family == "ripples"][-8:]:
        point = index.ripple(event.tick, event.seq)
        ripples.append(
            {
                "cx": point["u"] * width,
                "cy": point["v"] * height,
                "radius": 30.0 + (max(width, height) * 0.18 * point["w"]) + (event.energy * 26.0) + (ripple_energy * 4.0),
                "alpha": 0.12 + (0.22 * min(1.0, event.energy)),
            }
        )

    orbital_count = min(18, int(orbital_energy * 3.5))
    orbitals: List[Dict[str, float]] = []
    for idx in range(orbital_count):
        point = index.resolve(("t", tick // 2, "orbital", idx))
        orbitals.append(
            {
                "cx": width * (0.25 + (0.5 * point["u"])),
                "cy": height * (0.25 + (0.5 * point["v"])),
                "radius": 18.0 + (point["w"] * max(width, height) * 0.12),
                "thickness": 1.0 + (2.0 * point["z"]),
                "alpha": 0.08 + (0.18 * min(1.0, orbital_energy / 4.0)),
            }
        )

    lineage = [event.lineage for event in events[-4:]]
    return VisualTapeSnapshot(
        tick=tick,
        entries=len(events),
        total_energy=total_energy,
        hue_shift=hue_shift,
        family_energy=family_energy,
        breath=breath,
        haze=haze,
        zoom=zoom,
        bloom=bloom,
        veil=veil,
        scanline_alpha=scanline_alpha,
        grain=grain,
        glitch=glitch,
        prism=prism,
        particles=particles,
        ripples=ripples,
        orbitals=orbitals,
        lineage=lineage,
    )
