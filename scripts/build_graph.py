"""Build the map of what in this repository points at what.

Every edge is read from a convention the repository already keeps, so the
graph is the same on every run and holds no guess:

  page      docs/**/*.md, with the identifiers it defines ({#id}, [](){ #id }),
            the identifiers and pages it links, the figures it embeds, the
            artifact blocks it shows (title=), the D.1 terms it uses, the
            Governance Profile members it cites (`group.member`), the DIDs it
            names, the tracks and debts it cites, and its <!-- Sumber: -->
  track     tracks/*.md, with affects:, supersedes:, and the tracks and debts
            its body cites
  debt      debt/*.md, the same
  artifact  build/artifacts/*.json, the script that writes it, the scripts
            that read it, and the blocks in docs/ it fills
  figure    images/**/*.drawio and the docs/images/**/*.svg it exports to
  working   CLAUDE.md and README.md, with the tracks and paths they name

Writes build/graph/graph.json and build/graph/findings.txt. A finding is a
place where two of those conventions disagree; nothing is fixed here. An
error is a disagreement no record explains; an info is history the trail
keeps on purpose, such as a track whose affects: names a page a later
decision moved (tracks/0440). scripts/impact.py reads the graph.

Run:  .venv/bin/python scripts/build_graph.py [--check]
Exit: 0, or 1 with --check when there is an error.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import check_terms  # noqa: E402  D.1 is parsed in one place only

DOCS = ROOT / "docs"
ARTIFACTS = ROOT / "build" / "artifacts"
OUT = ROOT / "build" / "graph"
GRAPH = OUT / "graph.json"
FINDINGS = OUT / "findings.txt"
VIEW = ROOT / "scripts" / "graph_view.html"   # template; the data goes in at /*DATA*/
HTML = OUT / "graph.html"
WORKING = ["CLAUDE.md", "README.md"]

# Numbers two tracks were given on the same day, recorded in tracks/0440. A
# citation of one reaches both files; any other shared number is an error.
KNOWN_DUPLICATES = {"track:0211", "track:0289", "track:0293", "track:0294"}

# What the trail keeps on purpose. Every other finding is an error.
INFO = {
    "active track affects a path that no longer exists",
    "page cites a superseded record",
    "working file cites a superseded record",
    "artifact block traced to no generator, by title or signature",
    "record number carried by two files, recorded in tracks/0440",
}

# A generator writes the JSON file of its own name, except these three.
WRITER = {"summary": "build", "webvh": "logs", "x509": "x509ca"}

ANCHOR = re.compile(r"\{\s*#([a-z0-9][a-z0-9-]*)")
AUTOREF = re.compile(r"\]\[([a-z0-9][a-z0-9-]*)\]")
PATHLINK = re.compile(r"(!?)\[[^\]]*\]\(([^)\s]+)\)")
TITLE = re.compile(r'title="([^"]+)"')
CITE = re.compile(r"\b(tracks|debt)/(\d{4})")
SUMBER = re.compile(r"<!--\s*Sumber:\s*(.*?)\s*-->", re.S)
DID = re.compile(r"did:(?:webvh|key):[A-Za-z0-9.:%_-]+")
MEMBER = re.compile(r"`([a-z_]+)\.([a-z0-9_-]+)[a-z0-9_.-]*`")
FENCE = re.compile(r"(?s)```.*?```")
PATHSPAN = re.compile(r"`((?:docs|scripts|tracks|debt|images|source-data|build)/[^`\s]*)`")


def sources() -> list[pathlib.Path]:
    """Every file the graph is read from, for scripts/impact.py to test age."""
    out = list(DOCS.rglob("*.md")) + list((ROOT / "tracks").glob("*.md"))
    out += list((ROOT / "debt").glob("*.md")) + list(ARTIFACTS.glob("*.json"))
    out += list((ROOT / "images").rglob("*.drawio"))
    out += list((DOCS / "images").rglob("*.svg"))
    out += list((ROOT / "scripts" / "artifacts").glob("*.py"))
    out += [ROOT / w for w in WORKING] + [check_terms.GLOSSARY, VIEW]
    return [p for p in out if p.exists()]


def rel(p: pathlib.Path) -> str:
    return p.resolve().relative_to(ROOT).as_posix()


def blank_fences(text: str) -> str:
    return FENCE.sub(lambda m: re.sub(r"[^\n]", " ", m.group()), text)


def frontmatter(text: str) -> dict:
    """The small YAML subset tracks/ and debt/ use: scalars and one list."""
    m = re.match(r"(?s)\A---\n(.*?)\n---\n", text)
    data: dict = {}
    key = None
    for line in (m.group(1) if m else "").splitlines():
        item = re.match(r"\s+-\s+(.*)", line)
        if item and key:
            data.setdefault(key, []).append(item.group(1).split(" #")[0].strip())
            continue
        kv = re.match(r"([a-z_]+):\s*(.*)", line)
        if kv:
            key, value = kv.group(1), kv.group(2).split("#")[0].strip()
            data[key] = value if value else []
    return data


class Graph:
    def __init__(self) -> None:
        self.nodes: dict[str, dict] = {}
        self.edges: set[tuple[str, str, str]] = set()
        self.findings: dict[str, list[str]] = defaultdict(list)

    def node(self, nid: str, **attrs) -> str:
        self.nodes.setdefault(nid, {"id": nid, "kind": nid.split(":", 1)[0]})
        self.nodes[nid].update({k: v for k, v in attrs.items() if v is not None})
        return nid

    def edge(self, src: str, kind: str, dst: str) -> None:
        self.edges.add((src, kind, dst))

    def file_node(self, path: str) -> str:
        """The node for a repository path, by what kind of file it is."""
        path = path.rstrip("/") + ("/" if (ROOT / path).is_dir() else "")
        if path.startswith("docs/") and path.endswith(".md"):
            return self.node(f"page:{path}")
        if path.endswith(".drawio"):
            return self.node(f"drawio:{path}")
        if path.endswith(".svg"):
            return self.node(f"svg:{path}")
        return self.node(f"file:{path}")

    def record(self, kind: str, text: str) -> None:
        self.findings[kind].append(text)


def record_ids() -> dict[str, list[str]]:
    """`track:0289` to the node of every file carrying that number.

    A number is meant to name one file. Where two files share it, each gets
    the node `track:<file stem>` and a citation by number reaches both.
    """
    ids: dict[str, list[str]] = {}
    for folder, kind in (("tracks", "track"), ("debt", "debt")):
        by_num = defaultdict(list)
        for path in sorted((ROOT / folder).glob("*.md")):
            by_num[path.name[:4]].append(path)
        for num, paths in by_num.items():
            ids[f"{kind}:{num}"] = ([f"{kind}:{num}"] if len(paths) == 1
                                    else [f"{kind}:{p.stem}" for p in paths])
    return ids


RECORDS: dict[str, list[str]] = {}


def records(folder: str, num: str) -> list[str]:
    key = f"{'track' if folder == 'tracks' else 'debt'}:{num}"
    return RECORDS.get(key, [key])


def resolve_record(ref: str) -> list[str]:
    """`debt/0086` or `tracks/0013-slug.md` to its node ids."""
    m = re.match(r"(tracks|debt)/(\d{4})", ref)
    return records(m.group(1), m.group(2)) if m else []


def read_records(g: Graph) -> None:
    for folder, kind in (("tracks", "track"), ("debt", "debt")):
        for path in sorted((ROOT / folder).glob("*.md")):
            text = path.read_text()
            fm = frontmatter(text)
            num = path.name[:4]
            ids = records(folder, num)
            if len(ids) > 1:
                g.record("record number carried by two files, recorded in tracks/0440"
                         if f"{kind}:{num}" in KNOWN_DUPLICATES
                         else "record number carried by two files", rel(path))
            nid = g.node(ids[0] if len(ids) == 1 else f"{kind}:{path.stem}", path=rel(path), title=fm.get("title"),
                         status=fm.get("status") or "?")
            sup = fm.get("supersedes")
            # `0001 (items 1 and 2 only)` replaces part of 0001, which stays active.
            sup = sup if isinstance(sup, str) else ", ".join(sup or [])
            for s, part in re.findall(r"(\d{4})\s*(\([^)]*\))?", sup):
                for t in records("tracks", s):
                    g.edge(nid, "supersedes-in-part" if part else "supersedes", g.node(t))
            for ref in fm.get("affects") or []:
                ref = re.sub(r"\s*\(.*\)$", "", ref)
                found = resolve_record(ref)
                if found:
                    for r in found:
                        g.edge(nid, "affects", g.node(r))
                elif (ROOT / ref).exists():
                    g.edge(nid, "affects", g.file_node(ref))
                elif g.nodes[nid]["status"] == "open":
                    g.record("open debt affects a path that does not exist",
                             f"{rel(path)}: {ref}")
                elif g.nodes[nid]["status"] == "active":
                    g.record("active track affects a path that no longer exists",
                             f"{rel(path)}: {ref}")
            body = text.split("\n---\n", 1)[-1]
            for folder_ref, n in set(CITE.findall(body)):
                for target in records(folder_ref, n):
                    if target != nid:
                        g.edge(nid, "cites", g.node(target))


def read_artifacts(g: Graph, titles: set[str]) -> None:
    scripts = {p.stem: p for p in (ROOT / "scripts" / "artifacts").glob("*.py")}
    texts = {stem: p.read_text() for stem, p in scripts.items()}
    for path in sorted(ARTIFACTS.glob("*.json")):
        jid = g.node(f"json:{rel(path)}")
        writer = WRITER.get(path.stem, path.stem)
        for stem, text in texts.items():
            if f'"{path.name}"' not in text:
                continue
            sid = g.node(f"script:{rel(scripts[stem])}")
            g.edge(sid, "writes" if stem == writer else "reads", jid)

        def walk(x, depth: int = 0) -> None:
            if isinstance(x, dict) and depth < 6:
                for k, v in x.items():
                    if k in titles:
                        g.edge(jid, "fills", f"block:{k}")
                    walk(v, depth + 1)
        walk(json.loads(path.read_text()))
        # A block whose title the JSON file does not carry is still its
        # output when the file holds the block's signature.
        raw = path.read_text()
        for t, tokens in BODIES.items():
            if any(tok in raw for tok in tokens):
                g.edge(jid, "fills", f"block:{t}")

    # A block no JSON file holds may still be written or checked by a script
    # that names its title: inject.py for the computed ones, verify_artifacts.py
    # for every block whose signature it checks.
    named = dict(texts)
    named["verify_artifacts"] = (ROOT / "scripts" / "verify_artifacts.py").read_text()
    for t in titles:
        for stem, text in named.items():
            if t in text:
                path = ROOT / "scripts" / ("" if stem == "verify_artifacts" else "artifacts") / f"{stem}.py"
                kind = "verifies" if stem == "verify_artifacts" else "names-block"
                g.edge(g.node(f"script:{rel(path)}"), kind, f"block:{t}")


BLOCK = re.compile(r'``` \{[^}\n]*title="([^"]+)"[^}\n]*\}\n(.*?)\n```', re.S)
# Only a signature is unique to one signing run; a DID or a key repeats
# across every artifact that names it, so it would trace a block to the wrong file.
SIGNATURE = re.compile(r'"proofValue":\s*"([^"]+)"|eyJ[\w-]+\.[\w-]*\.([\w-]{40,})|"signature":\s*"([^"]{40,})"')
BODIES: dict[str, set[str]] = defaultdict(set)


def read_pages(g: Graph, terms: list[dict], members: set[str]) -> set[str]:
    titles: set[str] = set()
    term_res = [(t, re.compile(rf"(?<![\w-]){re.escape(t['canonical'])}(?![\w-])", re.I))
                for t in terms]
    for path in sorted(DOCS.rglob("*.md")):
        text = path.read_text()
        pid = g.file_node(rel(path))
        title = re.search(r"(?m)^title:\s*(.+)$", text)
        g.node(pid, title=title.group(1).strip().strip("\"'") if title else None)
        for t in TITLE.findall(text):
            titles.add(t)
            g.edge(pid, "shows", g.node(f"block:{t}"))
        for t, body in BLOCK.findall(text):
            BODIES[t] |= {x for m in SIGNATURE.findall(body) for x in m if x}
        for did in {d.split("#")[0].rstrip(".:") for d in DID.findall(text)}:
            g.edge(pid, "names", g.node(f"value:{did}"))
        for s in SUMBER.findall(text):
            g.edge(pid, "from-source", g.node(f"source:{' '.join(s.split())}"))
        for folder_ref, n in set(CITE.findall(text)):
            for target in records(folder_ref, n):
                g.edge(pid, "cites", g.node(target))

        prose = blank_fences(text)
        for a in ANCHOR.findall(prose):
            aid = f"anchor:{a}"
            if aid in g.nodes and g.nodes[aid].get("page") not in (None, rel(path)):
                g.record("identifier declared on two pages", f"{a}: {g.nodes[aid]['page']}, {rel(path)}")
            g.edge(pid, "defines", g.node(aid, page=rel(path)))
        for a in set(AUTOREF.findall(prose)):
            g.edge(pid, "links", g.node(f"anchor:{a}"))
        for bang, target in PATHLINK.findall(prose):
            if target.startswith(("http", "mailto:", "#")):
                continue
            file_part, _, frag = target.partition("#")
            if not file_part:
                continue
            dest = (path.parent / file_part).resolve()
            if not dest.is_relative_to(ROOT):
                continue
            dst = g.file_node(rel(dest))
            g.edge(pid, "embeds" if bang else "links", dst)
            if frag:
                g.edge(pid, "links", g.node(f"anchor:{frag}"))
        for group, member in set(MEMBER.findall(prose)):
            if group in {m.split(".")[0] for m in members}:
                mid = f"member:{group}.{member}"
                g.edge(pid, "cites-member", g.node(mid))
                if f"{group}.{member}" not in members:
                    g.record("Governance Profile member cited but not in the payload",
                             f"{rel(path)}: {group}.{member}")
        masked = check_terms.mask(text)
        for t, rx in term_res:
            if rx.search(masked):
                g.edge(pid, "uses-term", g.node(f"term:{t['canonical']}", klass=t["class"]))
    return titles


def gp_members() -> set[str]:
    path = ARTIFACTS / "governance.json"
    if not path.exists():
        return set()
    payload = json.loads(path.read_text())["_structured"]["payload"]
    return {f"{k}.{m}" for k, v in payload.items() if isinstance(v, dict) for m in v}


def read_members(g: Graph, members: set[str]) -> None:
    jid = g.node("json:build/artifacts/governance.json")
    for m in sorted(members):
        g.edge(jid, "holds", g.node(f"member:{m}"))


def read_figures(g: Graph) -> None:
    for src in sorted((ROOT / "images").rglob("*.drawio")):
        svg = DOCS / "images" / src.relative_to(ROOT / "images").with_suffix(".svg")
        if svg.exists():
            g.edge(g.file_node(rel(src)), "exports", g.file_node(rel(svg)))
        else:
            g.record("figure source with no export", rel(src))
    for svg in sorted((DOCS / "images").rglob("*.svg")):
        src = ROOT / "images" / svg.relative_to(DOCS / "images").with_suffix(".drawio")
        if not src.exists():
            g.record("figure export with no .drawio source", rel(svg))


def read_working(g: Graph) -> None:
    for name in WORKING:
        path = ROOT / name
        if not path.exists():
            continue
        fid = g.node(f"file:{name}")
        text = path.read_text()
        for folder_ref, n in set(CITE.findall(text)):
            for target in records(folder_ref, n):
                g.edge(fid, "cites", g.node(target))
        for p in sorted(set(PATHSPAN.findall(text))):
            if any(c in p for c in "<*{") or "NNNN" in p or re.fullmatch(r"(tracks|debt)/\d{4}", p):
                continue
            if not (ROOT / p).exists():
                g.record("working file names a path that does not exist", f"{name}: {p}")


def check(g: Graph) -> None:
    """The disagreements that need the whole graph to see."""
    status = {n: d.get("status", "?") for n, d in g.nodes.items() if d["kind"] in ("track", "debt")}
    succeeded = defaultdict(list)
    for src, kind, dst in g.edges:
        if kind.startswith("supersedes"):
            succeeded[dst].append((src, kind))
    for n, s in sorted(status.items()):
        if "path" not in g.nodes[n]:
            g.record("cited record that does not exist", n)
            continue
        if n.startswith("track:") and s.startswith("superseded") and not succeeded[n]:
            g.record("superseded track no track names in supersedes:", n)
    for dst, srcs in sorted(succeeded.items()):
        whole = sorted(src for src, kind in srcs if kind == "supersedes")
        if whole and status.get(dst, "?").startswith("active"):
            g.record("track superseded whole by another but still active",
                     f"{dst} (superseded by {', '.join(whole)})")
    for src, kind, dst in sorted(g.edges):
        if kind != "cites" or src.split(":")[0] not in ("page", "file"):
            continue
        s = status.get(dst, "?")
        if s.startswith(("superseded", "withdrawn")):
            g.record(f"{'page' if src.startswith('page:') else 'working file'} cites a {s} record",
                     f"{src.split(':', 1)[1]}: {dst}")
    linked = {dst for _, kind, dst in g.edges if kind == "links"}
    for n, d in g.nodes.items():
        if d["kind"] == "anchor" and n in linked and "page" not in d:
            g.record("identifier linked but defined nowhere", n)
        if (d["kind"] == "svg" and n.startswith("svg:docs/images/")
                and not any(e[2] == n and e[1] in ("embeds", "links") for e in g.edges)):
            g.record("figure export no page embeds", n)
    shown = {dst for _, kind, dst in g.edges if kind in ("fills", "names-block", "verifies")}
    for n, d in sorted(g.nodes.items()):
        if d["kind"] == "block" and n not in shown:
            g.record("artifact block traced to no generator, by title or signature", n.split(":", 1)[1])


def focus_of(g: Graph, item: str) -> str | None:
    """The node a finding is about, so the view can open it from the list."""
    head = item.split(" ", 1)[0].split(": ", 1)[0].rstrip(":")
    if head in g.nodes:
        return head
    for n, d in g.nodes.items():
        if d.get("path") == head:
            return n
    for prefix in ("page", "file"):
        if f"{prefix}:{head}" in g.nodes:
            return f"{prefix}:{head}"
    return f"block:{item}" if f"block:{item}" in g.nodes else None


def write_view(g: Graph) -> None:
    data = {
        "nodes": sorted(g.nodes.values(), key=lambda d: d["id"]),
        "edges": [{"source": s, "type": k, "target": t} for s, k, t in sorted(g.edges)],
        "findings": [
            {"level": "info" if kind in INFO else "error", "kind": kind,
             "items": [{"text": i, "focus": focus_of(g, i)} for i in sorted(set(g.findings[kind]))]}
            for kind in sorted(g.findings, key=lambda k: (k in INFO, k))],
    }
    # `</` inside a string would close the script element early.
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    HTML.write_text(VIEW.read_text().replace("/*DATA*/null", blob))


def build() -> Graph:
    RECORDS.update(record_ids())
    g = Graph()
    terms = check_terms.load_terms()
    read_records(g)
    titles = read_pages(g, terms, gp_members())
    read_artifacts(g, titles)
    read_members(g, gp_members())
    read_figures(g)
    read_working(g)
    check(g)
    OUT.mkdir(parents=True, exist_ok=True)
    GRAPH.write_text(json.dumps({
        "sources": len(sources()),
        "nodes": sorted(g.nodes.values(), key=lambda d: d["id"]),
        "edges": [{"source": s, "type": k, "target": t} for s, k, t in sorted(g.edges)],
    }, ensure_ascii=False, indent=1) + "\n")
    write_view(g)
    lines = []
    for kind in sorted(g.findings, key=lambda k: (k in INFO, k)):
        items = sorted(set(g.findings[kind]))
        lines += [f"## {'info' if kind in INFO else 'error'}: {kind} ({len(items)})", *items, ""]
    FINDINGS.write_text("\n".join(lines))
    return g


if __name__ == "__main__":
    g = build()
    kinds = defaultdict(int)
    for d in g.nodes.values():
        kinds[d["kind"]] += 1
    print(f"{len(g.nodes)} nodes, {len(g.edges)} edges -> {rel(GRAPH)}")
    print("  " + ", ".join(f"{k} {v}" for k, v in sorted(kinds.items())))
    errors = sum(len(set(v)) for k, v in g.findings.items() if k not in INFO)
    infos = sum(len(set(v)) for k, v in g.findings.items() if k in INFO)
    print(f"{errors} error(s), {infos} info -> {rel(FINDINGS)}")
    for kind in sorted(g.findings, key=lambda k: (k in INFO, k)):
        print(f"  {'info ' if kind in INFO else 'ERROR'} {len(set(g.findings[kind])):4d}  {kind}")
    sys.exit(1 if errors and "--check" in sys.argv else 0)
