"""Drop the `<!-- Sumber: ... -->` origin comment from every page at build time.

The comment stays in `docs/` so a draft change can be traced to the pages it
touches (CLAUDE.md section 5). It names internal decisions and source files,
so it never reaches the published HTML.
"""
import re

_SOURCE = re.compile(r"<!--\s*Sumber:.*?-->\n?", re.S)


def on_page_markdown(markdown, **kwargs):
    return _SOURCE.sub("", markdown)
