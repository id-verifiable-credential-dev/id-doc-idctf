import json
import pathlib
import tempfile
import unittest

import build_corpus

PAGE = """---
title: Role map
description: What a role is.
---

<!-- Sumber: Arsitektur Ekosistem Identitas Digital v0.2, §2.1 -->

# Role map {#role-map}

A role is a set of responsibilities.

[](){ #fig-role-map }

<figure markdown="1">
  ![alt](../../images/architecture-framework/roles/role-map.svg){ loading=lazy }
  <figcaption><span class="ekdn-fignum"></span> The role map.</figcaption>
</figure>

## Others {#others}

- One point.
"""

SOON = """---
title: "Trust Model"
---

<!-- Sumber: draft §5 -->

# Trust Model {#trust-model}

<p class="ekdn-soon">(soon)</p>

## Chapter contents {#tm-chapter-contents}

1. [Chain of trust](chain-of-trust.md)
"""


class CleanPageTest(unittest.TestCase):
    def test_title_comes_from_frontmatter(self):
        title, _, _ = build_corpus.clean_page(PAGE)
        self.assertEqual(title, "Role map")

    def test_quoted_title_is_unquoted(self):
        title, _, _ = build_corpus.clean_page(SOON)
        self.assertEqual(title, "Trust Model")

    def test_strips_frontmatter_comments_figure_and_anchor(self):
        _, body, _ = build_corpus.clean_page(PAGE)
        self.assertNotIn("Sumber", body)
        self.assertNotIn("description:", body)
        self.assertNotIn("<figure", body)
        self.assertNotIn("ekdn-fignum", body)
        self.assertNotIn("[](){", body)
        self.assertNotIn(".svg", body)

    def test_keeps_headings_prose_and_lists(self):
        _, body, _ = build_corpus.clean_page(PAGE)
        self.assertIn("# Role map", body)
        self.assertIn("A role is a set of responsibilities.", body)
        self.assertIn("## Others", body)
        self.assertIn("- One point.", body)

    def test_table_inside_figure_wrapper_survives(self):
        page = (
            "---\ntitle: T\n---\n\n# T\n\n[](){ #tbl-calls }\n\n"
            '<figure markdown="1" class="ekdn-table">\n\n'
            "| Module | May call |\n|---|---|\n| Issuer Core | Registry |\n\n</figure>\n"
        )
        _, body, _ = build_corpus.clean_page(page)
        self.assertIn("| Issuer Core | Registry |", body)
        self.assertNotIn("<figure", body)
        self.assertNotIn("</figure>", body)
        self.assertNotIn("#tbl-calls", body)

    def test_heading_ids_are_dropped(self):
        _, body, _ = build_corpus.clean_page(PAGE)
        self.assertNotIn("{#role-map}", body)

    def test_inline_svg_is_stripped(self):
        page = (
            "---\ntitle: T\n---\n\n# T\n\nBefore the art.\n\n"
            '<div class="ekdn-banner__art" aria-hidden="true">\n'
            '  <svg class="ekdn-graph" viewBox="0 0 400 130">\n'
            '    <line class="ekdn-graph__edge" style="--i: 1" x1="88" y1="56" x2="172" y2="56" />\n'
            '    <circle class="ekdn-graph__node" style="--i: 0" cx="60" cy="56" r="26" />\n'
            '    <path d="M 56 52 h 8 M 56 58 h 8" />\n'
            "  </svg>\n"
            "</div>\n\n"
            "After the art.\n"
        )
        _, body, _ = build_corpus.clean_page(page)
        self.assertIn("Before the art.", body)
        self.assertIn("After the art.", body)
        self.assertNotIn("<svg", body)
        self.assertNotIn("<line", body)
        self.assertNotIn("<circle", body)
        self.assertNotIn("<path", body)
        self.assertNotIn("ekdn-graph", body)

    def test_soon_page_is_flagged_and_reduced(self):
        _, body, is_soon = build_corpus.clean_page(SOON)
        self.assertTrue(is_soon)
        self.assertEqual(body.strip(), "This page is not written yet.")

    def test_written_page_is_not_soon(self):
        _, _, is_soon = build_corpus.clean_page(PAGE)
        self.assertFalse(is_soon)


class PageUrlTest(unittest.TestCase):
    def test_index_maps_to_folder(self):
        root = pathlib.Path("/x/docs")
        self.assertEqual(build_corpus.page_url(root / "index.md", root), "/")
        self.assertEqual(
            build_corpus.page_url(root / "architecture-framework/index.md", root),
            "/architecture-framework/",
        )

    def test_page_maps_to_directory_url(self):
        root = pathlib.Path("/x/docs")
        self.assertEqual(
            build_corpus.page_url(root / "architecture-framework/roles/role-map.md", root),
            "/architecture-framework/roles/role-map/",
        )


class BuildTest(unittest.TestCase):
    def test_build_writes_corpus_and_urls(self):
        with tempfile.TemporaryDirectory() as tmp:
            docs = pathlib.Path(tmp) / "docs"
            (docs / "roles").mkdir(parents=True)
            (docs / "index.md").write_text("---\ntitle: IDCTF\n---\n\n# IDCTF {#idctf}\n\nHome.\n")
            (docs / "roles" / "role-map.md").write_text(PAGE)
            (docs / "roles" / "soon.md").write_text(SOON)
            (docs / "stylesheets").mkdir()
            (docs / "stylesheets" / "extra.css").write_text("body{}")
            out = pathlib.Path(tmp) / "site" / "ask"
            pages, soon = build_corpus.build(docs, out)
            self.assertEqual((pages, soon), (3, 1))
            corpus = (out / "corpus.txt").read_text()
            self.assertIn("=== PAGE: Role map | URL: /roles/role-map/ ===", corpus)
            self.assertIn("=== PAGE: Trust Model | URL: /roles/soon/ ===", corpus)
            self.assertIn("This page is not written yet.", corpus)
            urls = json.loads((out / "urls.json").read_text())
            self.assertEqual(
                sorted(urls), ["/", "/roles/role-map/", "/roles/soon/"]
            )

    def test_pages_are_ordered_by_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            docs = pathlib.Path(tmp) / "docs"
            docs.mkdir()
            (docs / "b.md").write_text("---\ntitle: B\n---\n\n# B\n\nb\n")
            (docs / "a.md").write_text("---\ntitle: A\n---\n\n# A\n\na\n")
            out = pathlib.Path(tmp) / "out"
            build_corpus.build(docs, out)
            corpus = (out / "corpus.txt").read_text()
            self.assertLess(corpus.index("PAGE: A"), corpus.index("PAGE: B"))


if __name__ == "__main__":
    unittest.main()
