# idn-doc-ekdn-v2

Documentation site (MkDocs + Material for MkDocs) — **IDCTF, the Indonesia
Digital Credential Trust Framework**. IDCTF is five documents: the Architecture
Framework (`IDCTF-AF`), the Technical Specifications (`IDCTF-TS-nn`), the
Governance Framework (`IDCTF-GF`), the Credential Rulebook Catalog
(`IDCTF-CR`), and the Decision Log (`IDCTF-DL`).

Working rules for this repository are in [CLAUDE.md](./CLAUDE.md).

## Running

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

mkdocs serve   # dev server — http://127.0.0.1:8000
mkdocs build   # static output, single version, into site/

python3 scripts/build_versions.py   # static output, all versions, into site/
```

Add `--strict` to `mkdocs build` to promote warnings to errors — dead links,
files missing from `nav:`, and `nav:` entries pointing at missing files then
fail the build. That is the verification gate for this repository.

## Documentation versions

The version list lives in `versions.json` at the project root. It currently
holds two demo versions: `0.0.2` (aliased `latest`) and `0.0.1`.

The navbar version combobox reads that file relative to the page's parent
(`<base>/../versions.json`) and links each version to `<base>/../<version>/`.
So every version needs its own subdirectory. `python3
scripts/build_versions.py` assembles that:

```
site/
  versions.json
  index.html      # redirect to latest/
  0.0.1/
  0.0.2/
  latest/         # copy of 0.0.2
```

The version number in the landing page status strip is rewritten automatically
on each build, so `docs/index.md` only ever needs to carry one number.

Adding a version: add an entry to `versions.json` and re-run the script. The
`latest` alias decides where the site root redirects, and any version that is
not `latest` raises the "outdated version" banner from `overrides/main.html`.

Note: `mkdocs serve` builds a single version with no versioned directory, so
the combobox does not work there — run the script above and serve `site/` to
test it. If this project ever becomes a git repository, `mike` can replace the
script with the same layout.

## Languages

The site is English only. The `mkdocs-static-i18n` plugin stays configured
under `mkdocs.yml plugins.i18n` so a second language can return without
rebuilding that block, but English is the default locale and its files carry
no suffix (`index.md`). The `id` locale is listed with `build: false`: no
`/id/` directory is written, every Indonesian URL returns 404, and the navbar
language toggle does not render. Filenames and folder names are English
slugs, so every published URL is English.

Adding a new page: write `docs/topic.md` and register it in `nav:`. Bringing
Indonesian back means flipping `build: false` to `true`, adding `*.id.md`
files beside the English ones, and filling in `nav_translations` for the `id`
locale. Inter-page links in Markdown are **always written without the language
suffix** — the plugin strips the suffix at build time, and one correct link
serves both languages.

Note: `navigation.instant` in `theme.features` is deliberately **off** — the
feature is incompatible with the language toggle, so it stays off while the
i18n plugin is configured (the plugin emits a warning if you switch it back
on).

## Structure

- `docs/` — documentation content. An Introduction landing page (`index.md`)
  and five document folders, one navbar tab each:
  `docs/architecture-framework/`, `docs/technical-specifications/`,
  `docs/governance-framework/`, `docs/credential-rulebook/`,
  `docs/decision-log/`. Only the Architecture Framework has a chapter tree;
  the other four are one `index.md` each, marked `(soon)`. That chapter tree
  lives only in this repository — `nav:` in `mkdocs.yml` plus the file tree
  under `docs/`; the `struktur-dokumen-ekosistem.md` file that once served as
  the reference has been deleted, since it no longer matched the draft. Every
  section whose prose is unwritten carries a `<p class="ekdn-soon">(soon)</p>`
  marker. Each file records its origin chapter in the v0.2 draft as an HTML
  comment at the top, so a draft change can be traced back to the affected
  pages with `grep -rn "§5.5" docs/`. For TS specifically, the frontmatter
  `title:` is prefixed with the identifier (`[TS-05] Key Attestation and Device
  Binding`) so navigation, breadcrumbs, tab titles, and search results carry
  the number; the `#` heading in the body stays unnumbered, with the identifier
  in a `.ekdn-docid` paragraph above it.

  Chapters with a lot of content split into one page per section: nine middle
  chapters in the AF (Roles through Module Guides) and eight middle chapters
  in the GF (Governance Structure through Incidents and Continuity) plus the
  appendices. Those files live in a folder named after
  the chapter slug, with `index.md` as the chapter overview (the
  `navigation.indexes` feature) and one file per section. Short introductory
  and reference chapters stay a single page, with sections as `##` headings. TS
  stays one page per specification, following the TS1–TS14 pattern in the EUDI
  ARF; only the Credential Rulebook becomes a folder, because Appendix A holds
  a rulebook catalogue where each credential type stands on its own.

  Titles, navigation labels, and filenames carry no chapter numbers. Order
  comes from `nav:` in `mkdocs.yml`, not from filename sorting, so adding or
  moving a chapter means editing `nav:`. Specification identifiers (TS-00
  through TS-12) are not lost — they are written inside the page as
  `<p class="ekdn-docid">TS-01</p>` directly above the title.

  `navigation.sections` is deliberately off: with chapters holding section
  pages, that feature forces every chapter open and makes the left rail far too
  long. Without it, each chapter opens and closes on its own, and the page
  table of contents stays in the right rail.
- `source-data/` — source material. `Arsitektur Ekosistem Identitas Digital —
  Draft v0.2.md` is the content source for the Architecture Framework.
  `Bentuk Data Attestation.md` holds the wire format of the four attestation
  layers (platform attestation, Key Attestation, Verifier Device Certificate,
  Accreditation Credential), used when writing TS-03, TS-05, and TS-06.
  `JWT di OpenID4VCI dan OpenID4VP.md` walks through every HTTP message and
  every JWT in both protocols, used when writing TS-07 and TS-08. Both are
  copies of artifacts; the origin URL sits in each file's frontmatter.
  `arsip/arsitektur-standar/` holds the "Arsitektur dan Standar" pages that
  were dropped from navigation when the navbar moved to four tabs; they have
  not been merged into the Architecture Framework.
- `images/` — `.drawio` sources for diagrams, in per-document subfolders. Not
  published: MkDocs only serves files under `docs/`.
- `docs/images/` — the `.svg` exports of those diagrams, same per-document
  subfolders. This is what pages link to.
- `docs/stylesheets/extra.css` — the site's visual system. The palette and
  layout derive from the BLPID design (primary `#0281FF`, an ink scale,
  hairlines, tints); typography and the top bar follow the GitBook
  documentation site (Inter, 16px/26px body text, 30/24/20/16px headings at
  weight 600, 768px reading column, a white header with a hairline and a search
  pill). `primary: custom` / `accent: custom` in `mkdocs.yml` is what activates
  the `--md-primary-fg-color` tokens set here.
- `versions.json` — the version list read by the navbar combobox.
- `scripts/build_versions.py` — the versioned-site builder.
- `overrides/main.html` — one template block: the "outdated version" banner.
- `overrides/.icons/lucide/` — the [Lucide](https://lucide.dev) icon set (from
  the `lucide-static` package; the same artwork as `lucide-react`). Used by the
  theme through `theme.icon.*` in `mkdocs.yml`, and from Markdown as
  `:lucide-<name>:`. Adding an icon: copy its SVG file into that folder.
- `tracks/` — the decision trail. One file per settled decision; the format is
  in [CLAUDE.md](./CLAUDE.md), section 8.
- `mkdocs.yml` — off-the-shelf components: Material navigation features (tabs,
  sections, search, code copy, tooltips, and so on), the local search and HTML
  minify plugins, and Markdown extensions (admonition, tabs,
  superfences/mermaid, tasklist, and more).
