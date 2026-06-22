"""Repo-scale package contract for the Club.

The engine-native Club already resolves machine-level capabilities, consent, and thin
plugin fetches. This module adds the higher-level package layer: what the Club should
offer when the user is setting up a machine for the RibbonOS family.
"""
from __future__ import annotations

import importlib.util
import json
import os
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


SCHEMA_VERSION = "club.package_manifest.v1"


def club_dir() -> Path:
    base = os.environ.get("ORADIO_CLUB_DIR") or os.path.join(os.path.expanduser("~"), ".oradio_club")
    path = Path(base)
    path.mkdir(parents=True, exist_ok=True)
    return path


def package_requests_path() -> Path:
    return club_dir() / "package_requests.jsonl"


@dataclass(frozen=True)
class PackageProfile:
    id: str
    label: str
    description: str
    default: bool = False


@dataclass(frozen=True)
class DependencyBundle:
    id: str
    label: str
    description: str
    python_packages: List[str] = field(default_factory=list)
    import_probes: List[str] = field(default_factory=list)
    default: bool = False
    required: bool = False
    fix_hint: str = ""


@dataclass(frozen=True)
class ReadinessProbe:
    id: str
    label: str
    target: str
    required: bool = False
    fix_hint: str = ""


@dataclass(frozen=True)
class ClubPackage:
    id: str
    title: str
    kind: str
    summary: str
    source_repo: str
    install_mode: str
    provides: List[str] = field(default_factory=list)
    requires: List[str] = field(default_factory=list)
    profiles: List[PackageProfile] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)
    dependency_bundles: List[DependencyBundle] = field(default_factory=list)
    readiness_probes: List[ReadinessProbe] = field(default_factory=list)
    size_class: str = "normal"


@dataclass(frozen=True)
class PackageRequest:
    request_id: str
    package_id: str
    profile_id: str
    action: str
    created_at: float
    status: str = "requested"


def default_packages() -> List[ClubPackage]:
    return [
        ClubPackage(
            id="ribbon-os",
            title="RibbonOS Runtime",
            kind="runtime",
            summary="The opener, player, Club wiring, render path, and install/update runtime.",
            source_repo="ribbon-os",
            install_mode="recommended",
            provides=["oradio_open", "club_runtime", "render_runtime", "file_association"],
            profiles=[PackageProfile("standard", "Standard", "Install the normal RibbonOS runtime.", default=True)],
            artifacts=["RibbonOS Bootstrap"],
            dependency_bundles=[
                DependencyBundle(
                    id="desktop-core",
                    label="Desktop Core",
                    description="The main desktop shell, image stack, and runtime fetch/client tools.",
                    python_packages=["PyYAML>=6.0", "Pillow", "opencv-python", "numpy", "requests"],
                    import_probes=["yaml", "PIL", "cv2", "numpy", "requests"],
                    default=True,
                    required=True,
                    fix_hint="Install the core RibbonOS desktop dependencies before first launch.",
                ),
                DependencyBundle(
                    id="media-audio",
                    label="Media Audio",
                    description="Playback support for soundtrack, mixer, and local audio handling.",
                    python_packages=["pygame", "sounddevice", "soundfile"],
                    import_probes=["pygame", "sounddevice", "soundfile"],
                    default=True,
                    required=False,
                    fix_hint="Install the audio bundle for full soundtrack and sound-device support.",
                ),
                DependencyBundle(
                    id="voice-control",
                    label="Voice Control",
                    description="Optional Audio CLI / voice-command support used by the shell.",
                    python_packages=["audio_cli"],
                    import_probes=["audio_cli"],
                    default=False,
                    required=False,
                    fix_hint="Install the Audio CLI companion package or disable voice control in RibbonOS settings.",
                ),
            ],
            readiness_probes=[
                ReadinessProbe("import-yaml", "PyYAML import", "yaml", required=True, fix_hint="Install PyYAML."),
                ReadinessProbe("import-pil", "Pillow import", "PIL", required=True, fix_hint="Install Pillow."),
                ReadinessProbe("import-cv2", "OpenCV import", "cv2", required=False, fix_hint="Install opencv-python for full visual runtime support."),
                ReadinessProbe("import-pygame", "Pygame import", "pygame", required=False, fix_hint="Install pygame for soundtrack and mixer support."),
                ReadinessProbe("import-audio-cli", "Audio CLI import", "audio_cli", required=False, fix_hint="Install the Audio CLI companion package or disable voice control."),
            ],
        ),
        ClubPackage(
            id="kernel",
            title="Kernel",
            kind="kernel",
            summary="The canonical kernel artifact, Bookmark source workstation, lineage authority, mint policy, and export fixtures.",
            source_repo="kernel",
            install_mode="required",
            provides=["kernel_authority", "kernel_oradio", "mint_policy", "bookmark_source"],
            profiles=[PackageProfile("canonical", "Canonical", "Install the shipped kernel line.", default=True)],
            artifacts=["kernel.oradio", "bookmark.py"],
            dependency_bundles=[
                DependencyBundle(
                    id="mint-core",
                    label="Mint Core",
                    description="Dependencies needed to mint and preview the canon kernel line from Bookmark.",
                    python_packages=["PyYAML>=6.0", "Pillow", "pygame"],
                    import_probes=["yaml", "PIL", "pygame"],
                    default=True,
                    required=True,
                    fix_hint="Install the kernel minting dependencies before exporting or previewing Bookmark.",
                ),
            ],
            readiness_probes=[
                ReadinessProbe("import-pil", "Pillow import", "PIL", required=True, fix_hint="Install Pillow for kernel artwork and previews."),
                ReadinessProbe("import-pygame", "Pygame import", "pygame", required=False, fix_hint="Install pygame for optional kernel audio preview."),
            ],
            size_class="tiny",
        ),
        ClubPackage(
            id="radio-bricks",
            title="Radio Bricks",
            kind="bricks",
            summary="The mined shared brick garden: Python, HTML, JSON, and future concept bricks.",
            source_repo="radio-bricks",
            install_mode="optional",
            provides=["brick_catalog", "python_bricks", "html_bricks", "json_bricks"],
            profiles=[
                PackageProfile("core", "Core", "A small recommended starter set for normal use.", default=True),
                PackageProfile("recommended", "Recommended", "A broader practical brick garden."),
                PackageProfile("all", "All", "Install the full current brick garden."),
                PackageProfile("custom", "Pick & Choose", "Choose families and subsets later in the Club."),
            ],
            size_class="large",
        ),
        ClubPackage(
            id="atlas",
            title="Atlas Determinism",
            kind="atlas",
            summary="The determinism engine, loombit substrate, and heavyweight shard/bank/dict payloads.",
            source_repo="atlas",
            install_mode="optional",
            provides=["determinism_engine", "loombits", "atlas_banks"],
            profiles=[
                PackageProfile("engine-only", "Engine Only", "Install only the determinism code paths.", default=True),
                PackageProfile("banks", "Banks", "Install code plus core loombit banks."),
                PackageProfile("full", "Full", "Install Atlas with all declared heavy payloads."),
            ],
            size_class="heavy",
        ),
        ClubPackage(
            id="oradio-gallery",
            title="Oradio Gallery",
            kind="gallery",
            summary="Public example `.oradio` artifacts, loom graphs, and showcase stations.",
            source_repo="oradio-gallery",
            install_mode="optional",
            provides=["example_oradios", "gallery_browse", "loom_graph_inputs"],
            profiles=[
                PackageProfile("featured", "Featured", "Install a small featured gallery set.", default=True),
                PackageProfile("all", "All", "Install the full public gallery mirror."),
            ],
            artifacts=["featured.oradio", "featured.loom"],
        ),
    ]


def build_package_manifest() -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": time.time(),
        "bootstrap_required": True,
        "bootstrap_artifacts": ["RibbonOS Bootstrap", "kernel.oradio"],
        "packages": [
            {
                **asdict(pkg),
                "profiles": [asdict(profile) for profile in pkg.profiles],
            }
            for pkg in default_packages()
        ],
    }


def _probe_import(target: str) -> Dict[str, Any]:
    try:
        spec = importlib.util.find_spec(target)
    except Exception as exc:
        return {"ok": False, "target": target, "error": str(exc)}
    return {"ok": bool(spec is not None), "target": target, "error": None if spec is not None else "not installed"}


def build_readiness_report() -> Dict[str, Any]:
    packages = default_packages()
    package_reports: List[Dict[str, Any]] = []
    blocking: List[str] = []
    warnings: List[str] = []
    ready = True

    for pkg in packages:
        bundle_reports: List[Dict[str, Any]] = []
        probe_reports: List[Dict[str, Any]] = []

        for bundle in pkg.dependency_bundles:
            probe_results = [_probe_import(target) for target in bundle.import_probes]
            missing = [result["target"] for result in probe_results if not result["ok"]]
            bundle_ok = not missing
            if bundle.required and not bundle_ok:
                ready = False
                blocking.append(f"{pkg.id}:{bundle.id}")
            elif missing:
                warnings.append(f"{pkg.id}:{bundle.id}")
            bundle_reports.append({
                "id": bundle.id,
                "label": bundle.label,
                "required": bundle.required,
                "default": bundle.default,
                "ok": bundle_ok,
                "missing": missing,
                "python_packages": list(bundle.python_packages),
                "fix_hint": bundle.fix_hint,
            })

        for probe in pkg.readiness_probes:
            result = _probe_import(probe.target)
            if probe.required and not result["ok"]:
                ready = False
            probe_reports.append({
                "id": probe.id,
                "label": probe.label,
                "target": probe.target,
                "required": probe.required,
                "ok": result["ok"],
                "error": result["error"],
                "fix_hint": probe.fix_hint,
            })

        package_reports.append({
            "id": pkg.id,
            "title": pkg.title,
            "source_repo": pkg.source_repo,
            "dependency_bundles": bundle_reports,
            "readiness_probes": probe_reports,
        })

    return {
        "schema_version": "club.readiness.v1",
        "generated_at": time.time(),
        "ready": ready,
        "blocking": blocking,
        "warnings": warnings,
        "packages": package_reports,
    }


def record_package_request(package_id: str, profile_id: str, action: str = "install") -> PackageRequest:
    req = PackageRequest(
        request_id=uuid.uuid4().hex,
        package_id=str(package_id),
        profile_id=str(profile_id),
        action=str(action),
        created_at=time.time(),
    )
    with package_requests_path().open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(asdict(req), ensure_ascii=False) + "\n")
    return req


def load_package_requests(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    path = package_requests_path()
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            text = line.strip()
            if not text:
                continue
            try:
                rows.append(json.loads(text))
            except json.JSONDecodeError:
                continue
    if limit is not None and limit >= 0:
        return rows[-limit:]
    return rows
