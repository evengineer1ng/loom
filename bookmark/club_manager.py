from __future__ import annotations

import json
import subprocess
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict

import app_paths
from oradio_engine.club_packages import (
    build_package_manifest,
    build_readiness_report,
    load_package_requests,
    record_package_request,
)


def launch_backend() -> Dict[str, Any]:
    cmd = app_paths.opener_command()
    try:
        subprocess.Popen(cmd, cwd=str(app_paths.bundle_root()))
    except Exception as exc:
        return {"ok": False, "error": str(exc), "command": cmd}
    return {"ok": True, "command": cmd}


def open_club_manager(asset_path: str | Path, *, host: str = "127.0.0.1", port: int = 0,
                      open_browser: bool = True) -> Dict[str, Any]:
    asset = Path(asset_path)
    if not asset.exists():
        return {"error": f"club asset not found: {asset}"}

    class Handler(BaseHTTPRequestHandler):
        def _send_json(self, payload: Dict[str, Any], status: int = 200) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _send_file(self, path: Path) -> None:
            data = path.read_bytes()
            content_type = "text/html; charset=utf-8" if path.suffix.lower() == ".html" else "application/octet-stream"
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self) -> None:  # noqa: N802
            if self.path in ("/", f"/{asset.name}"):
                self._send_file(asset)
                return
            if self.path == "/api/manifest":
                self._send_json(build_package_manifest())
                return
            if self.path == "/api/readiness":
                self._send_json(build_readiness_report())
                return
            if self.path == "/api/requests":
                self._send_json({"requests": load_package_requests(limit=40)})
                return
            self.send_error(404, "Not found")

        def do_POST(self) -> None:  # noqa: N802
            if self.path == "/api/launch-backend":
                result = launch_backend()
                self._send_json(result, status=200 if result.get("ok") else 500)
                return
            if self.path != "/api/request":
                self.send_error(404, "Not found")
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                length = 0
            raw = self.rfile.read(max(0, length))
            try:
                payload = json.loads(raw.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                self._send_json({"ok": False, "error": "invalid json"}, status=400)
                return
            package_id = str(payload.get("package_id") or "").strip()
            profile_id = str(payload.get("profile_id") or "").strip()
            action = str(payload.get("action") or "install").strip()
            if not package_id or not profile_id:
                self._send_json({"ok": False, "error": "package_id and profile_id are required"}, status=400)
                return
            req = record_package_request(package_id, profile_id, action=action)
            self._send_json({"ok": True, "request": req.__dict__})

        def log_message(self, fmt: str, *args: Any) -> None:
            return

    httpd = ThreadingHTTPServer((host, port), Handler)
    actual_port = int(httpd.server_address[1])
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    url = f"http://{host}:{actual_port}/{asset.name}"
    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    return {"url": url, "host": host, "port": actual_port, "httpd": httpd, "asset": str(asset)}
