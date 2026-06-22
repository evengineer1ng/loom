from bookmark import club_manager
import json


def test_launch_backend_returns_command(monkeypatch):
    called = {}

    def fake_popen(cmd, cwd=None):
        called["cmd"] = list(cmd)
        called["cwd"] = cwd
        class _Proc:
            pass
        return _Proc()

    monkeypatch.setattr(club_manager.subprocess, "Popen", fake_popen)
    result = club_manager.launch_backend()
    assert result["ok"] is True
    assert result["command"]
    assert called["cmd"] == result["command"]


def test_readiness_endpoint_returns_json(monkeypatch, tmp_path):
    asset = tmp_path / "club.html"
    asset.write_text("<!doctype html><title>club</title>", encoding="utf-8")
    served = club_manager.open_club_manager(asset, open_browser=False)
    try:
        import urllib.request

        with urllib.request.urlopen(f"{served['url'].rsplit('/', 1)[0]}/api/readiness") as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        assert payload["schema_version"] == "club.readiness.v1"
        assert "packages" in payload
    finally:
        served["httpd"].shutdown()
