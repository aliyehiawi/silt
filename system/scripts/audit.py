#!/usr/bin/env python3
"""
Subgraph-by-subgraph audit. For each cluster, show every file with:
- Outbound semantic edges (peer files linked from this file's body)
- Inbound semantic edges (peer files linking to this one)
- Frontmatter completeness check

Flag suspicious cases:
  * Orphan leaf: 0 inbound, 0 outbound semantic edges
  * Half-connected: only outbound (file links out but nothing links back)
  * Half-connected: only inbound (file is mentioned but doesn't link to anything)
  * Missing date / status / type fields
"""
import os, re, sys
from pathlib import Path
from collections import defaultdict

# Vault root is two levels up from this script (system/scripts/audit.py → repo root).
# Override with $BOOKLET_ROOT if you need to run from elsewhere.
BOOKLET = Path(os.environ.get("BOOKLET_ROOT", Path(__file__).resolve().parent.parent.parent))
WIKI_LINK_RE = re.compile(r"\[\[([^\]|#\\]+)(?:\\?\|([^\]]+))?\]\]")

SPINE = {"CLAUDE.md", "AGENTS.md", "README.md",
    "TASKS.md",
         "memory/all-entities.md", "memory/README.md",
         "memory/life/context.md", "memory/preferences.md",
         "memory/glossary.md",
         "journal/SKILL.md", "start/SKILL.md", "update/SKILL.md",
         "task-management/SKILL.md", "memory-management/SKILL.md",
         "system/docs/graph-convention.md", "system/docs/architecture.md", "system/version.md",
         "journal/all-time.md",
         "memory/work/_current.md", "memory/life/health/log.md"}
# Helper: also mark any monthly/yearly journal index + per-company glossary as spine
def _is_spine(rel):
    if rel in SPINE:
        return True
    if re.match(r"^journal/\d{4}/\d{4}\.md$", rel):
        return True
    if re.match(r"^journal/\d{4}/\d{2}/\d{4}-\d{2}\.md$", rel):
        return True
    if re.match(r"^memory/work/companies/[^/]+/glossary\.md$", rel):
        return True
    return False

# Cluster definitions — directory-based, auto-discovering.
#
# Per-company buckets are generated dynamically by walking memory/work/companies/.
# That way, audit output stays sensible whether you have 1 employer or 12 over a
# career, and you never have to edit this list.
#
# To add a manual sub-bucket (e.g. split friends into "closest" vs "extended" by
# name) — append a tuple `(label, lambda p: p in {"path/to/file.md", ...})` to
# CLUSTERS_EXTRA below. Lambdas take precedence over the regex buckets.
def _discover_company_clusters(booklet):
    out = []
    co_root = booklet / "memory" / "work" / "companies"
    if co_root.exists():
        for d in sorted(co_root.iterdir()):
            if d.is_dir() and not d.name.startswith("."):
                co = d.name
                pretty = co.replace("-", " ").title()
                out.append((f"Work — {pretty}", rf"^memory/work/companies/{re.escape(co)}/"))
    return out

CLUSTERS_EXTRA = [
    # Add hand-curated sub-buckets here if you want.
    # Example:
    #   ("Life — friends (inner circle)", lambda p: p in {
    #       "memory/life/people/friends/alice.md",
    #       "memory/life/people/friends/bob.md",
    #   }),
]

CLUSTERS_BASE = [
    ("Life — family", r"^memory/life/people/family/"),
    ("Life — friends", r"^memory/life/people/friends/"),
    ("Life — flatmates", r"^memory/life/people/flatmates/"),
    ("Life — teachers", r"^memory/life/people/teachers/"),
    ("Life — events", r"^memory/life/events/"),
    ("Life — topics", r"^memory/life/topics/"),
    ("Life — places", r"^memory/life/places/"),
    ("Life — orgs", r"^memory/life/orgs/"),
    ("Life — health", r"^memory/life/health/"),
    ("Life — home", r"^memory/life/home/"),
    ("Life — context/preferences", lambda p: p in {"memory/life/context.md", "memory/preferences.md"}),
    # Per-company work clusters get inserted here at runtime.
    ("Journal entries", r"^journal/\d{4}/\d{2}/\d{4}-"),
    ("Other (uncategorized)", lambda p: True),  # catch-all so every non-spine file is audited
]

def build_clusters(booklet):
    work_clusters = _discover_company_clusters(booklet)
    # Splice work clusters in just before "Journal entries"
    out = list(CLUSTERS_EXTRA)
    for c in CLUSTERS_BASE:
        if c[0] == "Journal entries":
            out.extend(work_clusters)
        out.append(c)
    return out

# Build all-files set
def main(booklet=BOOKLET):
    all_files = []
    for root, dirs, files in os.walk(booklet):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if f.endswith(".md"):
                p = Path(root)/f
                if p.is_symlink():
                    continue  # skip Claude Code SKILL.md symlinks; canonical is in system/skills/
                rel = str(p.relative_to(booklet))
                if rel.startswith("system/templates/") or rel.startswith("system/scripts/") or rel.startswith("system/skills/") or rel.endswith("/test-mv-2.md") or rel.endswith("/test-write-2.md"):
                    continue  # templates aren't entities; scripts aren't markdown content
                all_files.append(rel)
    all_set = set(all_files)

    # Build outbound edge map (filtered: only count edges within all_set, exclude self, exclude from spine sources)
    outbound = defaultdict(set)
    inbound = defaultdict(set)
    for rel in all_files:
        if _is_spine(rel):
            # spine outbound is OK to record but inbound counts will skip these
            pass
        text = (booklet/rel).read_text(encoding="utf-8")
        body = re.sub(r"\n## Linked from\n.*\Z", "", text, flags=re.DOTALL)
        for m in WIKI_LINK_RE.finditer(body):
            tgt = m.group(1).strip()
            if tgt == rel: continue
            if tgt not in all_set: continue
            outbound[rel].add(tgt)
            if rel not in SPINE:  # spine sources don't add semantic edges
                inbound[tgt].add(rel)

    # Frontmatter check
    def fm_check(rel):
        text = (booklet/rel).read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            return "no-yaml"
        yaml_block = text.split("---", 2)[1]
        missing = []
        if "type:" not in yaml_block: missing.append("type")
        if "title:" not in yaml_block: missing.append("title")
        if "created:" not in yaml_block: missing.append("created")
        if "updated:" not in yaml_block: missing.append("updated")
        return ",".join(missing) if missing else "ok"

    def cluster_match(cluster_def, rel):
        if callable(cluster_def):
            return cluster_def(rel)
        return re.match(cluster_def, rel) is not None

    print("=" * 80)
    print("VAULT-WIDE GRAPH AUDIT")
    print("=" * 80)

    # ---- Broken wiki-link check (catches ghost nodes before they reach Obsidian) ----
    # A wiki-link target is "broken" if its path doesn't resolve to a real file AND
    # doesn't contain a placeholder marker like `{` (curly-brace = template syntax,
    # intentionally non-resolvable). Broken targets create ghost nodes in Obsidian's
    # graph view — that's the failure mode users see as "phantom 'wiremind' / 'phoenix'".
    # Files that are allowed to contain example/illustrative wiki-links (skill docs).
    # Wiki-links in these files are typically inside code blocks for documentation.
    DOC_FILES_WITH_EXAMPLES = {
        "journal/SKILL.md", "start/SKILL.md", "update/SKILL.md",
        "task-management/SKILL.md", "memory-management/SKILL.md",
        "memory/README.md", "system/version.md",
        "AGENTS.md", "CLAUDE.md", "README.md",
    }
    # Known optional/external references — files that may not exist in every vault
    OPTIONAL_TARGETS = {"CONNECTORS.md"}

    def _strip_code_blocks(s: str) -> str:
        # Remove fenced code blocks (``` ... ```) so example wiki-links inside don't count.
        return re.sub(r"```[^`]*?```", "", s, flags=re.DOTALL)

    broken_links = []
    for rel in all_files:
        # Documentation files contain illustrative wiki-links inside code blocks; skip
        if rel in DOC_FILES_WITH_EXAMPLES:
            continue
        text_body = (booklet/rel).read_text(encoding="utf-8")
        # Strip the auto-generated Linked-from section (it's already validated by transform)
        body = re.sub(r"\n## Linked from\n.*\Z", "", text_body, flags=re.DOTALL)
        # Strip fenced code blocks (illustrative wiki-links inside docs)
        body = _strip_code_blocks(body)
        for m in WIKI_LINK_RE.finditer(body):
            tgt = m.group(1).strip()
            if "{" in tgt or "<" in tgt:
                continue  # placeholder syntax, intentional
            if not tgt.endswith(".md"):
                continue  # non-markdown links (script paths etc) aren't graph nodes
            if tgt in OPTIONAL_TARGETS:
                continue
            if tgt in all_set:
                continue  # resolves
            if tgt == rel:
                continue  # self-anchor
            broken_links.append((rel, tgt))

    if broken_links:
        print(f"\n## BROKEN WIKI-LINKS ({len(broken_links)} — these create ghost nodes in Obsidian)\n")
        for src, tgt in broken_links:
            print(f"  {src}  →  [[{tgt}]]")
        print("\n  Fix: either point the wiki-link at a real file, or replace the slug with a")
        print("  `{...}` placeholder (e.g. `{co}` for company, `{slug}` for entity slug). Curly-brace")
        print("  placeholders are intentionally non-resolvable so Obsidian doesn't render them.\n")

    issues = []
    if broken_links:
        issues.append(("broken-link", "vault", ["BROKEN-LINKS"], len(broken_links), 0))

    _seen = set()
    for label, cluster_def in build_clusters(booklet):
        matched = [r for r in all_files if cluster_match(cluster_def, r) and r not in _seen]
        for r in matched:
            _seen.add(r)
        if not matched: continue
        print(f"\n## {label}  ({len(matched)} files)\n")
        for rel in sorted(matched):
            oc = len(outbound[rel])
            ic = len(inbound[rel])
            flags = []
            is_journal_entry = re.match(r"journal/\d{4}/\d{2}/\d{4}-", rel) is not None
            is_spine_file = _is_spine(rel)
            is_template = rel.startswith("system/templates/")
            is_active_task = "/tasks/active/" in rel or "/tasks/waiting/" in rel
            if is_template:
                # Templates aren't entities — skip entirely.
                continue
            if is_spine_file:
                # Spine files are TOC pointers — skip orphan / only-X / FM checks.
                short = rel.split("/")[-1]
                print(f"  {short:50s}  →{oc:2d}  ←{ic:2d}  [spine]")
                continue
            fm = fm_check(rel)
            if oc == 0 and ic == 0: flags.append("ORPHAN")
            elif oc == 0: flags.append("only-inbound")
            elif ic == 0 and not is_journal_entry and not is_active_task: flags.append("only-outbound")
            if fm != "ok": flags.append(f"FM:{fm}")
            flag_str = " [" + ",".join(flags) + "]" if flags else ""
            short = rel.split("/")[-1]
            print(f"  {short:50s}  →{oc:2d}  ←{ic:2d}{flag_str}")
            if flags:
                issues.append((label, rel, flags, oc, ic))

    print("\n" + "=" * 80)
    print("ISSUES SUMMARY")
    print("=" * 80)
    print(f"Total issues: {len(issues)}")
    print()
    for label, rel, flags, oc, ic in issues:
        print(f"  [{label}] {rel}  →{oc} ←{ic}  {flags}")


if __name__ == "__main__":
    main()
