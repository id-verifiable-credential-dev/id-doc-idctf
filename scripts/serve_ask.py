"""Serve the built site and the Ask IDCTF function from one local origin.

`mkdocs serve` cannot host the function, and the function sends no CORS
headers, so the drawer has to call `/api/chat` on the origin it was served
from. This server does both: static files from `site/`, and `POST /api/chat`
through the same handler class Vercel runs (`api/chat.py`).

    .venv/bin/python -m mkdocs build --strict && .venv/bin/python scripts/build_corpus.py
    .venv/bin/python scripts/serve_ask.py                            # http://127.0.0.1:8010

Variables come from `.env` at the repository root (gitignored; `.env.example`
lists them) or from the environment, which wins. Rebuild and restart after
editing a page or the drawer; this server does not watch files. The key is
never written anywhere by this script.
"""

from __future__ import annotations

import os
import pathlib
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
ENV_FILE = ROOT / ".env"
sys.path.insert(0, str(ROOT / "api"))


def load_env_file(path: pathlib.Path) -> int:
    """Read KEY=value lines into os.environ without overriding what is set. Returns the count."""
    if not path.is_file():
        return 0
    count = 0
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value
            count += 1
    return count

import chat  # noqa: E402


class DevHandler(SimpleHTTPRequestHandler):
    """Static site plus the function, on one origin."""

    timeout = chat.handler.timeout
    _send = chat.handler._send
    do_POST = chat.handler.do_POST

    def do_GET(self) -> None:
        if self.path.startswith("/api/"):
            self._send(405, {"error": "bad_request"})
            return
        super().do_GET()

    def log_message(self, format: str, *args) -> None:
        # Static requests stay quiet; the service logs the function's own lines.
        return


def main() -> int:
    if not (SITE / "ask" / "corpus.txt").is_file():
        print("site/ask/corpus.txt is missing: build the site and the corpus first", file=sys.stderr)
        return 1
    loaded = load_env_file(ENV_FILE)
    if loaded:
        print(f"read {loaded} variable(s) from .env", flush=True)
    os.environ.setdefault("ASK_CORPUS_DIR", str(SITE / "ask"))
    if not os.environ.get("GEMINI_API_KEY"):
        print("GEMINI_API_KEY is not set: every question will answer 503", file=sys.stderr)
    port = int(os.environ.get("PORT", "8010"))  # 8000 is often taken by mkdocs serve or Docker
    server = ThreadingHTTPServer(("127.0.0.1", port), partial(DevHandler, directory=str(SITE)))
    print(f"serving site/ and /api/chat at http://127.0.0.1:{port}/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
