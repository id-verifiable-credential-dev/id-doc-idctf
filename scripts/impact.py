"""Show what a change to one thing reaches, before the change is made.

The target is any of:

  a path          docs/governance-framework/who-decides.md, CLAUDE.md,
                  images/.../role-map.drawio, scripts/artifacts/logs.py
  a record        0437, tracks/0437, debt/0194
  an identifier   gf-recognition, REQ-GF-012, ts-02-intervals
  a member        intervals.incident_report
  a term          Trust Authority            (as D.1 spells it)
  anything else   matched against block titles, DIDs and Sumber comments

For a page it also lists, per identifier the page defines, the pages that
link to it, since that is where a renamed or reworded heading lands.
Superseded, withdrawn and paid records are counted, not listed, unless
--all is given.

The graph is rebuilt first whenever a source file is newer than it, or a
source file was added or removed, so the answer is never read from an old map.

Run:  .venv/bin/python scripts/impact.py <target> [--all]
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict

import build_graph as bg

CLOSED = ("superseded", "withdrawn", "paid")


def load() -> dict:
    fresh = bg.GRAPH.exists()
    if fresh:
        graph = json.loads(bg.GRAPH.read_text())
        built = bg.GRAPH.stat().st_mtime
        src = bg.sources()
        fresh = graph.get("sources") == len(src) and all(p.stat().st_mtime <= built for p in src)
    if not fresh:
        print("graph out of date, rebuilding", file=sys.stderr)
        bg.build()
        graph = json.loads(bg.GRAPH.read_text())
    return graph


def resolve(target: str, nodes: dict) -> list[str]:
    t = target.strip().rstrip("/")
    m = re.fullmatch(r"(?:(tracks|debt)/)?(\d{4})(?:-.*)?(?:\.md)?", t)
    if m:
        kind = "debt" if m.group(1) == "debt" else "track"
        return [n for n in nodes if re.fullmatch(rf"{kind}:{m.group(2)}(-.*)?", n)]
    for prefix in ("page", "file", "drawio", "svg", "script", "json"):
        for cand in (f"{prefix}:{t}", f"{prefix}:{t}/"):
            if cand in nodes:
                return [cand]
    for cand in (f"anchor:{t.lower()}", f"member:{t}", f"term:{t}"):
        if cand in nodes:
            return [cand]
    low = t.lower()
    hits = [n for n in nodes if n.split(":", 1)[0] in ("term", "block", "value", "source", "member")
            and low in n.split(":", 1)[1].lower()]
    return sorted(hits)


def label(n: str, nodes: dict) -> str:
    d = nodes.get(n, {})
    extra = d.get("title") or d.get("page")
    status = d.get("status")
    out = n
    if status and status != "active":
        out += f" [{status}]"
    return f"{out}  {extra}" if extra and d["kind"] in ("track", "debt") else out


def show(nid: str, graph: dict, everything: bool) -> None:
    nodes = {d["id"]: d for d in graph["nodes"]}
    out_e, in_e = defaultdict(list), defaultdict(list)
    for e in graph["edges"]:
        out_e[e["source"]].append(e)
        in_e[e["target"]].append(e)

    def closed(n: str) -> bool:
        return nodes.get(n, {}).get("status", "").startswith(CLOSED)

    def group(title: str, items: list[str]) -> None:
        items = sorted(set(items))
        hidden = [i for i in items if closed(i)]
        if not everything:
            items = [i for i in items if not closed(i)]
        if not items and not hidden:
            return
        note = f", {len(hidden)} closed hidden" if hidden and not everything else ""
        print(f"  {title} ({len(items)}{note})")
        for i in items:
            print(f"    {label(i, nodes)}")

    print(label(nid, nodes))
    by_type = defaultdict(list)
    for e in out_e[nid]:
        if e["type"] == "defines":
            continue
        target = e["target"]
        if e["type"] == "links" and target.startswith("anchor:"):
            # Outbound links matter by the page they land on, not one by one.
            home = nodes.get(target, {}).get("page")
            target = f"page:{home}" if home else target
        by_type[f"{e['type']} ->"].append(target)
    for e in in_e[nid]:
        by_type[f"<- {e['type']}"].append(e["source"])
    # A path is also reached by what names a folder above it.
    path = nid.split(":", 1)[1]
    for n in nodes:
        if n.endswith("/") and n.split(":", 1)[0] == "file" and path.startswith(n.split(":", 1)[1]):
            for e in in_e[n]:
                by_type[f"<- {e['type']} (folder {n.split(':', 1)[1]})"].append(e["source"])
    # A block reaches the scripts that write the JSON file holding it.
    for e in in_e[nid]:
        if e["type"] == "fills":
            for w in in_e[e["source"]]:
                by_type[f"<- {w['type']} {e['source'].split('/')[-1]}"].append(w["source"])
    for key in sorted(by_type, key=lambda k: (k.startswith("<-"), k)):
        group(key, by_type[key])

    defined = [e["target"] for e in out_e[nid] if e["type"] == "defines"]
    if defined:
        linked = {a: sorted({e["source"] for e in in_e[a]
                             if e["type"] == "links" and e["source"] != nid}) for a in defined}
        outside = {a: p for a, p in linked.items() if p}
        print(f"  defines {len(defined)} identifier(s); {len(outside)} linked from other pages")
        for a, pages in sorted(outside.items()):
            print(f"    {a.split(':', 1)[1]}  <- {', '.join(p.split(':', 1)[1] for p in pages)}")


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--all"]
    if len(args) != 1:
        print(__doc__)
        return 2
    graph = load()
    nodes = {d["id"]: d for d in graph["nodes"]}
    hits = resolve(args[0], nodes)
    plain = not any(h.split(":", 1)[0] in ("page", "file", "drawio", "svg", "script",
                                           "json", "track", "debt", "anchor") for h in hits)
    if plain:
        # A name D.1 does not list, a Module or a Component, has no node of
        # its own, so the pages that spell it out are the answer.
        found = []
        for path in sorted(bg.DOCS.rglob("*.md")):
            n = path.read_text().count(args[0])
            if n:
                found.append((n, bg.rel(path)))
        if found:
            print(f"text {args[0]!r} appears in {len(found)} page(s)")
            for n, path in found:
                print(f"  {n:4d}  {path}")
            print()
    if not hits:
        if not plain or not found:
            print(f"nothing in the graph matches {args[0]!r}")
        return 0 if plain and found else 1
    if len(hits) > 12:
        print(f"{len(hits)} matches, narrow the target:")
        for h in hits[:40]:
            print(f"  {h}")
        return 1
    for h in hits:
        show(h, graph, "--all" in sys.argv)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
