#!/usr/bin/env python3
"""
Walk all .md files, find every [[path|alias]] wiki-link.
If the path doesn't resolve, try to repair it:
- Try to find the target file by basename
- Try to strip a leading "journal/YYYY/MM/" prefix accidentally added
"""
import os, re
from pathlib import Path
from collections import defaultdict

BOOKLET = Path("/sessions/jolly-confident-franklin/mnt/my booklet")
WIKI_LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:\|([^\]]+))?\]\]")

def main(booklet=BOOKLET):
    # Build basename -> rel path index
    basename_to_paths = defaultdict(list)
    all_files = []
    for root, dirs, files in os.walk(booklet):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if f.endswith(".md"):
                p = Path(root) / f
                rel = str(p.relative_to(booklet))
                all_files.append(rel)
                basename_to_paths[f].append(rel)

    def repair_target(target: str):
        """Return repaired target (or original)."""
        if (booklet / target).exists():
            return target
        # Try stripping a journal/YYYY/MM/ prefix that got tacked on
        m = re.match(r"journal/\d{4}/\d{2}/(.*)$", target)
        if m:
            candidate = m.group(1)
            if (booklet / candidate).exists():
                return candidate
        # Try stripping any leading non-memory segment
        if "/memory/" in target:
            idx = target.index("/memory/")
            candidate = target[idx+1:]
            if (booklet / candidate).exists():
                return candidate
        # Try basename lookup
        bn = Path(target).name
        if bn in basename_to_paths and len(basename_to_paths[bn]) == 1:
            return basename_to_paths[bn][0]
        return target

    repaired = [0]
    for rel in all_files:
        path = booklet / rel
        text = path.read_text(encoding="utf-8")
        def repl(m):
            target = m.group(1).strip()
            alias = m.group(2)
            new_target = repair_target(target)
            if new_target != target:
                repaired[0] += 1
                if alias:
                    return f"[[{new_target}|{alias}]]"
                return f"[[{new_target}]]"
            return m.group(0)
        new_text = WIKI_LINK_RE.sub(repl, text)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")

    print(f"Repaired {repaired[0]} broken wiki-link paths")


if __name__ == "__main__":
    main()
