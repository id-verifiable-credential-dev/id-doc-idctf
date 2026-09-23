#!/usr/bin/env python3
"""Build the versioned site without `mike`.

The version combobox in the Material navbar reads `versions.json` relative to
the page's parent (`<base>/../versions.json`) and links each version to
`<base>/../<version>/`. So every version must occupy its own subdirectory, with
`versions.json` sitting one level above them:

    site/
      versions.json
      index.html      -> redirect to the default alias
      0.0.1/
      0.0.2/
      latest/         -> copy of the version aliased as `latest`

`mike` normally assembles that layout on a `gh-pages` branch. This project is
not a git repository, so this script produces the same layout straight from the
working directory: for each entry in `versions.json`, the contents of `docs/`
are copied to a temporary directory, the version number in the status strip is
rewritten to match, and MkDocs builds it into `site/<version>/`.

Usage:

    python3 scripts/build_versions.py [-d site]

Adding a new version means adding an entry to `versions.json` and re-running
this script.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The landing page status strip carries the version number.
# This pattern is deliberately narrow so version-like numbers elsewhere (the
# 127.0.0.1 address in the docs, for instance) are not rewritten too.
VERSION_IN_TEXT = re.compile(r"(?<=\*\*)\d+\.\d+\.\d+(?=\*\*)")

REDIRECT_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>IDCTF — Indonesia Digital Credential Trust Framework</title>
<link rel="canonical" href="{target}/">
<meta http-equiv="refresh" content="0; url={target}/">
</head>
<body>
<p>Redirecting to <a href="{target}/">version {target}</a>.</p>
</body>
</html>
"""


def read_versions() -> list[dict]:
    versions = json.loads((ROOT / "versions.json").read_text(encoding="utf-8"))
    if not versions:
        sys.exit("versions.json is empty — nothing to build.")
    return versions


def build_version(version: str, out_dir: Path) -> None:
    """Build one version into `out_dir` from a temporary copy of the project."""
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "project"
        work.mkdir()
        shutil.copy2(ROOT / "mkdocs.yml", work / "mkdocs.yml")
        shutil.copytree(ROOT / "docs", work / "docs")
        shutil.copytree(ROOT / "overrides", work / "overrides")

        for page in work.joinpath("docs").rglob("*.md"):
            text = page.read_text(encoding="utf-8")
            patched = VERSION_IN_TEXT.sub(version, text)
            if patched != text:
                page.write_text(patched, encoding="utf-8")

        # Run with the working directory set to the temporary copy: pymdownx
        # resolves the `custom_icons` path against the working directory, not
        # against the config file.
        subprocess.run(
            [sys.executable, "-m", "mkdocs", "build", "--quiet",
             "-f", str(work / "mkdocs.yml"),
             "-d", str(out_dir)],
            cwd=work,
            check=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-d", "--site-dir", default="site",
        help="output directory (default: site)",
    )
    args = parser.parse_args()

    site = (ROOT / args.site_dir).resolve()
    if site.exists():
        shutil.rmtree(site)
    site.mkdir(parents=True)

    versions = read_versions()
    default_target = versions[0]["version"]

    for entry in versions:
        version = entry["version"]
        print(f"building version {version}")
        build_version(version, site / version)

        for alias in entry.get("aliases", []):
            print(f"  alias {alias} -> {version}")
            shutil.copytree(site / version, site / alias)
            if alias == "latest":
                default_target = alias

    shutil.copy2(ROOT / "versions.json", site / "versions.json")
    (site / "index.html").write_text(
        REDIRECT_PAGE.format(target=default_target), encoding="utf-8"
    )
    print(f"done — {site} (root redirects to {default_target}/)")


if __name__ == "__main__":
    main()
