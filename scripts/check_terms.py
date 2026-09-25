"""Check term spelling in docs/ against the closed list in the glossary.

The list lives in `source-data/Glosarium dan Konvensi IDCTF.md`, section D.1.
This script holds no terms of its own: it parses that table, so the glossary
stays the single source of truth and no third one is born.

Five classes, from D.1:

  standar   exact as the standard writes it, in any position
  protokol  exact as the specification writes it
  artefak   an IDCTF proper noun, always capitalized
  peran     an IDCTF role name, always capitalized
  umum      a common noun, always lowercase. A capital is allowed only at the
            start of a sentence, a table cell, a heading, or a list item.

For `umum` the forbidden forms are derived rather than listed: the Title Cased
form is wrong anywhere, and the Sentence cased form is wrong outside the
positions above. A one-word common noun has no Title Cased form of its own, so
its single capitalized form is judged by position alone. Everything the checker must not read (code, comments, link
targets, frontmatter, HTML) is masked before the search, and longer canonical
terms are masked before shorter ones so `Status List Token` never registers as
a bad `status list`.

Run:  .venv/bin/python scripts/check_terms.py
Exit: 0 clean, 1 if anything was found.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
GLOSSARY = ROOT / "source-data/Glosarium dan Konvensi IDCTF.md"
DOCS = ROOT / "docs"
CLASSES = {"standar", "protokol", "artefak", "peran", "umum"}

# A capital is allowed when the term opens a sentence or a structural slot.
# Decorations that may sit between the slot and the word are stripped first.
OPENERS = ("", ".", "!", "?", ":", "|", ">")
DECOR = "*_\"'“‘([-–—"


def load_terms() -> list[dict]:
    rows, in_table = [], False
    for line in GLOSSARY.read_text().splitlines():
        if line.startswith("| Istilah | Kelas |"):
            in_table = True
            continue
        if in_table:
            if not line.startswith("|"):
                break
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) != 4 or set(cells[0]) <= set("- "):
                continue
            term, klass, canonical, banned = cells
            if klass not in CLASSES:
                sys.exit(f"D.1: unknown class {klass!r} on term {term!r}")
            rows.append({
                "term": term,
                "class": klass,
                "canonical": canonical,
                "banned": [b.strip() for b in banned.split(",") if b.strip()],
            })
    if not rows:
        sys.exit("D.1: term table not found in the glossary")
    return rows


def mask(text: str) -> str:
    """Blank out every span the rule does not govern, preserving offsets."""
    out = list(text)

    def blank(m: re.Match) -> None:
        for i in range(m.start(), m.end()):
            if out[i] != "\n":
                out[i] = "\x00"

    patterns = [
        r"(?s)\A---\n.*?\n---\n",        # frontmatter
        r"(?s)<!--.*?-->",               # HTML comments
        r"(?s)```.*?```",                # fenced code
        r"`[^`\n]*`",                    # inline code
        r"\]\([^)\n]*\)",                # link and image targets
        r"(?s)<[^>\n]+>",                # HTML tags and their attributes
        r"https?://\S+",                 # bare URLs
    ]
    for pat in patterns:
        for m in re.finditer(pat, text):
            blank(m)
    return "".join(out)


def opener_before(line: str, col: int) -> bool:
    prefix = line[:col].rstrip()
    # A link's text is a title slot, so it keeps a title's capital wherever the
    # link sits in the sentence. Two forms count: the title alone, as in
    # [Trusted list and cache](...), and the cross-reference form CLAUDE.md
    # section 5 requires, [Section 6.1.1, Trusted list](...).
    opened = prefix.rfind("[")
    if opened != -1 and "]" not in prefix[opened:]:
        inner = prefix[opened + 1:]
        if re.fullmatch(r"(Section\s[\d.]+,)?\s*", inner):
            return True
    prefix = prefix.rstrip(DECOR).rstrip()
    if not prefix:
        return True
    # Every body heading in this repository opens with its section number
    # (CLAUDE.md section 5), so `### 6.1.1 Trusted list` is a heading slot and
    # the capital is correct there.
    if re.fullmatch(r"\s*(#{1,6}|[-*+]|\d+\.|>)[\s\d.]*", prefix):
        return True
    return prefix[-1] in OPENERS


def variants(canonical: str) -> tuple[str, str]:
    """Title Cased and Sentence cased forms of a common noun."""
    words = canonical.split()
    title = " ".join(w[:1].upper() + w[1:] for w in words)
    sentence = canonical[:1].upper() + canonical[1:]
    return title, sentence


def check() -> int:
    terms = load_terms()
    # Longest canonical first, so a long name shields the short word inside it:
    # `Status List Token` must not register as a badly cased `status list`.
    # Only the canonical spellings shield, never their Title Cased variants,
    # because for a common noun that variant is exactly what we are hunting.
    shields = sorted({t["canonical"] for t in terms}, key=len, reverse=True)
    findings = []

    for path in sorted(DOCS.rglob("*.md")):
        plain = mask(path.read_text())
        shielded = plain
        for shield in shields:
            shielded = shielded.replace(shield, "\x00" * len(shield))

        # A spelling listed in D.1 is wrong wherever it appears, so it is
        # searched unshielded. A case slip on a common noun is derived from the
        # canonical form instead, and searched with the long names masked out.
        plain_lines, shielded_lines = plain.splitlines(), shielded.splitlines()
        for term in terms:
            checks: list[tuple[str, bool, list[str]]] = [
                (b, False, plain_lines) for b in term["banned"]]
            if term["class"] == "umum":
                title, sentence = variants(term["canonical"])
                if sentence == title:
                    # One word, so the two variants collapse. The only capital
                    # it can carry is the sentence one, judged by position.
                    checks.append((title, True, shielded_lines))
                else:
                    checks.append((title, False, shielded_lines))
                    checks.append((sentence, True, shielded_lines))

            for form, positional, lines in checks:
                for n, line in enumerate(lines, 1):
                    for m in re.finditer(re.escape(form), line):
                        if positional and opener_before(line, m.start()):
                            continue
                        findings.append(
                            (path.relative_to(ROOT), n, m.start() + 1,
                             form, term["canonical"], term["class"]))

    findings.sort()
    for rel, n, col, form, canonical, klass in findings:
        print(f"{rel}:{n}:{col}: {form!r} -> {canonical!r}  [{klass}]")
    print(f"\n{len(terms)} terms from D.1, {len(findings)} finding(s) in docs/")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(check())
