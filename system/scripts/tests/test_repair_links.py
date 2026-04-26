"""Smoke test for system/scripts/repair_links.py."""
import sys
import shutil
import tempfile
import textwrap
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))

import repair_links  # noqa: E402


def write_file(root: Path, rel: str, content: str):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(content), encoding="utf-8")


class RepairLinksTests(unittest.TestCase):

    def test_repair_basename_match(self):
        d = Path(tempfile.mkdtemp(prefix="booklet-repair-"))
        try:
            write_file(d, "memory/life/people/friends/anna.md", """\
                ---
                type: person (friend)
                title: Anna
                tags: [life, person, friend]
                ---
                # Anna
                """)
            write_file(d, "memory/me.md", """\
                ---
                type: me
                title: Me
                tags: [me]
                ---
                # Me
                Knows [[memory/people/anna.md|Anna]].
                """)
            repair_links.main(booklet=d)
            me = (d / "memory/me.md").read_text()
            self.assertIn("[[memory/life/people/friends/anna.md", me)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_no_change_when_links_resolve(self):
        d = Path(tempfile.mkdtemp(prefix="booklet-repair2-"))
        try:
            write_file(d, "memory/me.md", """\
                ---
                type: me
                title: Me
                tags: [me]
                ---
                # Me
                Knows [[memory/foo.md|Foo]].
                """)
            write_file(d, "memory/foo.md", """\
                ---
                type: note
                title: Foo
                tags: [note]
                ---
                # Foo
                """)
            before = (d / "memory/me.md").read_text()
            repair_links.main(booklet=d)
            after = (d / "memory/me.md").read_text()
            self.assertEqual(before, after)
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
