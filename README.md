# IDCTF

Documentation site for **IDCTF, the Indonesia Digital Credential Trust
Framework** — the rules under which digital credentials are issued, held, and
verified in Indonesia.

IDCTF is five documents:


| Code          | Document                    | What it holds                                                                  |
| ------------- | --------------------------- | ------------------------------------------------------------------------------ |
| `IDCTF-AF`    | Architecture Framework      | Roles, modules, data model, trust model, use-case flows, software architecture |
| `IDCTF-TS-nn` | Technical Specifications    | Normative rules binding implementations                                        |
| `IDCTF-GF`    | Governance Framework        | Who may join, obligations, assessment, incidents, sanctions                    |
| `IDCTF-CR`    | Credential Rulebook Catalog | Rules per credential type                                                      |
| `IDCTF-DL`    | Decision Log                | Numbered decisions and their status                                            |




## Status

Only the Architecture Framework is being written. Of it, only the Roles chapter
is finished.


| Document      | Chapter                   | Status      |
| ------------- | ------------------------- | ----------- |
| `IDCTF-AF`    | Roles                     | Written     |
| `IDCTF-AF`    | High-Level Architecture   | Drafting    |
| `IDCTF-AF`    | Data Model and Protocols  | Not started |
| `IDCTF-AF`    | Trust Model               | Not started |
| `IDCTF-AF`    | Software Architecture     | Not started |
| `IDCTF-AF`    | Tech Stack and Deployment | Not started |
| `IDCTF-AF`    | Module Guides             | Not started |
| `IDCTF-TS-nn` | —                         | Not started |
| `IDCTF-GF`    | —                         | Not started |
| `IDCTF-CR`    | —                         | Not started |
| `IDCTF-DL`    | —                         | Not started |


A page whose prose is unwritten carries a `(soon)` marker and holds section
headings only.

## Running

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

mkdocs serve             # dev server — http://127.0.0.1:8000
mkdocs build --strict    # static output into site/; warnings become errors
```

The site is English only. Content lives in `docs/`; the chapter order comes
from `nav:` in `mkdocs.yml`.

## Hosting on Vercel

`vercel.json` holds the whole deployment: no framework preset, a `.venv` built
in the container with `requirements.txt` installed into it, and
`.venv/bin/python -m mkdocs build --strict` as the build step. The output
directory is `site/`, served at the root — the site is not versioned, so there
are no version subdirectories and no redirect. `trailingSlash` is on to match
the directory URLs MkDocs writes.

The install step has to go through a virtualenv: the build container's
interpreter is uv-managed and marked externally managed, so a plain
`pip install` into it fails with `error: externally-managed-environment`
(PEP 668). The local `.venv/` is covered by `.gitignore`, so the macOS copy
never ships, and cannot collide with the one the container builds.

Import the repository at <https://vercel.com/new> and accept the settings from
`vercel.json`, or deploy from this folder with `npx vercel --prod`.
