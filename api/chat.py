"""POST /api/chat on Vercel. Thin: read, hand to the service, write.

The service package sits next to this file under `_ask/`; the path insert
makes the import work both on Vercel and under the unit tests.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _ask import constants, service  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(name)s %(levelname)s %(message)s")


class handler(BaseHTTPRequestHandler):

    def _send(self, status: int, body: dict) -> None:
        data = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        # A HEAD response states the headers only; writing a body here would
        # violate HTTP (the stdlib's own send_error has the same guard).
        if self.command != "HEAD":
            self.wfile.write(data)

    def do_POST(self) -> None:
        try:
            length = max(0, int(self.headers.get("Content-Length") or 0))
        except ValueError:
            length = 0
        if length > constants.MAX_BODY:
            # Drain (bounded) so the client sees the 413 instead of a reset.
            remaining = min(length, 4 * constants.MAX_BODY)
            while remaining > 0:
                chunk = self.rfile.read(min(remaining, 65536))
                if not chunk:
                    break
                remaining -= len(chunk)
            self._send(413, {"error": "bad_request"})
            return
        raw = self.rfile.read(length)
        headers = {k: v for k, v in self.headers.items()}
        try:
            status, body = service.handle(raw, headers, dict(os.environ))
        except Exception as exc:  # own bug: log the type, never the request
            logging.getLogger("ask").error("unhandled error: %s", type(exc).__name__)
            status, body = 503, {"error": "unavailable"}
        self._send(status, body)

    def do_GET(self) -> None:
        self._send(405, {"error": "bad_request"})

    do_HEAD = do_OPTIONS = do_PUT = do_DELETE = do_PATCH = do_GET

    def log_message(self, format: str, *args) -> None:
        # The default writes the request line; status and timing come from the service log.
        return
