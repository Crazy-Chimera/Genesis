from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .core import GenesisConfig, GenesisObserver, GenesisUniverse


class GenesisServer:
    """Small HTTP wrapper for Render; the universe rules remain unchanged."""

    def __init__(self, config: GenesisConfig = GenesisConfig()) -> None:
        self.universe = GenesisUniverse(config)
        self.observer = GenesisObserver()
        self._lock = threading.Lock()

    def step(self) -> dict[str, float | int]:
        with self._lock:
            self.universe.step()
            return self.observer.measure(self.universe)

    def state(self) -> dict[str, float | int]:
        with self._lock:
            return self.observer.measure(self.universe)


class Handler(BaseHTTPRequestHandler):
    server_version = "GENESIS/0.1"

    def do_GET(self) -> None:
        app: GenesisServer = self.server.genesis_app  # type: ignore[attr-defined]

        if self.path == "/health":
            self._json(200, {"status": "ok", **app.state()})
            return

        if self.path == "/state":
            self._json(200, app.state())
            return

        if self.path == "/step":
            self._json(200, app.step())
            return

        self._json(
            200,
            {
                "name": "GENESIS",
                "experiment": "GENESIS-PW-001",
                "endpoints": ["/health", "/state", "/step"],
            },
        )

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    import os

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "10000"))

    app = GenesisServer()
    server = ThreadingHTTPServer((host, port), Handler)
    server.genesis_app = app  # type: ignore[attr-defined]
    print(f"GENESIS server listening on {host}:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
