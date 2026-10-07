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

Only the Architecture Framework is being written. Roles, High-Level Architecture,
Data Model and Protocols, the Glossary, and References are done; Software
Architecture is part written, and the Trust Model has not started. 22 of 45 pages
carry prose.


| Document      | Chapter                           | Status                      |
| ------------- | --------------------------------- | --------------------------- |
| `IDCTF-AF`    | Roles                             | ![Written][written]         |
| `IDCTF-AF`    | High-Level Architecture           | ![Written][written]         |
| `IDCTF-AF`    | Software Architecture             | ![Drafting][drafting]       |
| `IDCTF-AF`    | Data Model and Protocols          | ![Written][written]         |
| `IDCTF-AF`    | Trust Model                       | ![Not started][not-started] |
| `IDCTF-AF`    | Glossary                          | ![Written][written]         |
| `IDCTF-AF`    | References                        | ![Written][written]         |
| `IDCTF-TS-nn` | —                                 | ![Not started][not-started] |
| `IDCTF-GF`    | —                                 | ![Not started][not-started] |
| `IDCTF-CR`    | —                                 | ![Not started][not-started] |
| `IDCTF-DL`    | —                                 | ![Not started][not-started] |


![Written][written] every page has prose ·
![Drafting][drafting] some pages still `(soon)` ·
![Not started][not-started] every page `(soon)`

A page whose prose is unwritten carries a `(soon)` marker and holds section
headings only.

[written]: https://img.shields.io/badge/Written-✅-brightgreen
[drafting]: https://img.shields.io/badge/Drafting-🚧-yellow
[not-started]: https://img.shields.io/badge/Not_started-📅-blue

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

## Ask IDCTF

A floating button on every page opens a drawer that answers questions from
the site's own pages. The drawer posts to `/api/chat/` (trailing slash, so
`trailingSlash` in `vercel.json` does not redirect it), served by `api/chat.py`,
a Vercel Python function; the guardrails and the Gemini call live in `api/_ask/`. The
design is in `specs/2026-10-07-ask-idctf-design.md`.

Environment variables on the Vercel project:

| Variable | Required | Default |
|---|---|---|
| `GEMINI_API_KEY` | yes | none; without it the function answers `503` |
| `ASK_MODEL` | no | `gemini-flash-latest` |
| `ASK_MODEL_FALLBACK` | no | `gemini-flash-lite-latest` |

Restrict the key in Google AI Studio to the Generative Language API and set
a quota and a budget alert on it: the function's own rate limit is per warm
instance and is a brake, not a wall. Each question sends the whole corpus,
about 56,000 words, as context, so the cost per question is roughly 75,000
input tokens; the brake is per warm instance, so concurrent instances
multiply it.
A free-tier key allows roughly three such questions a minute and a few
hundred a day; past that Google answers 429, which the drawer shows as the
"not available" line. The first live run also showed `gemini-flash-latest`
failing on every call while `gemini-flash-lite-latest` answered in two to
three seconds, so on a free key `ASK_MODEL=gemini-flash-lite-latest` is the
faster setting.

The build writes the corpus to `site/ask/` after `mkdocs build`
(`scripts/build_corpus.py`); the function fetches it from its own
deployment on first use. Vercel's Deployment Protection must be off for the
deployment the function runs in, or that fetch returns the sign-in page and
every question answers 503.

Local development, with the function on the same origin as the pages (the
function sends no CORS headers, so a split origin cannot work):

```bash
cp .env.example .env                 # once; fill in GEMINI_API_KEY
.venv/bin/python -m mkdocs build --strict && .venv/bin/python scripts/build_corpus.py
.venv/bin/python scripts/serve_ask.py                            # http://127.0.0.1:8010
```

`scripts/serve_ask.py` serves `site/` and routes `POST /api/chat` through the
same handler class Vercel runs. It reads `.env` at the repository root
(gitignored; `.env.example` lists the variables) and lets the real
environment override it. It does not watch files: rebuild and restart after
an edit. Without a key every question answers 503.

Tests and the guardrail evaluation:

```bash
.venv/bin/python -m unittest discover -s tests -t . -v
.venv/bin/python scripts/eval_ask.py              # dry: validates the cases, no network
.venv/bin/python scripts/eval_ask.py --live       # posts to the running function, 20 cases per 10 minutes
```
