from oradio_engine.club_packages import (
    SCHEMA_VERSION,
    build_package_manifest,
    build_readiness_report,
    load_package_requests,
    package_requests_path,
    record_package_request,
)


def test_package_manifest_exposes_repo_scale_packages(monkeypatch, tmp_path):
    monkeypatch.setenv("ORADIO_CLUB_DIR", str(tmp_path / "club"))
    manifest = build_package_manifest()
    ids = {item["id"] for item in manifest["packages"]}
    assert manifest["schema_version"] == SCHEMA_VERSION
    assert manifest["bootstrap_required"] is True
    assert {"kernel", "ribbon-os", "radio-bricks", "atlas", "oradio-gallery"} <= ids

    packages = {item["id"]: item for item in manifest["packages"]}
    assert any(profile["default"] for profile in packages["radio-bricks"]["profiles"])
    assert any(profile["id"] == "engine-only" for profile in packages["atlas"]["profiles"])
    assert "bookmark.py" in packages["kernel"]["artifacts"]
    assert any(bundle["id"] == "desktop-core" for bundle in packages["ribbon-os"]["dependency_bundles"])
    assert any(bundle["id"] == "voice-control" for bundle in packages["ribbon-os"]["dependency_bundles"])
    assert any(probe["target"] == "audio_cli" for probe in packages["ribbon-os"]["readiness_probes"])
    assert any(bundle["required"] for bundle in packages["kernel"]["dependency_bundles"])


def test_record_package_request_persists_jsonl(monkeypatch, tmp_path):
    monkeypatch.setenv("ORADIO_CLUB_DIR", str(tmp_path / "club"))
    req = record_package_request("radio-bricks", "core", action="install")
    path = package_requests_path()
    assert path.exists()
    rows = load_package_requests()
    assert rows[-1]["request_id"] == req.request_id
    assert rows[-1]["package_id"] == "radio-bricks"
    assert rows[-1]["profile_id"] == "core"


def test_readiness_report_exposes_probe_results():
    report = build_readiness_report()
    assert report["schema_version"] == "club.readiness.v1"
    packages = {item["id"]: item for item in report["packages"]}
    assert "ribbon-os" in packages
    assert any(bundle["id"] == "desktop-core" for bundle in packages["ribbon-os"]["dependency_bundles"])
    assert any(probe["target"] == "audio_cli" for probe in packages["ribbon-os"]["readiness_probes"])
