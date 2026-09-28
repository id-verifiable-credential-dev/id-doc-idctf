"""Check that every `#fragment` link in docs/ resolves in the built site/.

`mkdocs build --strict` checks that a linked page exists. It never checks the
fragment after the `#`. Body headings here carry their position in `nav:`
(`## 3.1 Issuing`), so renumbering a chapter rewrites every anchor on the page
and silently breaks every link pointing at one. This script closes that gap.

It reads `site/`, so run it after the build:

    .venv/bin/python -m mkdocs build --strict
    .venv/bin/python scripts/check_anchors.py

A link is resolved the way MkDocs publishes the page: `foo/bar.md` becomes
`site/foo/bar/index.html` and `foo/index.md` becomes `site/foo/index.html`.
The `minify` plugin strips attribute quotes, so `id=` is matched both quoted
and bare. Code spans, fenced blocks and HTML comments are masked first, so an
example link inside backticks is never checked.

Exit: 0 clean, 1 if any fragment does not resolve.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SITE = ROOT / "site"

# ](target#fragment) and ](#fragment); the target may be empty for a same-page link.
LINK = re.compile(r"\]\(\s*([^)\s#]*)#([A-Za-z0-9_.:-]+)\s*\)")
ID_ATTR = re.compile(r"""\sid=(?:"([^"]+)"|'([^']+)'|([A-Za-z0-9_.:-]+))""")
MASK = (
    re.compile(r"```.*?```", re.S),
    re.compile(r"~~~.*?~~~", re.S),
    re.compile(r"`[^`\n]*`"),
    re.compile(r"<!--.*?-->", re.S),
)


def mask(text: str) -> str:
    """Blank out code and comments, keeping offsets so line numbers stay true."""
    for pattern in MASK:
        text = pattern.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)
    return text


def built_page(md: pathlib.Path) -> pathlib.Path:
    rel = md.relative_to(DOCS)
    if rel.name == "index.md":
        return SITE / rel.parent / "index.html"
    return SITE / rel.parent / rel.stem / "index.html"


def ids_in(html: pathlib.Path) -> set[str]:
    text = html.read_text(encoding="utf-8", errors="ignore")
    return {g for m in ID_ATTR.finditer(text) for g in m.groups() if g}


def main() -> int:
    if not SITE.is_dir():
        sys.exit("site/ not found. Run `.venv/bin/python -m mkdocs build --strict` first.")

    cache: dict[pathlib.Path, set[str] | None] = {}
    findings: list[str] = []
    links = 0

    for md in sorted(DOCS.rglob("*.md")):
        text = mask(md.read_text(encoding="utf-8"))
        for m in LINK.finditer(text):
            target, fragment = m.group(1), m.group(2)
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            links += 1
            line = text.count("\n", 0, m.start()) + 1
            where = f"{md.relative_to(ROOT)}:{line}"
            source = md if not target else (md.parent / target)
            try:
                source = source.resolve().relative_to(DOCS.resolve())
            except ValueError:
                findings.append(f"{where}: link leaves docs/ -> {target}#{fragment}")
                continue
            page = built_page(DOCS / source)
            if page not in cache:
                cache[page] = ids_in(page) if page.is_file() else None
            ids = cache[page]
            if ids is None:
                findings.append(f"{where}: no built page for {target or md.name}")
            elif fragment not in ids:
                findings.append(f"{where}: {target or md.name}#{fragment} does not resolve")

    for finding in findings:
        print(finding)
    print(f"\n{links} fragment link(s) in docs/, {len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
