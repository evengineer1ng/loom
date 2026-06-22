"""Shared loom runtime helpers.

Small pure helpers used by Bookmark, Loom, and RibbonOS to agree on:

- which `.loom` files exist,
- which loom is currently active in the shell,
- how a newly minted `.oradio` is inserted into a loom,
- how relationship crossovers are rebuilt,
- how RibbonOS is asked to adopt a loom.
"""
from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

from loom.dotloom import _slug
from oradio_engine.loom_graph import LoomGraph, declaration_text, load_declaration_text, slugify_node

ACTIVE_LOOM_FILE = ".active_loom.json"
SWITCH_REQUEST_FILE = ".switch_request"


def project_candidates(root: Path, pattern: str) -> List[Path]:
    return list(root.glob(pattern))


def discover_oradio_candidates(root: Path) -> List[Path]:
    seen: Dict[str, Path] = {}
    for pattern in ("*.oradio", "exports/*.oradio", "spec/examples/*.oradio"):
        for path in project_candidates(root, pattern):
            seen[str(path.resolve())] = path
    return list(seen.values())


def discover_primary_loom(root: Path) -> Optional[Path]:
    candidates: List[Path] = []
    for pattern in ("*.loom", "exports/*.loom", "spec/examples/*.loom"):
        candidates.extend(project_candidates(root, pattern))
    for path in sorted(candidates):
        try:
            universe, nodes = load_declaration_text(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if universe or nodes:
            if nodes:
                return path
    return None


def discover_all_looms(root: Path) -> List[Tuple[Path, str, str]]:
    out: List[Tuple[Path, str, str]] = []
    seen_path: set[str] = set()
    seen_id: set[str] = set()
    candidates: List[Path] = []
    for pattern in ("*.loom", "exports/*.loom", "spec/examples/*.loom"):
        candidates.extend(project_candidates(root, pattern))
    for path in sorted(candidates):
        rp = str(path.resolve())
        if rp in seen_path:
            continue
        try:
            universe, nodes = load_declaration_text(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not (universe or nodes):
            continue
        loom_id = str(universe) if universe else path.stem
        if loom_id in seen_id:
            continue
        seen_path.add(rp)
        seen_id.add(loom_id)
        out.append((path, loom_id, path.stem))
    return out


def active_loom_state_path(root: Path) -> Path:
    return root / ACTIVE_LOOM_FILE


def read_active_loom_state(root: Path) -> Dict[str, Any]:
    path = active_loom_state_path(root)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_active_loom_state(root: Path, loom_path: Optional[Path]) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    if loom_path is not None:
        try:
            universe, _nodes = load_declaration_text(loom_path.read_text(encoding="utf-8"))
        except Exception:
            universe = ""
        payload = {
            "loom_path": str(loom_path.resolve()),
            "loom_id": str(universe or loom_path.stem),
        }
    active_loom_state_path(root).write_text(json.dumps(payload), encoding="utf-8")
    return payload


def resolve_active_loom(root: Path) -> Optional[Path]:
    state = read_active_loom_state(root)
    raw = str(state.get("loom_path", "")).strip()
    if raw:
        path = Path(raw)
        if path.exists():
            return path
    return discover_primary_loom(root)


def read_oradio_identity(oradio_path: Path) -> Dict[str, str]:
    if zipfile.is_zipfile(oradio_path):
        try:
            with zipfile.ZipFile(oradio_path) as zf:
                manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
            return {
                "id": str(manifest.get("id") or oradio_path.stem).strip() or oradio_path.stem,
                "title": str(manifest.get("title") or manifest.get("id") or oradio_path.stem).strip() or oradio_path.stem,
            }
        except Exception:
            pass
    return {"id": oradio_path.stem, "title": oradio_path.stem}


def request_ribbonos_load(root: Path, loom_path: Path) -> None:
    rq = root / SWITCH_REQUEST_FILE
    rq.write_text(json.dumps({"action": "load_loom", "loom_path": str(loom_path)}), encoding="utf-8")


def relationship_edges(nodes: List[Dict[str, Any]]) -> List[Tuple[str, str]]:
    node_ids = {str(node.get("id", "")).strip() for node in nodes if str(node.get("id", "")).strip()}
    seen = set()
    edges: List[Tuple[str, str]] = []
    for node in nodes:
        left = str(node.get("id", "")).strip()
        if not left:
            continue
        soulmates = node.get("soulmates") or []
        if not soulmates:
            soulmate = str(node.get("soulmate", "")).strip()
            soulmates = [soulmate] if soulmate else []
        for right in soulmates:
            right_id = str(right or "").strip()
            if not right_id or right_id not in node_ids:
                continue
            pair = tuple(sorted((left, right_id)))
            if pair in seen:
                continue
            seen.add(pair)
            edges.append(pair)
    return edges


def upsert_oradio_into_loom(
    loom_path: Path,
    oradio_path: Path,
    *,
    soulmate_ids: Optional[List[str]] = None,
    label: str = "",
) -> Dict[str, Any]:
    universe, nodes = load_declaration_text(loom_path.read_text(encoding="utf-8"))
    identity = read_oradio_identity(oradio_path)
    node_id = slugify_node(identity["id"])
    node_label = label.strip() or identity["title"]
    target_path = str(oradio_path.resolve()).replace("\\", "/")
    soulmate_ids = [str(item).strip() for item in (soulmate_ids or []) if str(item).strip() and str(item).strip() != node_id]
    valid_ids = {str(node.get("id", "")).strip() for node in nodes if str(node.get("id", "")).strip()}
    missing = [item for item in soulmate_ids if item not in valid_ids]
    if missing:
        raise ValueError(f"unknown soulmate ids for loom {loom_path.name}: {', '.join(missing)}")

    existing = next((node for node in nodes if str(node.get("id", "")).strip() == node_id), None)
    if existing is None:
        nodes.append({
            "id": node_id,
            "label": node_label,
            "oradio": target_path,
            "soulmate": soulmate_ids[0] if soulmate_ids else "",
            "soulmates": soulmate_ids,
        })
    else:
        existing["label"] = node_label
        existing["oradio"] = target_path
        merged = list(existing.get("soulmates") or ([existing.get("soulmate")] if existing.get("soulmate") else []))
        for soulmate_id in soulmate_ids:
            if soulmate_id not in merged:
                merged.append(soulmate_id)
        existing["soulmate"] = merged[0] if merged else ""
        existing["soulmates"] = merged

    loom_path.write_text(declaration_text(universe, nodes), encoding="utf-8")
    return {"universe": universe, "nodes": nodes, "node_id": node_id}


def edge_style_key(a: str, b: str) -> str:
    """Undirected key for a bonded edge's transition personality, e.g. ('iracing','kernel') ->
    'iracing__kernel' (sorted, so both directions share one style)."""
    return "__".join(sorted([str(a), str(b)]))


def _styles_path(club_dir: Path, loom_id: str) -> Path:
    return Path(club_dir) / "crossovers" / loom_id / "styles.json"


def _textures_path(club_dir: Path, loom_id: str) -> Path:
    return Path(club_dir) / "crossovers" / loom_id / "textures.json"


def load_edge_styles(club_dir: Path, loom_id: str) -> Dict[str, str]:
    """The per-edge transition personality map {edge_key: profile} for a loom (empty = all default
    carrier/ribbon-drift). Stored Club-side next to the crossover clips."""
    p = _styles_path(Path(club_dir), loom_id)
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            return {str(k): str(v) for k, v in data.items()} if isinstance(data, dict) else {}
        except Exception:
            return {}
    return {}


def load_edge_textures(club_dir: Path, loom_id: str) -> Dict[str, str]:
    """The per-edge line-texture map {edge_key: image_path} for a loom."""
    p = _textures_path(Path(club_dir), loom_id)
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            return {str(k): str(v) for k, v in data.items()} if isinstance(data, dict) else {}
        except Exception:
            return {}
    return {}


def set_edge_style(club_dir: Path, loom_id: str, a: str, b: str, profile: Optional[str]) -> Dict[str, str]:
    """Set (or clear, when profile is None/'ribbon_drift') the transition personality for an edge.
    Returns the updated style map. Does NOT rebake — the caller regenerates the edge."""
    p = _styles_path(Path(club_dir), loom_id)
    styles = load_edge_styles(club_dir, loom_id)
    key = edge_style_key(a, b)
    if profile and profile != "ribbon_drift":
        styles[key] = profile
    else:
        styles.pop(key, None)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(styles, indent=2, ensure_ascii=False), encoding="utf-8")
    return styles


def set_edge_texture(club_dir: Path, loom_id: str, a: str, b: str, texture_path: Optional[str]) -> Dict[str, str]:
    """Set or clear an edge's visual line texture path. Returns updated texture map."""
    p = _textures_path(Path(club_dir), loom_id)
    textures = load_edge_textures(club_dir, loom_id)
    key = edge_style_key(a, b)
    if texture_path:
        textures[key] = str(texture_path)
    else:
        textures.pop(key, None)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(textures, indent=2, ensure_ascii=False), encoding="utf-8")
    return textures


def sync_crossovers(
    project_root: Path,
    loom_path: Path,
    universe: str,
    nodes: List[Dict[str, Any]],
    *,
    only_nodes: Optional[Iterable[str]] = None,
    only_edge: Optional[Tuple[str, str]] = None,
    on_progress: Optional[Callable[[int, int, str], None]] = None,
) -> Tuple[int, int]:
    """Bake the loom's relationship crossovers Club-side. Returns (built_files, failed_edges).

    `only_nodes` restricts the bake to edges touching those node ids (a per-node / batch
    regenerate); `only_edge=(a,b)` restricts to exactly one edge — both MERGE into the existing set
    (unrelated crossovers left alone). None rebuilds the whole loom (atomic full swap). Each edge is
    baked with its chosen transition PERSONALITY (club styles.json; default = ribbon-drift carrier).
    `on_progress(done, total, label)` fires once before each edge and once at the end, so a UI can
    drive a progress bar / ETA. Either way the bake is transactional: an interruption or a per-edge
    failure never corrupts the live set."""
    from bookmark.mint import extract_loop, mint_crossover

    loom_id = _slug(universe) or loom_path.stem
    club_dir = project_root / "club"
    cross_dir = club_dir / "crossovers" / loom_id
    styles = load_edge_styles(club_dir, loom_id)

    edges = relationship_edges(nodes)
    if only_edge is not None:
        want = edge_style_key(*only_edge)
        edges = [(left, right) for (left, right) in edges if edge_style_key(left, right) == want]
    elif only_nodes is not None:
        only = {str(n).strip() for n in only_nodes if str(n).strip()}
        edges = [(left, right) for (left, right) in edges if left in only or right in only]
    partial = only_edge is not None or only_nodes is not None
    total = len(edges)

    nodes_by_id = {str(node.get("id", "")).strip(): node for node in nodes}
    built = 0
    failed = 0
    # Transactional bake: stage into a temp club, then atomically swap in. The carrier renders take
    # minutes and run in a daemon thread (loom app2), so a user closing the app mid-bake would
    # otherwise kill the render and leave a half-written crossover (one direction "works", the rest
    # fall back to a bare cut). Staging means an interruption never corrupts the existing set; a
    # per-edge failure cleans its own partials so they can't be swapped in.
    with tempfile.TemporaryDirectory(prefix="loom-crossovers-") as tmp:
        tmp_root = Path(tmp)
        stage_club = tmp_root / "club"
        stage_dir = stage_club / "crossovers" / loom_id
        stage_dir.mkdir(parents=True, exist_ok=True)
        loops: Dict[str, Path] = {}
        for node_id, node in nodes_by_id.items():
            oradio = str(node.get("oradio", "")).strip()
            if not oradio:
                continue
            candidate = Path(oradio)
            if not candidate.is_absolute():
                candidate = (loom_path.parent / candidate).resolve()
            if not candidate.exists():
                continue
            try:
                loops[node_id] = extract_loop(candidate, tmp_root / f"{node_id}.loop.mp4")
            except Exception:
                continue

        for i, (left, right) in enumerate(edges):
            if on_progress is not None:
                try:
                    on_progress(i, total, f"{left} ↔ {right}")
                except Exception:
                    pass
            loop_left = loops.get(left)
            loop_right = loops.get(right)
            if loop_left is None or loop_right is None:
                failed += 1
                continue
            try:
                paths = mint_crossover(
                    loop_left,
                    loop_right,
                    from_id=left,
                    to_id=right,
                    loom_id=loom_id,
                    club_dir=stage_club,
                    profile=styles.get(edge_style_key(left, right)),
                )
                # Both directions get a forward .entry (the shell looks up `from__to.entry.mp4`).
                rev_entry = stage_dir / f"{right}__{left}.entry.mp4"
                rev_exit = stage_dir / f"{right}__{left}.exit.mp4"
                shutil.copyfile(str(paths["exit"]), rev_entry)
                shutil.copyfile(str(paths["entry"]), rev_exit)
                built += 2
            except Exception:
                failed += 1
                # drop this edge's partials so a half-render can't be swapped in
                for stem in (f"{left}__{right}", f"{right}__{left}"):
                    for suffix in (".entry.mp4", ".exit.mp4"):
                        try:
                            (stage_dir / f"{stem}{suffix}").unlink()
                        except OSError:
                            pass

        # Swap the freshly-staged set in only if we actually built something; otherwise leave the
        # existing crossovers untouched (no regression on a fully-failed/interrupted bake).
        if built:
            cross_dir.mkdir(parents=True, exist_ok=True)
            if not partial:
                # full rebuild -> atomic replace of the whole loom's crossover set, but PRESERVE the
                # author's custom/ clips (hard-mode overrides) AND the styles.json — regen never
                # wipes those.
                existing_custom = cross_dir / "custom"
                if existing_custom.is_dir():
                    shutil.copytree(existing_custom, stage_dir / "custom", dirs_exist_ok=True)
                existing_styles = cross_dir / "styles.json"
                if existing_styles.is_file():
                    shutil.copyfile(existing_styles, stage_dir / "styles.json")
                if cross_dir.exists():
                    shutil.rmtree(cross_dir, ignore_errors=True)
                shutil.move(str(stage_dir), str(cross_dir))
            else:
                # partial regenerate -> merge just the rebuilt edges over the existing set
                for f in stage_dir.iterdir():
                    if f.name in ("custom", "styles.json"):
                        continue   # never overwrite custom clips / the style map on a partial bake
                    shutil.move(str(f), str(cross_dir / f.name))

    if on_progress is not None:
        try:
            on_progress(total, total, "done")
        except Exception:
            pass
    return built, failed
