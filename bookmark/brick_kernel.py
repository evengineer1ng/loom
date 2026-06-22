"""The brick kernel — discover, validate, run, and wire ``loom.concept.v1`` bricks.

A *brick* is one small ``.py`` module that exposes a ``CONCEPT`` dict plus the surface
functions ``inspect`` / ``validate`` / ``run`` (and usually ``receipts``). Bricks declare
typed packet I/O (``inputs`` / ``outputs``) and capabilities (``requires`` / ``provides``),
which is what lets Bookmark wire them into a graph: one brick's output packet-type feeds the
next brick's input.

This module is intentionally tiny and dependency-free. It loads brick files in isolation and
tolerates per-brick import failures (a brick that imports a missing library is catalogued as
*unavailable*, never fatal) — so mining a half-broken old repo still yields a usable catalog.
"""

from __future__ import annotations

import importlib.util
import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional

API_VERSION = "loom.concept.v1"

# Keys every well-formed CONCEPT must carry.
REQUIRED_CONCEPT_KEYS = (
    "api_version", "id", "kind", "version", "deterministic",
    "inputs", "outputs", "requires", "provides", "side_effects",
    "ui_slots", "tags", "description",
)

# Surface functions every brick module must expose. Only ``inspect`` + ``run`` are
# universal in the wild; ``validate`` and ``receipts`` are optional (many bricks omit them).
CONTRACT_FUNCS = ("inspect", "run")


class WireError(Exception):
    """Raised when two bricks cannot be connected (packet-type mismatch, missing brick…)."""


@dataclass
class Brick:
    """A loaded brick — its CONCEPT plus a handle to the module that runs it.

    When a brick file fails to import or violates the contract, it is still catalogued
    with ``available=False`` and an ``error`` string, so the registry never hides what it
    found. ``id`` falls back to the file's namespaced path when CONCEPT is unreadable.
    """

    id: str
    path: Path
    kind: str = "unknown"
    version: str = ""
    deterministic: bool = False
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    requires: tuple[str, ...] = ()
    provides: tuple[str, ...] = ()
    side_effects: tuple[str, ...] = ()
    ui_slots: tuple[Any, ...] = ()
    tags: tuple[str, ...] = ()
    description: str = ""
    emoji: str = ""          # the brick's glyph; pinned via CONCEPT["emoji"] or auto-assigned
    lang: str = "python"     # python | html | json | ... — the brick's medium
    asset: Optional[Path] = None   # for non-python bricks, the file the brick IS (html/json/…)
    concept: Dict[str, Any] = field(default_factory=dict)
    module: Any = None
    available: bool = False
    error: Optional[str] = None

    @property
    def family(self) -> str:
        """The ``family.subfamily`` namespace (the id without its leaf), e.g. ``math.stats``."""
        return self.id.rsplit(".", 1)[0] if "." in self.id else ""

    def validate(self, input_packet: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
        if not self.available:
            return [{"code": "unavailable", "message": self.error or "brick not loaded"}]
        fn = getattr(self.module, "validate", None)  # optional in the contract
        return list(fn(input_packet, context)) if callable(fn) else []

    def run(self, input_packet: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run the brick. Always returns the standard result envelope, even on failure.

        Python bricks exec their module's ``run``. Non-python ("surface"/"data") bricks don't
        execute python — running one yields an envelope naming the surface to open (html/json/…);
        the kernel acts on it via :func:`serve_brick`. The envelope shape is identical so the
        wiring substrate doesn't care what medium a brick is.
        """
        if not self.available:
            return _fail(self.error or "brick not loaded", code="unavailable")
        if self.lang != "python":
            return {
                "ok": True,
                "output_packet": make_packet(
                    f"surface.{self.lang}.v1",
                    {"lang": self.lang, "asset": str(self.asset or ""), "brick_id": self.id},
                ),
                "receipts": [], "issues": [], "meta": {"lang": self.lang},
            }
        try:
            return self.module.run(input_packet, context)
        except Exception as exc:  # a brick raising is a run-time issue, not a kernel crash
            return _fail(f"{type(exc).__name__}: {exc}", code="run_raised")


def _fail(message: str, code: str = "error") -> Dict[str, Any]:
    return {"ok": False, "output_packet": {}, "receipts": [],
            "issues": [{"code": code, "message": message}], "meta": {}}


def make_packet(packet_type: str, payload: Dict[str, Any], *,
                trace_id: str = "", refs: Optional[List[Any]] = None,
                meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Build a well-formed input packet for a brick."""
    return {
        "packet_type": packet_type,
        "packet_version": packet_type,
        "trace_id": trace_id or uuid.uuid4().hex,
        "parent_trace_id": "",
        "payload": dict(payload),
        "refs": list(refs or []),
        "meta": dict(meta or {}),
    }


def _concept_issues(concept: Dict[str, Any]) -> List[str]:
    """Return human-readable reasons a CONCEPT is not well-formed (empty list = ok)."""
    issues: List[str] = []
    missing = [k for k in REQUIRED_CONCEPT_KEYS if k not in concept]
    if missing:
        issues.append(f"CONCEPT missing keys: {', '.join(missing)}")
    av = concept.get("api_version")
    if av and av != API_VERSION:
        issues.append(f"unexpected api_version {av!r} (want {API_VERSION!r})")
    return issues


def _load_brick(path: Path, root: Path) -> Brick:
    """Import one brick file in isolation; never raises — failures land in Brick.error."""
    rel = path.relative_to(root).with_suffix("")
    # id fallback from path: math.stats/mean_value -> math.stats.mean_value
    fallback_id = ".".join(rel.parts)
    mod_name = f"_brick_{fallback_id.replace('.', '_')}"
    try:
        spec = importlib.util.spec_from_file_location(mod_name, path)
        if spec is None or spec.loader is None:
            return Brick(id=fallback_id, path=path, error="could not create import spec")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as exc:
        return Brick(id=fallback_id, path=path, error=f"import failed — {type(exc).__name__}: {exc}")

    concept = getattr(module, "CONCEPT", None)
    if not isinstance(concept, dict):
        return Brick(id=fallback_id, path=path, module=module, error="no CONCEPT dict")

    problems = _concept_issues(concept)
    missing_funcs = [f for f in CONTRACT_FUNCS if not callable(getattr(module, f, None))]
    if missing_funcs:
        problems.append(f"missing functions: {', '.join(missing_funcs)}")

    brick = Brick(
        id=str(concept.get("id", fallback_id)),
        path=path,
        kind=str(concept.get("kind", "unknown")),
        version=str(concept.get("version", "")),
        deterministic=bool(concept.get("deterministic", False)),
        inputs=tuple(concept.get("inputs", ())),
        outputs=tuple(concept.get("outputs", ())),
        requires=tuple(concept.get("requires", ())),
        provides=tuple(concept.get("provides", ())),
        side_effects=tuple(concept.get("side_effects", ())),
        ui_slots=tuple(concept.get("ui_slots", ())),
        tags=tuple(concept.get("tags", ())),
        description=str(concept.get("description", "")),
        emoji=str(concept.get("emoji", "")),
        lang=str(concept.get("lang", "python")),
        asset=path,
        concept=concept,
        module=module,
        available=not problems,
        error="; ".join(problems) or None,
    )
    return brick


def _load_sidecar_brick(concept_path: Path, root: Path) -> Brick:
    """Load a non-python brick from a ``name.concept.json`` sidecar.

    The CONCEPT is the SAME shape as a python brick's in-file dict (id, kind, inputs/outputs,
    emoji, …) plus ``lang`` (html|json|…) and ``asset`` (the file the brick is, resolved relative
    to the sidecar, or absolute). No inspect/run functions are required — a surface/data brick is
    "available" when its asset exists and its CONCEPT is well-formed.
    """
    rel = concept_path.relative_to(root).with_suffix("")  # drops .json (leaves name.concept)
    fallback_id = ".".join(rel.with_suffix("").parts)     # drops .concept too
    try:
        concept = json.loads(concept_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return Brick(id=fallback_id, path=concept_path, lang="unknown",
                     error=f"bad concept.json — {type(exc).__name__}: {exc}")
    if not isinstance(concept, dict):
        return Brick(id=fallback_id, path=concept_path, error="concept.json is not an object")

    lang = str(concept.get("lang", "")).strip() or "html"
    asset_field = str(concept.get("asset", "")).strip()
    asset = Path(asset_field)
    if not asset.is_absolute():
        asset = (concept_path.parent / asset_field).resolve() if asset_field else None

    problems = _concept_issues(concept)
    if not asset_field:
        problems.append("sidecar brick missing 'asset'")
    elif asset is None or not asset.exists():
        problems.append(f"asset not found: {asset_field}")

    return Brick(
        id=str(concept.get("id", fallback_id)),
        path=concept_path,
        kind=str(concept.get("kind", "surface")),
        version=str(concept.get("version", "")),
        deterministic=bool(concept.get("deterministic", False)),
        inputs=tuple(concept.get("inputs", ())),
        outputs=tuple(concept.get("outputs", ())),
        requires=tuple(concept.get("requires", ())),
        provides=tuple(concept.get("provides", ())),
        side_effects=tuple(concept.get("side_effects", ())),
        ui_slots=tuple(concept.get("ui_slots", ())),
        tags=tuple(concept.get("tags", ())),
        description=str(concept.get("description", "")),
        emoji=str(concept.get("emoji", "")),
        lang=lang,
        asset=asset,
        concept=concept,
        module=None,
        available=not problems,
        error="; ".join(problems) or None,
    )


def discover(root: str | Path) -> Dict[str, Brick]:
    """Walk ``root`` for brick ``.py`` files and load each. Returns {id: Brick}.

    Skips dunder files and ``__pycache__``. Later ids win on collision (deterministic by
    sorted path order), so a curated copy can shadow a mined original.
    """
    root = Path(root)
    out: Dict[str, Brick] = {}
    if not root.exists():
        return out
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" in path.parts or path.name.startswith("__"):
            continue
        brick = _load_brick(path, root)
        out[brick.id] = brick
    # Non-python ("surface"/"data") bricks: a name.concept.json sidecar beside the asset.
    for path in sorted(root.rglob("*.concept.json")):
        if "__pycache__" in path.parts:
            continue
        brick = _load_sidecar_brick(path, root)
        out[brick.id] = brick
    return out


class BrickRegistry:
    """A loaded catalog of bricks, queryable by id, capability, packet-type, or tag."""

    def __init__(self, bricks: Optional[Dict[str, Brick]] = None):
        self.bricks: Dict[str, Brick] = dict(bricks or {})
        self.emoji_of: Dict[str, str] = {}     # brick_id -> emoji
        self.by_emoji: Dict[str, str] = {}     # emoji -> brick_id
        self.assign_emojis()

    @classmethod
    def from_path(cls, root: str | Path) -> "BrickRegistry":
        return cls(discover(root))

    @classmethod
    def from_roots(cls, roots: Iterable[str | Path]) -> "BrickRegistry":
        """Mine several brick troves into one registry (later roots win on id collision)."""
        reg = cls()
        for root in roots:
            reg.add_path(root)
        return reg

    def add_path(self, root: str | Path) -> "BrickRegistry":
        """Merge another bricks root into this registry (for mining several repos)."""
        self.bricks.update(discover(root))
        self.assign_emojis()
        return self

    def assign_emojis(self) -> None:
        """Give every brick a UNIQUE emoji so a string of emojis lays a string of bricks.

        Pinned ``CONCEPT["emoji"]`` wins; the rest are filled greedily from a large pool in
        sorted-id order, so assignment is stable across runs and collision-free within a registry.
        """
        self.emoji_of, self.by_emoji = {}, {}
        pool = _emoji_pool()
        taken: set[str] = set()
        # pass 1: honor pinned emojis
        for bid in sorted(self.bricks):
            pin = (self.bricks[bid].emoji or "").strip()
            if pin and pin not in taken:
                self.emoji_of[bid] = pin
                taken.add(pin)
        # pass 2: greedily assign from the pool to the rest
        it = iter(pool)
        for bid in sorted(self.bricks):
            if bid in self.emoji_of:
                continue
            for glyph in it:
                if glyph not in taken:
                    self.emoji_of[bid] = glyph
                    taken.add(glyph)
                    break
        for bid, glyph in self.emoji_of.items():
            self.by_emoji[glyph] = bid
            self.bricks[bid].emoji = glyph

    def brick_by_emoji(self, glyph: str) -> Optional[Brick]:
        bid = self.by_emoji.get(glyph)
        return self.bricks.get(bid) if bid else None

    def bricks_for_emojis(self, text: str) -> List[Brick]:
        """Parse a string of emojis (any separators ignored) into the bricks they name."""
        out: List[Brick] = []
        for ch in (text or ""):
            brick = self.brick_by_emoji(ch)
            if brick is not None:
                out.append(brick)
        return out

    def __len__(self) -> int:
        return len(self.bricks)

    def __iter__(self) -> Iterable[Brick]:
        return iter(self.bricks.values())

    def get(self, brick_id: str) -> Optional[Brick]:
        return self.bricks.get(brick_id)

    def available(self) -> List[Brick]:
        return [b for b in self.bricks.values() if b.available]

    def broken(self) -> List[Brick]:
        return [b for b in self.bricks.values() if not b.available]

    def providing(self, capability: str) -> List[Brick]:
        return [b for b in self.available() if capability in b.provides]

    def emitting(self, packet_type: str) -> List[Brick]:
        """Bricks whose output includes ``packet_type`` — candidates to feed a consumer."""
        return [b for b in self.available() if packet_type in b.outputs]

    def accepting(self, packet_type: str) -> List[Brick]:
        """Bricks whose input includes ``packet_type`` — candidates downstream of a producer."""
        return [b for b in self.available() if packet_type in b.inputs]

    def with_tag(self, tag: str) -> List[Brick]:
        return [b for b in self.available() if tag in b.tags]


@dataclass
class StepResult:
    brick_id: str
    ok: bool
    output_packet: Dict[str, Any]
    receipts: List[Dict[str, Any]]
    issues: List[Dict[str, Any]]


@dataclass
class PipelineResult:
    ok: bool
    output_packet: Dict[str, Any]
    steps: List[StepResult]
    receipts: List[Dict[str, Any]]  # flattened causal ledger across the whole run

    @property
    def failed_step(self) -> Optional[StepResult]:
        return next((s for s in self.steps if not s.ok), None)


class Pipeline:
    """An ordered wiring of bricks. Each brick's output packet feeds the next brick's input.

    Wiring is *type-checked at build time*: the producer's output packet-type must be in the
    consumer's declared ``inputs``. This is the same matching the authoring canvas will do
    visually; the mint serializes the validated graph into the oradio declaration.
    """

    def __init__(self, registry: BrickRegistry, brick_ids: List[str]):
        self.registry = registry
        self.bricks: List[Brick] = []
        for bid in brick_ids:
            brick = registry.get(bid)
            if brick is None:
                raise WireError(f"unknown brick: {bid!r}")
            if not brick.available:
                raise WireError(f"brick {bid!r} unavailable: {brick.error}")
            self.bricks.append(brick)
        self._check_types()

    def _check_types(self) -> None:
        for producer, consumer in zip(self.bricks, self.bricks[1:]):
            if not producer.outputs:
                raise WireError(f"{producer.id} declares no outputs to feed {consumer.id}")
            shared = set(producer.outputs) & set(consumer.inputs)
            if not shared:
                raise WireError(
                    f"cannot wire {producer.id} -> {consumer.id}: "
                    f"outputs {list(producer.outputs)} have no match in "
                    f"inputs {list(consumer.inputs)}"
                )

    def run(self, input_packet: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> PipelineResult:
        steps: List[StepResult] = []
        ledger: List[Dict[str, Any]] = []
        packet = input_packet
        ok_all = True
        for brick in self.bricks:
            result = brick.run(packet, context)
            step = StepResult(
                brick_id=brick.id,
                ok=bool(result.get("ok")),
                output_packet=result.get("output_packet", {}) or {},
                receipts=result.get("receipts", []) or [],
                issues=result.get("issues", []) or [],
            )
            steps.append(step)
            ledger.extend(step.receipts)
            if not step.ok:
                ok_all = False
                break
            packet = step.output_packet
        return PipelineResult(ok=ok_all, output_packet=packet if ok_all else {},
                              steps=steps, receipts=ledger)


def serve_brick(brick: "Brick", *, open_browser: bool = True, host: str = "127.0.0.1",
                port: int = 0) -> Dict[str, Any]:
    """Serve a surface (html) brick locally and (optionally) open the browser.

    Returns {url, host, port, httpd, asset}. The caller owns `httpd` (call .shutdown() to stop).
    Non-html bricks return {error}. This is how an oradio's html `open` surface is realized.
    """
    if brick.lang != "html" or not brick.asset or not Path(brick.asset).exists():
        return {"error": f"not a servable html brick: {brick.id}"}
    import functools
    import http.server
    import socketserver
    import threading
    import webbrowser

    asset = Path(brick.asset)
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(asset.parent))
    httpd = socketserver.TCPServer((host, port), handler)
    actual_port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    url = f"http://{host}:{actual_port}/{asset.name}"
    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    return {"url": url, "host": host, "port": actual_port, "httpd": httpd, "asset": str(asset)}


# Emoji pool for brick glyphs — generated from pictographic Unicode ranges via chr() so the
# source stays ASCII (no literal-emoji encoding hazard on cp1252). ~1000+ glyphs; plenty unique
# for the current 243 bricks. Order is stable, so emoji assignment is reproducible.
_EMOJI_RANGES = [
    (0x1F300, 0x1F320), (0x1F330, 0x1F37F), (0x1F380, 0x1F3CF), (0x1F3E0, 0x1F3F0),
    (0x1F400, 0x1F4FD), (0x1F500, 0x1F53D), (0x1F550, 0x1F567), (0x1F5FB, 0x1F5FF),
    (0x1F600, 0x1F64F), (0x1F680, 0x1F6C5), (0x1F900, 0x1F9FF), (0x1FA70, 0x1FAA8),
    (0x1FAB0, 0x1FABD), (0x1FAC0, 0x1FAC5), (0x1FAD0, 0x1FADB),
]

_EMOJI_POOL_CACHE: List[str] = []


def _emoji_pool() -> List[str]:
    global _EMOJI_POOL_CACHE
    if not _EMOJI_POOL_CACHE:
        pool: List[str] = []
        for lo, hi in _EMOJI_RANGES:
            pool.extend(chr(cp) for cp in range(lo, hi + 1))
        _EMOJI_POOL_CACHE = pool
    return _EMOJI_POOL_CACHE


# Mined brick troves (see memory: brick-contract-loom-concept-v1). Now VAULTED IN-REPO + repo-
# relative, so the garden travels with a clone (no machine-specific paths) and is git-safe. Add a
# path here and every surface (Bookmark, palette, canvas) sees the new bricks. discover() skips a
# missing root, so dropping a trove is harmless.
_REPO = Path(__file__).resolve().parent.parent
ATL_BRICKS = _REPO / "atl_bricks" / "bricks"      # the 150 mined atl bricks (was external)
RADIO_BRICKS = _REPO / "radio_bricks" / "bricks"  # the 469 mined radio bricks (was external)
# Polyglot trove: non-python (html/json) bricks declared via name.concept.json sidecars.
HTML_BRICKS = _REPO / "html_bricks" / "bricks"
# oracle-radio's own (kernel-side) python bricks — e.g. the picture-frame carousel decorator.
LOCAL_BRICKS = _REPO / "bricks"
BRICK_ROOTS = [ATL_BRICKS, RADIO_BRICKS, HTML_BRICKS, LOCAL_BRICKS]


def _demo(root: str | Path = ATL_BRICKS) -> None:
    """Smoke test: catalog a bricks root, then run a deterministic brick end-to-end."""
    reg = BrickRegistry.from_path(root)
    ok, broken = reg.available(), reg.broken()
    print(f"discovered {len(reg)} bricks at {root}")
    print(f"  available: {len(ok)}   unavailable: {len(broken)}")
    fams: Dict[str, int] = {}
    for b in ok:
        fams[b.family] = fams.get(b.family, 0) + 1
    for fam in sorted(fams):
        print(f"    {fam:24} {fams[fam]}")
    if broken:
        print("  unavailable (mining gaps):")
        for b in broken:
            print(f"    {b.id:40} {b.error}")

    mean = reg.get("math.stats.mean_value")
    if mean and mean.available:
        pkt = make_packet("math.series_request.v1", {"values": [2, 4, 6, 8]})
        result = mean.run(pkt)
        print("\nran math.stats.mean_value on [2,4,6,8]:")
        print(f"  ok={result['ok']} payload={result['output_packet'].get('payload')}")
        print(f"  receipts={[r['receipt_id'] for r in result['receipts']]}")


if __name__ == "__main__":
    import sys
    _demo(sys.argv[1] if len(sys.argv) > 1 else ATL_BRICKS)
