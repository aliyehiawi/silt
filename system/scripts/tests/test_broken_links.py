"""
Regression test: audit must catch broken wiki-link targets that aren't placeholders.
This prevents the "ghost node" failure mode (e.g. [[companies/wiremind/...]] when the
real path is [[companies/acme-corp/...]]).
"""
import sys
import shutil
import tempfile
import textwrap
import unittest
import contextlib
import io
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))

import audit  # noqa: E402


def write_file(root: Path, rel: str, content: str):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(content), encoding="utf-8")


class BrokenLinkTests(unittest.TestCase):

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="booklet-brokenlink-"))

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _run(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            audit.main(booklet=self.dir)
        return buf.getvalue()

    def test_broken_link_detected(self):
        """A wiki-link to a non-existent path (no `{` placeholder) should be flagged."""
        write_file(self.dir, "memory/me.md", """\
            ---
            type: me
            title: Me
            created: 2026-04-24
            updated: 2026-04-25
            tags: [me, spine]
            ---
            # Me
            See [[memory/work/companies/ghost-co/people/sarah.md|Sarah]].
            """)
        out = self._run()
        self.assertIn("BROKEN WIKI-LINKS", out)
        self.assertIn("ghost-co", out)

    def test_curly_placeholder_not_flagged(self):
        """A wiki-link with `{co}` is intentional template syntax — not flagged."""
        write_file(self.dir, "memory/me.md", """\
            ---
            type: me
            title: Me
            created: 2026-04-24
            updated: 2026-04-25
            tags: [me, spine]
            ---
            # Me
            Example: `[[memory/work/companies/{co}/people/sarah.md|Sarah]]`.
            """)
        out = self._run()
        self.assertNotIn("BROKEN WIKI-LINKS", out)

    def test_angle_placeholder_not_flagged(self):
        """A wiki-link with `<...>` is template syntax — not flagged."""
        write_file(self.dir, "memory/me.md", """\
            ---
            type: me
            title: Me
            created: 2026-04-24
            updated: 2026-04-25
            tags: [me, spine]
            ---
            # Me
            Example: [[<path-from-vault-root>|alias]].
            """)
        out = self._run()
        self.assertNotIn("BROKEN WIKI-LINKS", out)

    def test_link_inside_code_block_not_flagged(self):
        """Wiki-links inside fenced code blocks are doc examples — not flagged.
        (Skill files and the README contain illustrative examples.)"""
        write_file(self.dir, "memory/some-doc.md", """\
            ---
            type: note
            title: Some Doc
            created: 2026-04-24
            updated: 2026-04-25
            tags: [note]
            ---
            # Some Doc
            ```markdown
            See [[memory/life/places/tokyo.md|Tokyo]] (example).
            ```
            """)
        out = self._run()
        # Doc is not in DOC_FILES_WITH_EXAMPLES allowlist, but the example IS in a
        # code block, so it should be skipped.
        self.assertNotIn("BROKEN WIKI-LINKS", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
