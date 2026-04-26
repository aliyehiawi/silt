"""
Smoke + regression tests for system/scripts/transform.py.

Run:    python3 system/scripts/tests/test_transform.py
Or via: bash system/scripts/run_tests.sh
"""
import os
import re
import sys
import shutil
import tempfile
import textwrap
import unittest
from pathlib import Path

# Make transform.py importable
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))

import transform  # noqa: E402


class TempVault:
    """Build a tiny synthetic vault under a tempdir, point transform.BOOKLET at it."""

    def __init__(self):
        self.dir = Path(tempfile.mkdtemp(prefix="booklet-test-"))
        self.original_booklet = transform.BOOKLET

    def __enter__(self):
        transform.BOOKLET = self.dir
        return self

    def __exit__(self, *exc):
        transform.BOOKLET = self.original_booklet
        shutil.rmtree(self.dir, ignore_errors=True)

    def write(self, rel, content):
        p = self.dir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(textwrap.dedent(content), encoding="utf-8")

    def read(self, rel):
        return (self.dir / rel).read_text(encoding="utf-8")


class TransformTests(unittest.TestCase):

    def test_pseudo_frontmatter_to_yaml(self):
        with TempVault() as v:
            v.write("memory/life/people/friends/anna.md", """\
                # Anna

                **Type:** person
                **Status:** active (as of 2026-04-24)
                **Created:** 2026-04-24
                **Updated:** 2026-04-24

                ## Notes

                Friend.
                """)
            transform.transform_file("memory/life/people/friends/anna.md")
            text = v.read("memory/life/people/friends/anna.md")
            self.assertTrue(text.startswith("---\n"))
            self.assertIn("type: person", text)
            self.assertIn("created: 2026-04-24", text)
            self.assertIn("updated: 2026-04-24", text)
            # Pseudo-frontmatter no longer present in body
            self.assertNotIn("**Type:**", text)
            self.assertNotIn("**Created:**", text)

    def test_idempotency(self):
        """Running transform_file twice must produce identical output."""
        with TempVault() as v:
            v.write("memory/life/people/friends/bob.md", """\
                ---
                type: person (friend)
                title: Bob
                status: active (as of 2026-04-24)
                created: 2026-04-24
                updated: 2026-04-24
                tags:
                  - life
                  - person
                  - friend
                ---

                # Bob

                Friend.

                ## Log

                - 2026-04-24 — stub.
                """)
            transform.transform_file("memory/life/people/friends/bob.md")
            once = v.read("memory/life/people/friends/bob.md")
            transform.transform_file("memory/life/people/friends/bob.md")
            twice = v.read("memory/life/people/friends/bob.md")
            self.assertEqual(once, twice)

    def test_wiki_link_normalization(self):
        """Markdown link [Text](path) should become [[path|Text]]."""
        with TempVault() as v:
            v.write("memory/life/people/friends/charlie.md", """\
                ---
                type: person (friend)
                title: Charlie
                created: 2026-04-24
                updated: 2026-04-24
                tags:
                  - life
                  - person
                  - friend
                ---

                # Charlie

                Knows [Diana](memory/life/people/friends/diana.md).
                """)
            v.write("memory/life/people/friends/diana.md", """\
                ---
                type: person (friend)
                title: Diana
                created: 2026-04-24
                updated: 2026-04-24
                tags:
                  - life
                  - person
                  - friend
                ---
                # Diana
                """)
            transform.transform_file("memory/life/people/friends/charlie.md")
            text = v.read("memory/life/people/friends/charlie.md")
            self.assertIn("[[memory/life/people/friends/diana.md|Diana]]", text)
            self.assertNotIn("[Diana](memory/life", text)

    def test_arrow_path_normalization(self):
        with TempVault() as v:
            v.write("memory/life/people/friends/eve.md", """\
                ---
                type: person (friend)
                title: Eve
                created: 2026-04-24
                updated: 2026-04-24
                tags:
                  - life
                  - person
                  - friend
                ---
                # Eve
                Met → memory/life/people/friends/frank.md
                """)
            v.write("memory/life/people/friends/frank.md", "---\ntype: person (friend)\ntitle: Frank\ncreated: 2026-04-24\nupdated: 2026-04-24\ntags:\n  - life\n---\n# Frank\n")
            transform.transform_file("memory/life/people/friends/eve.md")
            text = v.read("memory/life/people/friends/eve.md")
            self.assertIn("[[memory/life/people/friends/frank.md|", text)

    def test_backlink_generation(self):
        """Pass B should append `## Linked from` listing inbound sources."""
        with TempVault() as v:
            v.write("memory/life/people/friends/grace.md", """\
                ---
                type: person (friend)
                title: Grace
                created: 2026-04-24
                updated: 2026-04-24
                tags:
                  - life
                  - person
                  - friend
                ---
                # Grace
                Friend of [[memory/life/people/friends/henry.md|Henry]].
                """)
            v.write("memory/life/people/friends/henry.md", """\
                ---
                type: person (friend)
                title: Henry
                created: 2026-04-24
                updated: 2026-04-24
                tags:
                  - life
                  - person
                  - friend
                ---
                # Henry
                """)
            # Run the full pipeline
            transform.main()
            henry = v.read("memory/life/people/friends/henry.md")
            self.assertIn("## Linked from", henry)
            self.assertIn("memory/life/people/friends/grace.md", henry)

    def test_spine_filtered_from_backlinks(self):
        """A spine source (e.g. a SKILL file) should NOT appear in inbound backlinks."""
        with TempVault() as v:
            v.write("system/skills/journal.md", """\
                ---
                type: skill
                title: Journal Skill
                created: 2026-04-24
                updated: 2026-04-24
                tags:
                  - skill
                  - spine
                ---
                # Journal Skill
                Refers to [[memory/life/people/friends/iris.md|Iris]] as an example.
                """)
            v.write("memory/life/people/friends/iris.md", """\
                ---
                type: person (friend)
                title: Iris
                created: 2026-04-24
                updated: 2026-04-24
                tags:
                  - life
                  - person
                  - friend
                ---
                # Iris
                """)
            transform.main()
            iris = v.read("memory/life/people/friends/iris.md")
            # The journal skill mentions Iris but is spine — should NOT appear in Iris's backlinks
            self.assertNotIn("[[system/skills/journal.md", iris)

    def test_escaped_pipe_in_table(self):
        """Wiki-links with escaped pipes (Obsidian table syntax) should still count as edges."""
        with TempVault() as v:
            v.write("memory/me.md", r"""---
type: me
title: Me
created: 2026-04-24
updated: 2026-04-24
tags:
  - me
---
# Me

| Role | Where |
|---|---|
| Engineer | [[memory/work/companies/foo/foo.md\|Foo Corp]] |
""")
            v.write("memory/work/companies/foo/foo.md", """\
                ---
                type: company
                title: Foo Corp
                created: 2026-04-24
                updated: 2026-04-24
                tags:
                  - work
                  - company/foo
                ---
                # Foo Corp
                """)
            transform.main()
            foo = v.read("memory/work/companies/foo/foo.md")
            self.assertIn("## Linked from", foo)
            self.assertIn("memory/me.md", foo)


if __name__ == "__main__":
    unittest.main(verbosity=2)
