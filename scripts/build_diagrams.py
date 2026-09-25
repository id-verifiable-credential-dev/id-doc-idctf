"""Generate the paired .drawio source and .svg export for one diagram set.

`images/<document>/<chapter>/<slug>.drawio` is the source of truth and
`docs/images/<document>/<chapter>/<slug>.svg` is what the pages link to. Both
are written from the same spec here so the two trees cannot drift apart.

PAD is the space drawn inside the .svg itself, not in CSS: the canvas is the
content box grown by PAD on every side, and the content is shifted into it, so
the white card and what sits on it always agree. See CLAUDE.md section 9.

Run:  .venv/bin/python scripts/build_diagrams.py
"""

from __future__ import annotations

import html
import pathlib

PAD = 36

FONT = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
INK = "#16242f"
MUTED = "#4a5f6f"
BAND = "#b8c4ce"
LINE = "#5c7180"
CARD_STROKE = "#e2e9f0"

# One color per Service, held constant across every figure on the page, so a
# reader who learns the mapping once carries it through the whole chapter.
PALETTE = {
    "issuer": ("#fff3cd", "#d4a017"),
    "wallet": ("#e2d9f3", "#7d5ba6"),
    "verifier": ("#cfe2ff", "#2f6fd0"),
    "trust": ("#d4edda", "#3c8d5a"),
    "library": ("#f8d7da", "#c0392b"),
    "off": ("#e9ecef", "#6c757d"),
}

BOX_W, BOX_H, GAP = 186, 54, 12
GUTTER = 104          # left gutter inside a module band, for the layer name
BAND_PAD = 14
BAND_LABEL = 30
PER_ROW = 4           # components per row before wrapping within one layer


def wrap(text: str, limit: int = 26) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if len(trial) > limit and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


class Canvas:
    def __init__(self, title: str, desc: str):
        self.title, self.desc = title, desc
        self.svg: list[str] = []
        self.cells: list[str] = []
        self.w = self.h = 0
        self._n = 0

    def _id(self, p: str) -> str:
        self._n += 1
        return f"{p}{self._n}"

    def extend(self, x: float, y: float) -> None:
        self.w, self.h = max(self.w, x), max(self.h, y)

    # -- primitives ----------------------------------------------------------

    def band(self, x, y, w, h, label):
        self.svg.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="none" '
            f'stroke="{BAND}" stroke-width="1.2" stroke-dasharray="5 4"/>'
        )
        self.svg.append(
            f'<text x="{x + 14}" y="{y + 21}" font-family="{FONT}" font-size="11.5" '
            f'font-weight="600" letter-spacing="0.4" fill="{MUTED}">{html.escape(label)}</text>'
        )
        self.cells.append(
            f'<mxCell id="{self._id("band")}" value="{html.escape(label)}" '
            'style="rounded=1;arcSize=6;fillColor=none;strokeColor=#b8c4ce;dashed=1;'
            'dashPattern=5 4;verticalAlign=top;align=left;spacingLeft=12;spacingTop=6;'
            'fontSize=11;fontStyle=1;fontColor=#4a5f6f;html=1;" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>'
        )
        self.extend(x + w, y + h)

    def box(self, x, y, w, h, title, subs=(), kind="issuer", bold=True):
        fill, stroke = PALETTE[kind]
        self.svg.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="1.3"/>'
        )
        head = wrap(title, int(w / 6.4))
        lines = [(t, 11.5, "600", INK) for t in head] + [(s, 10, "400", MUTED) for s in subs]
        total = len(lines) * 13.4
        cy = y + (h - total) / 2 + 10
        for text, size, weight, fill_c in lines:
            self.svg.append(
                f'<text x="{x + w / 2:.1f}" y="{cy:.1f}" text-anchor="middle" '
                f'font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
                f'fill="{fill_c}">{html.escape(text)}</text>'
            )
            cy += 13.4
        label = html.escape(title + ("\n" + "\n".join(subs) if subs else ""))
        self.cells.append(
            f'<mxCell id="{self._id("n")}" value="{label}" '
            f'style="rounded=1;arcSize=8;fillColor={fill};strokeColor={stroke};'
            f'fontSize=12;fontColor={INK};html=1;whiteSpace=wrap;verticalAlign=middle;" '
            f'vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>'
        )
        self.extend(x + w, y + h)

    def gutter_label(self, x, y, h, text):
        self.svg.append(
            f'<text x="{x}" y="{y + h / 2 + 4:.1f}" font-family="{FONT}" font-size="11" '
            f'font-weight="600" fill="{MUTED}">{html.escape(text)}</text>'
        )

    def text(self, x, y, s, size=11, weight="400", fill=MUTED, anchor="start"):
        self.svg.append(
            f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{fill}">{html.escape(s)}</text>'
        )
        align = {"start": "left", "middle": "center", "end": "right"}[anchor]
        ox = {"start": 0, "middle": -110, "end": -220}[anchor]
        self.cells.append(
            f'<mxCell id="{self._id("t")}" value="{html.escape(s)}" '
            f'style="text;html=1;strokeColor=none;fillColor=none;align={align};'
            f'verticalAlign=middle;fontSize={size};fontColor={fill};'
            f'fontStyle={1 if weight == "600" else 0};" vertex="1" parent="1">'
            f'<mxGeometry x="{x + ox}" y="{y - 10}" width="220" height="20" as="geometry"/></mxCell>'
        )
        self.extend(x, y)

    def edge(self, points, label=None, dashed=False, arrow=True):
        pts = " ".join(f"{px},{py}" for px, py in points)
        dash = ' stroke-dasharray="6 4"' if dashed else ""
        mark = ' marker-end="url(#arrow)"' if arrow else ""
        self.svg.append(
            f'<polyline points="{pts}" fill="none" stroke="{LINE}" stroke-width="1.5" '
            f'stroke-linejoin="round"{dash}{mark}/>'
        )
        if label:
            mx, my = points[len(points) // 2]
            w = len(label) * 5.6 + 12
            self.svg.append(
                f'<rect x="{mx - w / 2:.1f}" y="{my - 9:.1f}" width="{w:.1f}" height="18" '
                'rx="3" fill="#ffffff" fill-opacity="0.94"/>'
            )
            self.svg.append(
                f'<text x="{mx:.1f}" y="{my + 4:.1f}" text-anchor="middle" '
                f'font-family="{FONT}" font-size="10.5" fill="{MUTED}">{html.escape(label)}</text>'
            )
        for px, py in points:
            self.extend(px, py)

    def cell(self, x, y, w, h, glyph, fill, stroke, tone=INK):
        self.svg.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="1"/>'
        )
        if glyph:
            self.svg.append(
                f'<text x="{x + w / 2:.1f}" y="{y + h / 2 + 4.5:.1f}" text-anchor="middle" '
                f'font-family="{FONT}" font-size="12.5" font-weight="600" '
                f'fill="{tone}">{html.escape(glyph)}</text>'
            )
        self.cells.append(
            f'<mxCell id="{self._id("c")}" value="{html.escape(glyph)}" '
            f'style="rounded=1;arcSize=20;fillColor={fill};strokeColor={stroke};'
            f'fontSize=12;fontStyle=1;fontColor={tone};html=1;" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>'
        )
        self.extend(x + w, y + h)

    # -- emit ----------------------------------------------------------------

    def render(self, stem: str, chapter: str = "high-level-architecture") -> tuple[int, int]:
        w, h = int(self.w + PAD * 2), int(self.h + PAD * 2)
        body = "\n".join(self.svg)
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" role="img" aria-labelledby="t d">\n'
            f'<title id="t">{html.escape(self.title)}</title>'
            f'<desc id="d">{html.escape(self.desc)}</desc>\n'
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            'markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,1 L9,5 L0,9 z" fill="{LINE}"/></marker></defs>\n'
            f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="12" '
            f'fill="#ffffff" stroke="{CARD_STROKE}"/>\n'
            f'<g transform="translate({PAD},{PAD})">\n{body}\n</g>\n</svg>\n'
        )
        drawio = (
            '<mxfile host="app.diagrams.net" type="device">\n'
            f'  <diagram name="{html.escape(self.title)}">\n'
            f'    <mxGraphModel dx="{w}" dy="{h}" grid="1" gridSize="10" page="1" '
            f'pageWidth="{w}" pageHeight="{h}" math="0" shadow="0">\n'
            "      <root>\n        <mxCell id=\"0\"/>\n        <mxCell id=\"1\" parent=\"0\"/>\n"
            + "\n".join("        " + c for c in self.cells)
            + "\n      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n"
        )
        svg_path = SVG_ROOT / chapter / f"{stem}.svg"
        dio_path = DIO_ROOT / chapter / f"{stem}.drawio"
        svg_path.parent.mkdir(parents=True, exist_ok=True)
        dio_path.parent.mkdir(parents=True, exist_ok=True)
        svg_path.write_text(svg)
        dio_path.write_text(drawio)
        return w, h


def module_band(c: Canvas, x, y, width, module, kind, layers) -> float:
    """One Module as a band, one row per layer, wrapping past PER_ROW boxes."""
    rows = []
    for layer, comps in layers:
        for i in range(0, len(comps), PER_ROW):
            rows.append((layer if i == 0 else "", comps[i:i + PER_ROW]))
    height = BAND_LABEL + len(rows) * (BOX_H + GAP) + BAND_PAD
    c.band(x, y, width, height, module)
    cy = y + BAND_LABEL
    for layer, comps in rows:
        if layer:
            c.gutter_label(x + BAND_PAD, cy, BOX_H, layer)
        cx = x + GUTTER
        for comp in comps:
            name, sub = (comp if isinstance(comp, tuple) else (comp, None))
            c.box(cx, cy, BOX_W, BOX_H, name, (sub,) if sub else (), kind)
            cx += BOX_W + GAP
        cy += BOX_H + GAP
    return y + height


ROOT = pathlib.Path(__file__).resolve().parent.parent

# Each figure is written into the chapter that publishes it, in both trees at
# once (CLAUDE.md section 9). The component figures belong to Software
# Architecture; the Module map and the call matrix belong to High-Level
# Architecture.
DIO_ROOT = ROOT / "images/architecture-framework"
SVG_ROOT = ROOT / "docs/images/architecture-framework"


# ---------------------------------------------------------------- figure 4.1

def fig_module_map():
    c = Canvas(
        "The eleven Modules, grouped by Service",
        "Four Service columns. Issuer Services holds Issuer Core and Issuer Console, "
        "both run many times. Wallet Services holds one Mobile Wallet with millions "
        "of installations and a single Wallet Backend Service. Verifier Services holds "
        "Verifier Core, Verifier Console and Mobile Verifier. Trust Infrastructure "
        "holds Trust Authority, Trust Registry, DID Service and KMS, one of each.")
    cols = [
        ("ISSUER SERVICES", "issuer", [("Issuer Core", "many"), ("Issuer Console", "many")]),
        ("WALLET SERVICES", "wallet", [("Mobile Wallet", "one app, millions installed"),
                                       ("Wallet Backend Service", "one")]),
        ("VERIFIER SERVICES", "verifier", [("Verifier Core", "many"), ("Verifier Console", "many"),
                                           ("Mobile Verifier", "millions installed")]),
        ("TRUST INFRASTRUCTURE", "trust", [("Trust Authority", "one"), ("Trust Registry", "one"),
                                           ("DID Service", "one"), ("KMS", "one")]),
    ]
    bw, bx = 248, 0
    tallest = max(len(m) for _, _, m in cols)
    bh = BAND_LABEL + tallest * (66 + GAP) + BAND_PAD
    for label, kind, mods in cols:
        c.band(bx, 0, bw, bh, label)
        cy = BAND_LABEL
        for name, sub in mods:
            c.box(bx + BAND_PAD, cy, bw - BAND_PAD * 2, 66, name, (sub,), kind)
            cy += 66 + GAP
        bx += bw + 16
    c.text(0, bh + 26, "Color marks the Service. Every later figure on this page keeps the same mapping.", 10.5)
    return c.render("module-map")


# ---------------------------------------------------------------- figure 4.2

def fig_call_matrix():
    c = Canvas(
        "Which Module may call which",
        "A matrix of caller against callee for all eleven Modules plus a database column. "
        "Filled cells mark a permitted call, hollow cells a read from cache or a static file, "
        "crossed cells a prohibited call, and the barred cells the four prohibitions the "
        "pipeline tests on every build. The last four rows are empty of permitted calls "
        "outside Trust Infrastructure, which is how the figure shows that Trust "
        "Infrastructure never calls outward.")
    mods = ["IC", "ICn", "WA", "WBS", "VC", "VCn", "VA", "TA", "TR", "DID", "KMS", "DB"]
    rows = [
        ("Issuer Core", {"WBS": "X", "VC": "x", "TA": "x", "TR": "@", "DID": "@", "KMS": "o", "DB": "@"}),
        ("Issuer Console", {"IC": "@", "WBS": "x", "VC": "x", "TA": "x", "TR": "x", "DID": "x", "KMS": "x", "DB": "X"}),
        ("Mobile Wallet", {"IC": "@", "WBS": "@", "VC": "@", "VA": "@", "TA": "x", "TR": "c", "DID": "c", "KMS": "x"}),
        ("Wallet Backend Service", {"IC": "x", "VC": "x", "TA": "x", "TR": "@", "DID": "@", "KMS": "x", "DB": "@"}),
        ("Verifier Core", {"IC": "X", "WBS": "x", "TA": "x", "TR": "@", "DID": "@", "KMS": "o", "DB": "@"}),
        ("Verifier Console", {"IC": "x", "VC": "@", "WBS": "x", "TA": "x", "TR": "x", "DID": "x", "KMS": "x", "DB": "X"}),
        ("Mobile Verifier", {"IC": "x", "VC": "@", "TA": "x", "TR": "c", "KMS": "x"}),
        ("Trust Authority", {"IC": "X", "ICn": "X", "WA": "X", "WBS": "X", "VC": "X", "VCn": "X", "VA": "X",
                             "TR": "@", "DID": "@", "KMS": "@", "DB": "@"}),
        ("Trust Registry", {"IC": "X", "ICn": "X", "WA": "X", "WBS": "X", "VC": "X", "VCn": "X", "VA": "X", "DB": "@"}),
        ("DID Service", {"IC": "X", "ICn": "X", "WA": "X", "WBS": "X", "VC": "X", "VCn": "X", "VA": "X", "DB": "@"}),
        ("KMS", {"IC": "X", "ICn": "X", "WA": "X", "WBS": "X", "VC": "X", "VCn": "X", "VA": "X", "DB": "@"}),
    ]
    style = {
        "@": ("●", "#d4edda", "#3c8d5a", "#1e5b38"),
        "c": ("○", "#eef4fb", "#8fb4d9", "#2f6fd0"),
        "o": ("◐", "#fff8e6", "#d4a017", "#8a6400"),
        "x": ("×", "#f4f6f8", "#cbd5dd", "#8894a0"),
        "X": ("✕", "#f8d7da", "#c0392b", "#a32519"),
    }
    lw, cw, ch, top = 196, 60, 34, 56
    for i, m in enumerate(mods):
        x = lw + i * cw
        c.text(x + cw / 2, top - 12, m, 10.5, "600", MUTED, "middle")
    for r, (name, cells) in enumerate(rows):
        y = top + r * ch
        c.text(lw - 10, y + ch / 2 + 4, name, 11, "600", INK, "end")
        for i, m in enumerate(mods):
            g = cells.get(m)
            x = lw + i * cw
            if g is None:
                c.cell(x + 2, y + 2, cw - 4, ch - 4, "", "#fbfcfd", "#eef1f4")
            else:
                glyph, fill, stroke, tone = style[g]
                c.cell(x + 2, y + 2, cw - 4, ch - 4, glyph, fill, stroke, tone)
    c.svg.append(
        f'<line x1="{lw}" y1="{top + 7 * ch}" x2="{lw + len(mods) * cw}" y2="{top + 7 * ch}" '
        f'stroke="{BAND}" stroke-width="1.4" stroke-dasharray="5 4"/>')
    c.text(lw + len(mods) * cw + 8, top + 7 * ch + 4, "", 10)
    ly = top + len(rows) * ch + 34
    legend = [("@", "may call"), ("c", "may read, from cache or a static file"),
              ("o", "may call, never during a transaction"), ("x", "must not call"),
              ("X", "must not call, and the pipeline fails the build")]
    for i, (key, desc) in enumerate(legend):
        gy = ly + i * 24
        glyph, fill, stroke, tone = style[key]
        c.cell(0, gy, 26, 20, glyph, fill, stroke, tone)
        c.text(34, gy + 14, desc, 10.5)
    c.text(0, ly + len(legend) * 24 + 16,
           "Blank cells are calls that never arise. Below the dashed rule, no Module of Trust "
           "Infrastructure may call outward.", 10.5)
    return c.render("module-dependencies")


def band_width(layers) -> int:
    n = max(min(len(comps), PER_ROW) for _, comps in layers)
    return GUTTER + n * BOX_W + (n - 1) * GAP + BAND_PAD


def component_figure(stem, title, desc, modules, note, chapter="software-architecture"):
    c = Canvas(title, desc)
    width = max(band_width(layers) for _, _, layers in modules)
    y = 0.0
    for module, kind, layers in modules:
        y = module_band(c, 0, y, width, module, kind, layers) + 20
    c.text(0, y + 6, note, 10.5)
    return c.render(stem, chapter)


# ---------------------------------------------------------------- figure 4.3

def fig_issuer_components():
    return component_figure(
        "component-issuer-services",
        "Components inside Issuer Services",
        "Issuer Core in four layers: three controllers, three domain services, three "
        "providers including Claims Provider, and one repository. Issuer Console below it "
        "has three views and a single client that reaches the Admin Controller.",
        [("ISSUER CORE", "issuer", [
            ("Controller", ["Issuance Controller", "Authorization Controller", "Admin Controller"]),
            ("Domain", ["Credential Builder", "Status Manager", "Key Attestation Validator"]),
            ("Provider", [("Claims Provider", "the only one that differs per install"),
                          "Signing Provider", "Trust SDK"]),
            ("Repository", ["Issuance Repository"])]),
         ("ISSUER CONSOLE", "issuer", [
             ("View", ["Configuration View", "Operations View", "Reporting View"]),
             ("Client", [("Core API Client", "no database connection")])])],
        "Claims Provider is the only component whose contents differ at every installation.")


# ---------------------------------------------------------------- figure 4.4

def fig_wallet_components():
    return component_figure(
        "component-wallet-services",
        "Components inside Wallet Services",
        "Mobile Wallet in four layers: four protocol clients, five domain components "
        "including Trust Display and Consent UI, two providers, and the encrypted Credential "
        "Store. Wallet Backend Service below it issues Key Attestations and keeps a device "
        "registry that holds no credential data.",
        [("WALLET APPLICATION", "wallet", [
            ("Client", ["Auth Client", "Issuance Client", "Presentation Client", "Attestation Client"]),
            ("Domain", ["Trust Display", "Consent UI", "App Lock", "Credential Renderer",
                        "Credential Codec"]),
            ("Provider", [("Keystore Manager", "secure element"), ("Trust SDK", "local cache")]),
            ("Repository", [("Credential Store", "SQLCipher, encrypted")])]),
         ("WALLET BACKEND SERVICE", "wallet", [
             ("Controller", ["Key Attestation Issuer"]),
             ("Domain", ["Account Service", "Notification Service", "Recovery Service"]),
             ("Provider", [("Signing Provider", "Wallet Provider key in HSM")]),
             ("Repository", [("Device Repository", "no credential data")])])],
        "Wallet Backend Service knows the account and the device, never the credential.")


# ---------------------------------------------------------------- figure 4.5

def fig_verifier_components():
    return component_figure(
        "component-verifier-services",
        "Components inside Verifier Services",
        "Verifier Core with three controllers, three domain services including Trust "
        "Evaluator, two providers and a repository. Verifier Console with three views and "
        "a client. Mobile Verifier, which runs on a merchant or counter device with no "
        "server, is the only proximity reader, and whose Activity Repository holds no "
        "citizen attribute.",
        [("VERIFIER CORE", "verifier", [
            ("Controller", ["Presentation Controller", "RP Controller", "Admin Controller"]),
            ("Domain", [("Credential Verifier", "SD-JWT VC and ldp_vc"),
                        ("Trust Evaluator", "entity chain, transaction chain"),
                        "Verifier Device Certificate Issuer"]),
            ("Provider", ["Signing Provider", "Trust SDK"]),
            ("Repository", ["Verification Repository"])]),
         ("VERIFIER CONSOLE", "verifier", [
             ("View", ["Template View", "Merchant View", "Reporting View"]),
             ("Client", [("Core API Client", "no database connection")])]),
         ("MOBILE VERIFIER", "verifier", [
             ("Client", ["Presentation Client", "Attestation Client"]),
             ("Domain", [("Credential Verifier", "SD-JWT VC and mdoc only")]),
             ("View", ["Result View"]),
             ("Provider", [("Keystore Manager", "secure element"), ("Trust SDK", "local cache")]),
             ("Repository", [("Activity Repository", "no citizen attribute")])])],
        "Verifier Core reads nothing in proximity. Mobile Verifier carries no ldp_vc path and verifies entirely from cache.")


# ---------------------------------------------------------------- figure 4.6

def fig_trust_components():
    return component_figure(
        "component-trust-infrastructure",
        "Components inside Trust Infrastructure",
        "Trust Authority with its registrar controller, five domain services including the "
        "Certificate Authority, and two repositories. Trust Registry, which answers TRQP and "
        "publishes the static artifacts. DID Service, which issues and resolves did:webvh. "
        "KMS, whose Key Controller exposes no sign operation.",
        [("TRUST AUTHORITY", "trust", [
            ("Controller", ["Registrar Controller"]),
            ("Domain", ["Accreditation Service", ("Certificate Authority", "both roots, offline HSM"),
                        ("Key Lifecycle Service", "never sign"), "Governance Service",
                        "Incident Service"]),
            ("Repository", ["Entity Repository", ("Transparency Log", "append only")])]),
         ("TRUST REGISTRY", "trust", [
             ("Controller", ["TRQP Controller", "Credential Rulebook Controller"]),
             ("Domain", ["List Publisher", "Conformance Crawler"]),
             ("Provider", [("Object Storage Provider", "to CDN")]),
             ("Repository", ["Registry Repository"])]),
         ("DID SERVICE", "trust", [
             ("Controller", ["Publisher Controller", "Resolver Controller"]),
             ("Domain", [("Log Service", "did.jsonl, pre-rotation")]),
             ("Provider", [("Object Storage Provider", "to CDN")]),
             ("Repository", ["Document Repository"])]),
         ("KMS", "trust", [
             ("Controller", [("Key Controller", "no sign operation")]),
             ("Domain", [("Escrow Service", "one-time key handover")]),
             ("Provider", [("Cryptographic Provider", "HSM, cloud KMS, vault")]),
             ("Repository", ["Key Registry"])])],
        "Nothing in Trust Infrastructure signs on behalf of an entity.")


# ---------------------------------------------------------------- figure 4.7

def fig_trust_sdk():
    c = Canvas(
        "Trust SDK: six parts, and the four Modules that embed it",
        "The Trust SDK is a library rather than a Module. Six parts, of which the DID "
        "Resolver Client and the X.509 Validator carry the highest risk of the Go and Dart "
        "implementations drifting apart. It is embedded as a Provider-layer component in "
        "Issuer Core, Verifier Core, Mobile Wallet and Mobile Verifier, and in no "
        "other Module.")
    parts = [("Trust Client", "TRQP", ""), ("Artifact Consumer", "trusted list, rulebook", "!"),
             ("DID Resolver Client", "did:webvh, did:key", "!!"),
             ("Status Checker", "status list, bitstring", "!"),
             ("X.509 Validator", "DSC, VDC, CRL, VICAL", "!!!"),
             ("Cache Store", "TTL, last known good", "")]
    risk = {"": ("low", "#e9ecef", "#6c757d"), "!": ("medium", "#fff3cd", "#d4a017"),
            "!!": ("high", "#ffe0cc", "#d2691e"), "!!!": ("highest", "#f8d7da", "#c0392b")}
    bw = 3 * BOX_W + 2 * GAP + BAND_PAD * 2
    c.band(0, 0, bw, BAND_LABEL + 2 * 68 + 12 + BAND_PAD, "TRUST SDK  ·  LIBRARY, NOT A MODULE")
    for i, (name, sub, mark) in enumerate(parts):
        px = BAND_PAD + (i % 3) * (BOX_W + GAP)
        py = BAND_LABEL + (i // 3) * (68 + 12)
        label, fill, stroke = risk[mark]
        c.cell(px, py, BOX_W, 68, "", fill, stroke)
        c.text(px + BOX_W / 2, py + 25, name, 11.5, "600", INK, "middle")
        c.text(px + BOX_W / 2, py + 40, sub, 10, "400", MUTED, "middle")
        c.text(px + BOX_W / 2, py + 56, f"drift risk: {label}", 9.5, "600", stroke, "middle")
    top = BAND_LABEL + 2 * 68 + 12 + BAND_PAD
    c.text(0, top + 32, "embedded as a Provider-layer component in", 11, "600", INK)
    ey = top + 48
    for i, (name, lang, kind) in enumerate([
            ("Issuer Core", "Go", "issuer"), ("Verifier Core", "Go", "verifier"),
            ("Mobile Wallet", "Dart", "wallet"), ("Mobile Verifier", "Dart", "verifier")]):
        ex = i * (BOX_W + GAP)
        c.box(ex, ey, BOX_W, 58, name, (lang,), kind)
    c.text(0, ey + 92, "and in no other Module", 11, "600", INK)
    for i, name in enumerate(["Issuer Console", "Verifier Console", "Wallet Backend Service",
                              "Trust Authority", "Trust Registry", "DID Service", "KMS"]):
        ox = (i % 4) * (BOX_W + GAP)
        oy = ey + 104 + (i // 4) * 44
        c.box(ox, oy, BOX_W, 34, name, (), "off")
    c.text(0, ey + 104 + 2 * 44 + 22,
           "One interface, two implementations, held together by shared test vectors run on "
           "every pipeline build.", 10.5)
    return c.render("trust-sdk", "software-architecture")



# ---------------------------------------------------------------- figure 1.1

DMP = "data-model-and-protocols"


def fig_credential_anatomy():
    c = Canvas(
        "What one credential carries",
        "A credential drawn as a signed envelope. Four things sit inside it: the claims, the "
        "type identifier, the holder binding and the status pointer. Across the bottom, "
        "inside the same envelope, runs the issuer's signature, which covers all four.")
    c.band(0, 0, 536, 236, "CREDENTIAL")
    for title, x, y in (("Claims", 20, 40), ("Type identifier", 276, 40),
                        ("Holder binding", 20, 114), ("Status pointer", 276, 114)):
        c.box(x, y, 240, 58, title, (), "off")
    c.box(20, 188, 496, 38, "Issuer signature", (), "issuer")
    return c.render("credential-anatomy", DMP)


# ---------------------------------------------------------------- figure 1.2

def fig_two_representations():
    c = Canvas(
        "One credential, two representations",
        "One credential key at the top. Below it the same credential exists twice, once as "
        "SD-JWT VC and once as ISO mdoc, both bound to that one key. Each representation "
        "serves one mode: SD-JWT VC online, ISO mdoc in proximity.")
    c.box(160, 0, 200, 50, "Credential key", (), "wallet")
    c.edge([(260, 50), (260, 65), (260, 80)], arrow=False)
    c.edge([(140, 80), (260, 80), (380, 80)], arrow=False)
    c.edge([(140, 80), (140, 95), (140, 110)])
    c.edge([(380, 80), (380, 95), (380, 110)])
    c.box(40, 110, 200, 54, "SD-JWT VC", (), "wallet")
    c.box(280, 110, 200, 54, "ISO mdoc", (), "wallet")
    c.edge([(140, 164), (140, 182), (140, 200)])
    c.edge([(380, 164), (380, 182), (380, 200)])
    c.box(40, 200, 200, 46, "Online", (), "verifier")
    c.box(280, 200, 200, 46, "Proximity", (), "verifier")
    return c.render("one-credential-two-representations", DMP)


# ---------------------------------------------------------------- figure 2.1

def fig_holder_identifier():
    c = Canvas(
        "A fresh holder identifier for every credential",
        "One citizen holds three credentials, and each carries a different did:key. Each "
        "credential goes to a different verifier. Because no identifier is shared between "
        "them, two verifiers comparing what they received find nothing in common.")
    c.box(220, 0, 200, 46, "One citizen", (), "wallet")
    c.edge([(320, 46), (320, 62), (320, 76)], arrow=False)
    c.edge([(100, 76), (320, 76), (540, 76)], arrow=False)
    for title, key, x in (("KTP Digital", "did:key A", 0),
                          ("Driving license", "did:key B", 220),
                          ("Diploma", "did:key C", 440)):
        c.edge([(x + 100, 76), (x + 100, 91), (x + 100, 106)])
        c.box(x, 106, 200, 58, title, (key,), "wallet")
        c.edge([(x + 100, 164), (x + 100, 182), (x + 100, 200)])
    for i, x in enumerate((0, 220, 440)):
        c.box(x, 200, 200, 46, f"Verifier {i + 1}", (), "verifier")
    c.text(320, 288,
           "no identifier in common, so two verifiers cannot tell these are one citizen",
           10.5, "600", MUTED, "middle")
    return c.render("holder-identifier-per-credential", DMP)


# ---------------------------------------------------------------- figure 3.1

def fig_protocol_per_interaction():
    c = Canvas(
        "The protocol behind each interaction",
        "Seven interactions and the standard carrying each. Issuer Core issues to Mobile "
        "Wallet over OpenID4VCI. Mobile Wallet presents to Verifier Core over OpenID4VP and "
        "to Mobile Verifier over ISO/IEC 18013-5, and exchanges a platform attestation with "
        "Wallet Backend Service for a Key Attestation. Issuer Core and Verifier Core query "
        "Trust Registry over ToIP TRQP. Mobile Verifier carries a Verifier Device "
        "Certificate from Verifier Core. Verifier Core hands its result to the Relying "
        "Party application over OIDC or SAML.")
    c.box(310, 0, 200, 50, "Wallet Backend Service", (), "wallet")
    c.box(0, 120, 200, 50, "Issuer Core", (), "issuer")
    c.box(310, 120, 200, 50, "Mobile Wallet", (), "wallet")
    c.box(620, 120, 200, 50, "Mobile Verifier", (), "verifier")
    c.box(0, 270, 200, 50, "Trust Registry", (), "trust")
    c.box(310, 270, 200, 50, "Verifier Core", (), "verifier")
    c.box(310, 390, 200, 50, "Relying Party application", (), "off")
    c.edge([(200, 145), (255, 145), (310, 145)], "OpenID4VCI")
    c.edge([(410, 120), (410, 85), (410, 50)], "Key Attestation")
    c.edge([(510, 145), (565, 145), (620, 145)], "ISO/IEC 18013-5")
    c.edge([(410, 170), (410, 200), (410, 270)], "OpenID4VP")
    c.edge([(100, 170), (100, 220), (100, 270)], "ToIP TRQP")
    c.edge([(310, 295), (255, 295), (200, 295)], "ToIP TRQP")
    c.edge([(720, 170), (720, 305), (615, 305), (510, 305)], "Verifier Device Certificate")
    c.edge([(410, 320), (410, 355), (410, 390)], "OIDC / SAML")
    return c.render("protocol-per-interaction", DMP)


# ---------------------------------------------------------------- figure 3.2

def fig_online_and_offline():
    c = Canvas(
        "Online and offline: where the network calls go",
        "Two columns. Online, Mobile Wallet presents to Verifier Core over OpenID4VP on "
        "HTTPS, and Verifier Core fetches the trusted list, the status list and a TRQP "
        "answer fresh over the network. Offline, Mobile Wallet presents to Mobile Verifier "
        "over ISO/IEC 18013-5 on BLE, and Mobile Verifier reads the same artifacts from its "
        "own cache, making no network call at all.")
    for ox, label in ((0, "ONLINE"), (440, "OFFLINE  ·  PROXIMITY")):
        c.band(ox, 0, 400, 330, label)
    for ox, who, proto, how, artifacts, foot in (
            (0, "Verifier Core", "OpenID4VP over HTTPS", "fetched fresh",
             "Trusted list, status list, TRQP", "network calls: yes"),
            (440, "Mobile Verifier", "ISO/IEC 18013-5 over BLE", "read from cache",
             "Trusted list, status list, VICAL", "network calls: zero")):
        cx = ox + 200
        c.box(ox + 115, 44, 170, 46, "Mobile Wallet", (), "wallet")
        c.edge([(cx, 90), (cx, 115), (cx, 140)], proto)
        c.box(ox + 115, 140, 170, 46, who, (), "verifier")
        c.edge([(cx, 186), (cx, 213), (cx, 240)], how)
        c.box(ox + 55, 240, 290, 50, artifacts, (), "trust")
        c.text(cx, 314, foot, 11, "600", INK, "middle")
    return c.render("online-and-offline", DMP)


# ---------------------------------------------------------------- figure 4.1

def fig_where_artifacts_live():
    c = Canvas(
        "Where each artifact lives",
        "Four columns, one per place an artifact can sit. On the central CDN: the trusted "
        "list, the Credential Rulebook and VICAL. On the entity's own domain: the DID "
        "Document and the status list. Answered on request rather than published: the "
        "Authority Statement. Carried in the exchange itself: the Accreditation Credential, "
        "the Key Attestation, the Verifier Device Certificate, the credential, the "
        "presentation and the Document Signer Certificate. Box color marks the Service that "
        "issues the artifact.")
    rows = [
        ("CENTRAL CDN",
         [("Trusted list", "trust"), ("Credential Rulebook", "trust"), ("VICAL", "trust")]),
        ("ENTITY'S OWN DOMAIN",
         [("DID Document", "trust"), ("Status list", "issuer")]),
        ("ANSWERED ON REQUEST",
         [("Authority Statement", "trust")]),
        ("CARRIED IN THE EXCHANGE",
         [("Accreditation Credential", "trust"), ("Key Attestation", "wallet"),
          ("Verifier Device Certificate", "verifier"), ("Credential", "issuer"),
          ("Presentation", "wallet"), ("Document Signer Certificate", "trust")]),
    ]
    BW, BH, G, PER = 172, 44, 10, 3
    width = 14 * 2 + PER * BW + (PER - 1) * G
    y = 0
    for label, items in rows:
        nrows = (len(items) + PER - 1) // PER
        height = 30 + nrows * BH + (nrows - 1) * G + 14
        c.band(0, y, width, height, label)
        for j, (name, kind) in enumerate(items):
            c.box(14 + (j % PER) * (BW + G), y + 30 + (j // PER) * (BH + G),
                  BW, BH, name, (), kind)
        y += height + 12
    for i, (kind, name) in enumerate((("issuer", "Issuer Services"),
                                      ("wallet", "Wallet Services"),
                                      ("verifier", "Verifier Services"),
                                      ("trust", "Trust Infrastructure"))):
        lx = (i % 2) * 280
        ly = y + 12 + (i // 2) * 26
        fill, stroke = PALETTE[kind]
        c.cell(lx, ly, 26, 18, "", fill, stroke)
        c.text(lx + 34, ly + 13, name, 10.5)
    return c.render("where-artifacts-live", DMP)


if __name__ == "__main__":
    for fn in (fig_module_map, fig_call_matrix, fig_issuer_components, fig_wallet_components,
               fig_verifier_components, fig_trust_components, fig_trust_sdk,
               fig_credential_anatomy, fig_two_representations, fig_holder_identifier,
               fig_protocol_per_interaction, fig_online_and_offline,
               fig_where_artifacts_live):
        w, h = fn()
        print(f"{fn.__name__:28} {w} x {h}")
