"""Export every .drawio under images/ to its .svg under docs/images/.

The .drawio file is the source of truth; the .svg is only its export. The two
trees keep identical per-document subfolders, so a source at
`images/<document>/<chapter>/<slug>.drawio` exports to
`docs/images/<document>/<chapter>/<slug>.svg`.

Two shapes of source exist, and the difference is whether the author drew the
white card into the diagram:

  * the card is in the file — a full-page rounded white rectangle at the
    origin. It is exported as it stands, with no border added.
  * the card is not in the file. The export gets a PAD-wide border and the card
    is drawn into the .svg afterwards, which is what CLAUDE.md section 9 asks
    for: the space belongs to the .svg, never to CSS.

The canvas outside the card is transparent (`-t`). Without it draw.io paints an
opaque white square behind the whole export, and the rounded corners of the card
sit on white rather than on the page.

Fonts are not embedded — that multiplies a 30 kB export by twenty — so every
font-family in the export is rewritten to the stack the pages already use.

Run:  .venv/bin/python scripts/export_diagrams.py [slug ...]
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIO_ROOT = ROOT / "images"
SVG_ROOT = ROOT / "docs" / "images"

DRAWIO = "drawio"
PAD = 36
CARD_STROKE = "#e2e9f0"
CARD_RADIUS = 12
FONT = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"


def has_card(path: pathlib.Path) -> bool:
    """True when the diagram already draws its own full-page white card."""
    model = ET.parse(path).getroot().find(".//mxGraphModel")
    if model is None:
        return False
    pw, ph = float(model.get("pageWidth") or 0), float(model.get("pageHeight") or 0)
    for cell in model.iter("mxCell"):
        geom = cell.find("mxGeometry")
        if geom is None:
            continue
        style = (cell.get("style") or "").lower()
        if "rounded=1" not in style or "fillcolor=#ffffff" not in style:
            continue
        x, y = float(geom.get("x") or 0), float(geom.get("y") or 0)
        w, h = float(geom.get("width") or 0), float(geom.get("height") or 0)
        if x <= 2 and y <= 2 and w >= pw - 4 and h >= ph - 4:
            return True
    return False


def export(src: pathlib.Path, dst: pathlib.Path, border: int) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [DRAWIO, "-x", "-f", "svg", "--embed-svg-fonts", "false",
         "--theme", "light", "-t", "-b", str(border), "-o", str(dst), str(src)],
        check=True, capture_output=True, text=True,
    )


def retype_fonts(svg: str) -> str:
    def swap(m: re.Match) -> str:
        value = m.group(2)
        if "mono" in value.lower() or "courier" in value.lower():
            return m.group(0)
        return f"{m.group(1)}{FONT}{m.group(3)}"

    svg = re.sub(r'(font-family=")([^"]+)(")', swap, svg)
    return re.sub(r'(font-family:\s*)([^;"]+)()', swap, svg)


def add_card(svg: str) -> str:
    size = re.search(r'<svg[^>]*\swidth="([\d.]+)px?"[^>]*\sheight="([\d.]+)px?"', svg)
    if size is None:
        raise SystemExit("export carries no width/height — cannot place the card")
    w, h = float(size.group(1)), float(size.group(2))
    card = (
        f'<rect x="0.5" y="0.5" width="{w - 1:g}" height="{h - 1:g}" '
        f'rx="{CARD_RADIUS}" fill="#ffffff" stroke="{CARD_STROKE}"/>'
    )
    opening = re.search(r"<svg[^>]*>", svg).end()
    defs = re.compile(r"<defs\b.*?(?:</defs>|/>)", re.S).match(svg, opening)
    at = defs.end() if defs else opening
    return svg[:at] + card + svg[at:]


def main(only: list[str]) -> None:
    sources = sorted(DIO_ROOT.rglob("*.drawio"))
    if only:
        sources = [s for s in sources if s.stem in only]
        if not sources:
            raise SystemExit(f"no .drawio matches {only}")
    for src in sources:
        rel = src.relative_to(DIO_ROOT).with_suffix(".svg")
        dst = SVG_ROOT / rel
        card = has_card(src)
        export(src, dst, 0 if card else PAD)
        svg = retype_fonts(dst.read_text())
        if not card:
            svg = add_card(svg)
        dst.write_text(svg)
        size = re.search(r'width="([\d.]+)px?"\s+height="([\d.]+)px?"', svg)
        print(f"{'own card' if card else 'card added':11}  "
              f"{size.group(1)}x{size.group(2)}  {rel}")


if __name__ == "__main__":
    main(sys.argv[1:])
