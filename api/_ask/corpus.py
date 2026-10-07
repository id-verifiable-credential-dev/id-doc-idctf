"""Load the corpus once per warm instance.

Locally and under `vercel dev`, ASK_CORPUS_DIR points at `site/ask`. On
Vercel the function fetches its own deployment's `/ask/` files, which the
build step wrote next to the pages.
"""

from __future__ import annotations

import json
import pathlib
import urllib.request

_cache: tuple[str, set[str]] | None = None


def reset() -> None:
    global _cache
    _cache = None


def _read_dir(folder: pathlib.Path) -> tuple[str, set[str]]:
    text = (folder / "corpus.txt").read_text(encoding="utf-8")
    urls = set(json.loads((folder / "urls.json").read_text(encoding="utf-8")))
    return text, urls


def _fetch(base: str) -> tuple[str, set[str]]:
    def get(path: str) -> str:
        with urllib.request.urlopen(f"{base}{path}", timeout=10) as resp:
            return resp.read().decode("utf-8")

    return get("/ask/corpus.txt"), set(json.loads(get("/ask/urls.json")))


def load(env: dict) -> tuple[str, set[str]]:
    global _cache
    if _cache is not None:
        return _cache
    folder = env.get("ASK_CORPUS_DIR")
    if folder:
        try:
            _cache = _read_dir(pathlib.Path(folder))
        except Exception as exc:  # missing file and parse errors alike: the caller maps to 503
            raise OSError(f"corpus dir read failed: {type(exc).__name__}") from exc
        return _cache
    host = env.get("VERCEL_URL")
    if not host:
        raise OSError("no corpus source: set ASK_CORPUS_DIR or VERCEL_URL")
    try:
        _cache = _fetch(f"https://{host}")
    except Exception as exc:  # network and parse errors alike: the caller maps to 503
        raise OSError(f"corpus fetch failed: {type(exc).__name__}") from exc
    return _cache
