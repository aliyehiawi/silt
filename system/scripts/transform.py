#!/usr/bin/env python3
"""
Idempotent version: reads existing YAML frontmatter (if present) and merges
with pseudo-frontmatter, keeping created/updated and other preserved fields.
"""
import os, re, json, sys
from pathlib import Path
from collections import defaultdict

# Vault root is two levels up from this script (system/scripts/transform.py → repo root).
# Override with $BOOKLET_ROOT if you need to run from elsewhere.
BOOKLET = Path(os.environ.get("BOOKLET_ROOT", Path(__file__).resolve().parent.parent.parent))
EXCLUDE_DIRS = {".git"}

# `created`/`updated` defaults when the script can't infer one. Replaced at runtime
# with today's date via __import__('datetime').date.today().isoformat() — keep the
# constant here only for fixture/tests that pin a deterministic date.
import datetime as _dt
TODAY = _dt.date.today().isoformat()

# Files whose outbound links are TOC noise — exclude them from inbound backlink lists.
# (They still get their own Linked-from from real semantic sources.)
SPINE_SOURCES = {
    "CLAUDE.md",
    "AGENTS.md",
    "README.md",
    "TASKS.md",
    "memory/work/_current.md", "memory/life/health/log.md",
    "memory/all-entities.md",
    "memory/README.md",
    "memory/life/context.md",
    "memory/preferences.md",
    "memory/glossary.md",
    "journal/SKILL.md",
    "start/SKILL.md",
    "update/SKILL.md",
    "task-management/SKILL.md",
    "memory-management/SKILL.md",
    "system/docs/graph-convention.md",
    "system/docs/architecture.md",
    "system/version.md",
    "journal/all-time.md",
}
# Also auto-mark any journal/YYYY/YYYY.md or journal/YYYY/MM/YYYY-MM.md as spine
def is_spine(rel):
    if rel in SPINE_SOURCES:
        return True
    if re.match(r"^journal/\d{4}/\d{4}\.md$", rel):
        return True
    if re.match(r"^journal/\d{4}/\d{2}/\d{4}-\d{2}\.md$", rel):
        return True
    if re.match(r"^memory/work/companies/[^/]+/glossary\.md$", rel):
        return True
    return False

MANUAL_FILES = {
    "CLAUDE.md",
    "AGENTS.md",
    "README.md",
    "TASKS.md",
    "memory/work/_current.md", "memory/life/health/log.md",
    "memory/README.md",
    "memory/all-entities.md",
    "memory/me.md",
    "journal/SKILL.md",
    "start/SKILL.md",
    "update/SKILL.md",
    "task-management/SKILL.md",
    "memory-management/SKILL.md",
    "system/docs/graph-convention.md",
    "system/docs/architecture.md",
    "system/version.md",
}

PSEUDO_FM_RE = re.compile(r"^\s*\*\*(.+?):\*\*\s*(.+?)\s*$")
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
ARROW_PATH_RE = re.compile(r"((?:→|↗)\s+)([A-Za-z0-9_./-][A-Za-z0-9_./-]*\.md)\b")
TICK_PATH_RE = re.compile(r"`([A-Za-z0-9_./-]*/[A-Za-z0-9_./-]+\.md)`")  # require a slash to avoid bare-filename false positives
WIKI_LINK_RE = re.compile(r"\[\[([^\]|#\\]+)(?:\\?\|([^\]]+))?\]\]")

def normalize_link_target(src_dir: Path, target: str) -> str:
    target = target.strip().strip("`'\"")
    if not target:
        return target
    if target.startswith(("http://", "https://", "mailto:")):
        return None
    # Treat paths starting with a known root as absolute-from-booklet
    ROOTS = ("memory/", "journal/", "TASKS.md", "CLAUDE.md")
    if target.startswith(ROOTS):
        if (BOOKLET / target).exists():
            return target
        return target  # broken but still treat as absolute
    # Otherwise resolve relative to source dir
    candidate = (src_dir / target).resolve()
    if str(candidate).startswith(str(BOOKLET)):
        rel = str(candidate.relative_to(BOOKLET))
        if (BOOKLET / rel).exists():
            return rel
        return rel
    try:
        return str(candidate.relative_to(BOOKLET))
    except ValueError:
        return target

def stem_to_display(stem: str) -> str:
    return " ".join(w.capitalize() if w.islower() else w for w in stem.replace("_", "-").split("-"))

def display_for_path(p: str) -> str:
    stem = Path(p).stem
    if stem.lower() in ("readme", "index", "_current"):
        parts = p.split("/")
        if len(parts) >= 2:
            base = parts[-2] if parts[-2] else parts[-1]
            return stem_to_display(base) if stem.lower() == "readme" else stem_to_display(stem)
    return stem_to_display(stem)

def to_wiki_link(target_path, display=None):
    if display:
        return f"[[{target_path}|{display}]]"
    return f"[[{target_path}]]"

# ---- YAML I/O -------------------------------------------------------

def parse_yaml_block(text):
    """Parse our flat YAML (string + list-of-strings). Returns dict."""
    out = {}
    cur_list_key = None
    for line in text.splitlines():
        if cur_list_key:
            m = re.match(r"^\s+-\s+(.*)$", line)
            if m:
                out[cur_list_key].append(m.group(1).strip())
                continue
            else:
                cur_list_key = None
        if not line.strip():
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$", line)
        if not m:
            continue
        k, v = m.group(1), m.group(2)
        if not v.strip():
            cur_list_key = k
            out[k] = []
        else:
            v = v.strip()
            # unquote
            if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                v = v[1:-1]
            out[k] = v
    return out

def split_yaml_frontmatter(text):
    """If text starts with '---\\n...\\n---\\n' return (yaml_dict, rest_text). Else (None, text)."""
    lines = text.splitlines(keepends=False)
    if not lines or lines[0].strip() != "---":
        return None, text
    for j in range(1, min(len(lines), 80)):
        if lines[j].strip() == "---":
            yaml_block = "\n".join(lines[1:j])
            rest = "\n".join(lines[j+1:])
            return parse_yaml_block(yaml_block), rest
    return None, text

def yaml_dump(d):
    lines = ["---"]
    order = ["type", "title", "aliases", "status", "created", "updated",
             "dates", "first_met", "opened", "closed", "due", "completed",
             "relation", "role", "team", "country", "city", "address",
             "project", "codename", "also_called", "kind", "companions",
             "places", "cross_refs", "my_role", "tags"]
    seen = set()
    for k in order:
        if k not in d: continue
        v = d[k]
        seen.add(k)
        if isinstance(v, list):
            if not v: continue
            lines.append(f"{k}:")
            for item in v:
                lines.append(f"  - {item}")
        else:
            sv = str(v).strip()
            if any(c in sv for c in [":", "#", "*", "&", "!", "|", ">", "%", "@", "`"]) or sv.startswith(("- ", "{", "[", '"', "'")) or sv.endswith(":"):
                sv_escaped = sv.replace('"', '\\"')
                lines.append(f'{k}: "{sv_escaped}"')
            else:
                lines.append(f"{k}: {sv}")
    for k, v in d.items():
        if k in seen: continue
        if isinstance(v, list):
            if not v: continue
            lines.append(f"{k}:")
            for item in v:
                lines.append(f"  - {item}")
        else:
            sv = str(v).strip()
            if any(c in sv for c in [":", "#"]):
                sv_escaped = sv.replace('"', '\\"')
                lines.append(f'{k}: "{sv_escaped}"')
            else:
                lines.append(f"{k}: {sv}")
    lines.append("---")
    return "\n".join(lines)

# ---- frontmatter derivation -----------------------------------------

def extract_pseudo_frontmatter(lines):
    fm = {}
    i = 0
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    consumed_until = i
    while i < len(lines):
        line = lines[i]
        if line.strip() == "":
            i += 1
            continue
        if line.startswith("## ") or line.startswith("# "):
            break
        m = PSEUDO_FM_RE.match(line)
        if m:
            k = m.group(1).strip()
            v = m.group(2).strip()
            fm[k] = v
            consumed_until = i + 1
            i += 1
        else:
            break
    return fm, lines[consumed_until:]

def infer_type_from_path(rel_path):
    if "/people/family/" in rel_path: return "person (family)"
    if "/people/friends/" in rel_path: return "person (friend)"
    if "/people/flatmates/" in rel_path: return "person (flatmate)"
    if "/people/contacts/" in rel_path: return "person (contact)"
    if "/work/companies/" in rel_path and "/people/" in rel_path: return "person (work)"
    if "/projects/" in rel_path: return "project"
    if "/tasks/active/" in rel_path: return "task (active)"
    if "/tasks/waiting/" in rel_path: return "task (waiting)"
    if "/tasks/done/" in rel_path: return "task (done)"
    if "/events/" in rel_path: return "event"
    if "/topics/" in rel_path: return "topic"
    if "/places/" in rel_path: return "place"
    if "/orgs/" in rel_path: return "org"
    if "/health/conditions/" in rel_path: return "health-condition"
    if "/health/providers/" in rel_path: return "health-provider"
    if "/home/" in rel_path: return "home"
    if "/how-to/" in rel_path: return "how-to"
    if rel_path.endswith("glossary.md"): return "glossary"
    if rel_path.endswith("README.md"): return "readme"
    if rel_path.endswith("_current.md"): return "pointer"
    if rel_path.endswith("index.md"):
        if "journal/" in rel_path: return "journal-index"
        return "index"
    if "journal/" in rel_path:
        if re.match(r"journal/\d{4}/\d{2}/\d{4}-\d{2}-\d{2}\.md$", rel_path):
            return "journal-entry"
        return "journal-index"
    return "note"

def tags_for_path(rel_path, type_field):
    tags = []
    if rel_path.startswith("memory/work/"):
        tags.append("work")
        m = re.match(r"memory/work/companies/([^/]+)/", rel_path)
        if m:
            tags.append(f"company/{m.group(1)}")
        if "/people/" in rel_path: tags.append("person")
        if "/projects/" in rel_path: tags.append("project")
        if "/tasks/" in rel_path: tags.append("task")
        if "/how-to/" in rel_path: tags.append("how-to")
    elif rel_path.startswith("memory/life/"):
        tags.append("life")
        if "/people/family/" in rel_path: tags += ["person", "family"]
        elif "/people/friends/" in rel_path: tags += ["person", "friend"]
        elif "/people/flatmates/" in rel_path: tags += ["person", "flatmate"]
        elif "/people/" in rel_path: tags.append("person")
        if "/events/" in rel_path: tags.append("event")
        if "/topics/" in rel_path: tags.append("topic")
        if "/places/" in rel_path: tags.append("place")
        if "/orgs/" in rel_path: tags.append("org")
        if "/health/" in rel_path: tags.append("health")
        if "/home/" in rel_path: tags.append("home")
    elif rel_path.startswith("journal/"):
        tags.append("journal")
    type_main = re.split(r"\s+\(", (type_field or "").strip())[0].strip()
    if type_main and type_main not in tags:
        tags.append(type_main)
    # Dedupe preserve order
    seen = set()
    out = []
    for t in tags:
        if t not in seen:
            out.append(t); seen.add(t)
    return out

def derive_yaml(rel_path, h1, existing_yaml, fm_pseudo):
    """Merge: existing YAML > pseudo > path-derived defaults."""
    out = dict(existing_yaml or {})

    # type
    if "type" not in out:
        raw = fm_pseudo.get("Type", "").strip()
        if raw:
            out["type"] = raw
        else:
            out["type"] = infer_type_from_path(rel_path)

    # title
    if "title" not in out and h1:
        out["title"] = h1

    # field translations
    pseudo_to_yaml = {
        "Also known as": "aliases", "Aliases": "aliases",
        "Status": "status",
        "Created": "created", "Updated": "updated",
        "Dates": "dates", "First met": "first_met",
        "Opened": "opened", "Closed": "closed",
        "Due": "due", "Completed": "completed",
        "Relation": "relation", "Role": "role", "Team": "team",
        "Country": "country", "City": "city", "Address": "address",
        "Project": "project", "Companions": "companions",
        "Places": "places", "Codename": "codename",
        "Also called": "also_called", "Kind": "kind",
        "Cross-refs": "cross_refs", "My role": "my_role",
    }
    for src, dst in pseudo_to_yaml.items():
        v = fm_pseudo.get(src)
        if v is not None and dst not in out:
            if dst == "aliases":
                out[dst] = [a.strip().strip("`*") for a in re.split(r",|/| or ", v) if a.strip()]
            else:
                out[dst] = v

    # tags
    if "tags" not in out:
        out["tags"] = tags_for_path(rel_path, out.get("type", ""))

    return out

# ---- link conversion -------------------------------------------------

def convert_links_in_body(rel_path, body):
    src_dir = (BOOKLET / rel_path).parent
    def md_repl(m):
        text, target = m.group(1), m.group(2)
        if target.startswith(("http://", "https://", "mailto:", "#")):
            return m.group(0)
        if not (target.endswith(".md") or "/" in target):
            return m.group(0)
        norm = normalize_link_target(src_dir, target)
        if norm is None or not norm.endswith(".md"):
            return m.group(0)
        return to_wiki_link(norm, text)
    def arrow_repl(m):
        prefix, target = m.group(1), m.group(2)
        norm = normalize_link_target(src_dir, target)
        if norm is None or not norm.endswith(".md"):
            return m.group(0)
        return f"{prefix}{to_wiki_link(norm, display_for_path(norm))}"
    def tick_repl(m):
        target = m.group(1)
        norm = normalize_link_target(src_dir, target)
        if norm is None or not norm.endswith(".md"):
            return m.group(0)
        return to_wiki_link(norm, display_for_path(norm))
    body = MD_LINK_RE.sub(md_repl, body)
    body = ARROW_PATH_RE.sub(arrow_repl, body)
    body = TICK_PATH_RE.sub(tick_repl, body)
    return body

# ---- main passes -----------------------------------------------------

def transform_file(rel_path: str):
    path = BOOKLET / rel_path
    raw = path.read_text(encoding="utf-8", errors="ignore")
    existing_yaml, rest = split_yaml_frontmatter(raw)
    lines = rest.splitlines()
    while lines and lines[0].strip() == "":
        lines.pop(0)
    h1 = None
    body_start = 0
    if lines and lines[0].startswith("# "):
        h1 = lines[0][2:].strip()
        body_start = 1
    body_lines = lines[body_start:]
    fm_pseudo, body_lines = extract_pseudo_frontmatter(body_lines)
    yaml_dict = derive_yaml(rel_path, h1, existing_yaml, fm_pseudo)
    yaml_block = yaml_dump(yaml_dict)
    body = "\n".join(body_lines).rstrip() + "\n"
    body = convert_links_in_body(rel_path, body)
    body = re.sub(r"\n## Linked from\n.*?\Z", "\n", body, flags=re.DOTALL)
    body = body.rstrip() + "\n"
    new_content = f"{yaml_block}\n\n# {h1 or Path(rel_path).stem}\n\n{body}"
    path.write_text(new_content, encoding="utf-8")

def collect_links(rel_path: str):
    text = (BOOKLET / rel_path).read_text(encoding="utf-8")
    targets = set()
    for m in WIKI_LINK_RE.finditer(text):
        target = m.group(1).strip()
        if target == rel_path: continue
        targets.add(target)
    return targets

def get_title_from_frontmatter(rel_path: str) -> str:
    """Return the file's `title:` from YAML frontmatter, falling back to display_for_path."""
    try:
        text = (BOOKLET / rel_path).read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            return display_for_path(rel_path)
        end = text.find("\n---", 4)
        if end == -1: return display_for_path(rel_path)
        yaml_block = text[4:end]
        m = re.search(r"^title:\s*(.+?)\s*$", yaml_block, re.MULTILINE)
        if m:
            t = m.group(1).strip().strip('"\'')
            if t:
                return t
    except Exception:
        pass
    return display_for_path(rel_path)

def append_backlinks(rel_path: str, sources):
    if not sources: return
    path = BOOKLET / rel_path
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"\n## Linked from\n.*\Z", "\n", text, flags=re.DOTALL)
    sources_sorted = sorted(set(sources))
    lines = ["", "## Linked from", ""]
    for src in sources_sorted:
        lines.append(f"- [[{src}|{get_title_from_frontmatter(src)}]]")
    lines.append("")
    text = text.rstrip() + "\n" + "\n".join(lines)
    path.write_text(text, encoding="utf-8")

def main(only_files=None):
    all_files = []
    for root, dirs, files in os.walk(BOOKLET):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")
                                       and "system/templates" not in str(Path(root) / d).replace(str(BOOKLET), "")
                                       and "system/scripts" not in str(Path(root) / d).replace(str(BOOKLET), "")]
        for f in files:
            if f.endswith(".md"):
                p = Path(root) / f
                rel = str(p.relative_to(BOOKLET))
                if rel.startswith("system/templates/") or rel.startswith("system/scripts/") or rel.startswith("system/skills/") or rel.endswith("/test-mv-2.md") or rel.endswith("/test-write-2.md"):
                    continue
                if p.is_symlink():
                    continue  # skip Claude Code SKILL.md symlinks; canonical is in system/skills/
                all_files.append(rel)
    auto_files = [f for f in all_files if f not in MANUAL_FILES]
    if only_files:
        auto_files = [f for f in auto_files if f in only_files]
    print(f"Pass A: transforming {len(auto_files)} files")
    for rel in auto_files:
        try:
            transform_file(rel)
        except Exception as e:
            print(f"FAIL transform {rel}: {e}", file=sys.stderr)
    print("Pass B: backlinks")
    inbound = defaultdict(set)
    for rel in all_files:
        if is_spine(rel):
            continue  # spine/TOC sources don't add semantic backlinks
        try:
            for t in collect_links(rel):
                inbound[t].add(rel)
        except Exception as e:
            print(f"FAIL collect {rel}: {e}", file=sys.stderr)
    auto_set = set(f for f in all_files if f not in MANUAL_FILES)
    for rel in auto_set:
        sources = sorted(inbound.get(rel, set()))
        append_backlinks(rel, sources)
    Path("/sessions/jolly-confident-franklin/mnt/outputs/backlinks.json").write_text(
        json.dumps({k: sorted(v) for k, v in inbound.items()}, indent=2, ensure_ascii=False))
    print("Done.")

if __name__ == "__main__":
    main()
