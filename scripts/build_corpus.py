"""Write the Ask IDCTF corpus from docs/ into site/ask/.

One text file holds every page, each under a header line the function and
the prompt rely on. Figure images, captions and anchors go; a table inside
a `<figure class="ekdn-table">` wrapper stays, because the wrapper is
layout and the table is prose.

    === PAGE: <title> | URL: <url> ===

A page still carrying the `(soon)` marker is reduced to its header plus one
line, so the model can say the chapter is not written instead of guessing.
`urls.json` lists every published page URL; the function drops any source
the model returns that is not in it.

Runs after `mkdocs build --strict`, because it writes into `site/`:

    .venv/bin/python scripts/build_corpus.py
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
OUT = ROOT / "site" / "ask"

SOON_MARKER = '<p class="ekdn-soon">(soon)</p>'
NOT_WRITTEN = "This page is not written yet."

_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
_TITLE = re.compile(r"^title:\s*(.+?)\s*$", re.M)
_COMMENT = re.compile(r"<!--.*?-->", re.S)
_FIGCAPTION = re.compile(r"<figcaption\b.*?</figcaption>", re.S)
_SVG = re.compile(r"<svg\b.*?</svg>", re.S)
_IMAGE_LINE = re.compile(r"^\s*!\[[^\]]*\]\([^)]*\)(\{[^}]*\})?\s*$", re.M)
_ANCHOR_LINE = re.compile(r"^\[\]\(\)\{\s*#[^}]*\}\s*$", re.M)
_HEADING_ID = re.compile(r"\s*\{#[^}]*\}\s*$", re.M)
_HTML_TAG = re.compile(r"</?(div|span|p|figure)\b[^>]*>")
_BLANK_RUN = re.compile(r"\n{3,}")


def clean_page(text: str) -> tuple[str, str, bool]:
    """Return (title, body, is_soon) for one Markdown page."""
    title = ""
    match = _FRONTMATTER.match(text)
    if match:
        found = _TITLE.search(match.group(1))
        if found:
            title = found.group(1).strip().strip('"').strip("'")
        text = text[match.end():]
    is_soon = SOON_MARKER in text
    if is_soon:
        return title, NOT_WRITTEN + "\n", True
    text = _COMMENT.sub("", text)
    text = _FIGCAPTION.sub("", text)
    text = _SVG.sub("", text)
    text = _IMAGE_LINE.sub("", text)
    text = _ANCHOR_LINE.sub("", text)
    text = _HEADING_ID.sub("", text)
    text = _HTML_TAG.sub("", text)
    text = _BLANK_RUN.sub("\n\n", text)
    return title, text.strip() + "\n", False


def page_url(md_path: pathlib.Path, docs_root: pathlib.Path) -> str:
    rel = md_path.relative_to(docs_root).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "index":
        parts = parts[:-1]
    return "/" + "/".join(parts) + ("/" if parts else "")


def build(docs_root: pathlib.Path, out_dir: pathlib.Path) -> tuple[int, int]:
    out_dir.mkdir(parents=True, exist_ok=True)
    pages = sorted(docs_root.rglob("*.md"))
    chunks: list[str] = []
    urls: list[str] = []
    soon_count = 0
    for path in pages:
        title, body, is_soon = clean_page(path.read_text(encoding="utf-8"))
        url = page_url(path, docs_root)
        title = title or path.stem
        soon_count += int(is_soon)
        urls.append(url)
        chunks.append(f"=== PAGE: {title} | URL: {url} ===\n{body}")
    (out_dir / "corpus.txt").write_text("\n".join(chunks), encoding="utf-8")
    (out_dir / "urls.json").write_text(json.dumps(urls, indent=0), encoding="utf-8")
    return len(pages), soon_count


def main() -> int:
    if not (ROOT / "site").is_dir():
        print("site/ is missing: run mkdocs build first", file=sys.stderr)
        return 1
    pages, soon = build(DOCS, OUT)
    print(f"corpus: {pages} pages, {soon} not written, written to {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
