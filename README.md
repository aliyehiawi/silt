---
type: project-readme
title: Silt
created: 2026-04-25
updated: 2026-04-25
tags:
  - readme
  - public
  - spine
---

# Silt — A second brain that compounds over decades

A file-based memory + journal system you co-own with an AI agent. Every day you free-dump 2–10 lines about what happened; the agent parses people, places, projects, events, tasks out of it and updates a curated knowledge graph in Markdown. Open the same folder in Obsidian and you have a navigable web of everything you've worked on, lived through, and learned about — connected to itself, not to a flat index.

**Built to last 20 years.** Plain-text Markdown only. No vendor lock-in, no proprietary database, no "last-synced" fields. Leaving a job, a country, or a tool costs you zero data — every file is self-contained prose.

---

## What it does

- **Daily journaling that becomes structured memory.** Type `/journal worked on Phoenix step 3 with Sarah, prefecture appointment for the visa, called mom about summer trip` — the agent extracts five entities (Phoenix project, Sarah coworker, prefecture place, visa topic, mom person), appends one dated line to each of their files, stubs anything new, and shows you a diff before writing.
- **A real knowledge graph.** Every file uses Obsidian-style wiki-links with explicit display aliases. Open the vault in Obsidian's graph view and you see clusters of real relationships — the trip ↔ the people on it ↔ the city, the project ↔ its team ↔ its dependencies, family ↔ shared events. **Index files don't dominate the graph** — they're tagged `#spine` and filtered out so what you see is meaningful, not TOC noise.
- **Tasks as files, not lines.** Each task gets its own Markdown file with a description and a dated log. Over years, `tasks/done/` becomes a browseable record of exactly what you shipped — the raw material for your CV in your own words.
- **Decodes your shorthand.** A two-tier memory (hot cache + full tree) lets the agent translate "ask todd about the PSR for phoenix" → "ask Todd Martinez (Finance lead) about the Pipeline Status Report for Project Phoenix (Q2 launch)" without you ever spelling it out twice.
- **External sources are inputs, not pointers.** Wiki and chat connectors (Notion, Slack, etc.) feed the local tree but nothing from them is stored — no URLs, no IDs, no "last synced". Lose access tomorrow and your local memory is unaffected.

---

## Why it's different from a notes app

| | Typical notes app | Silt |
|---|---|---|
| Storage | Proprietary DB or sync service | Plain Markdown in git |
| Cross-references | Manual links, easily stale | Path-based wiki-links + auto-regenerated `## Linked from` footers |
| Graph | Optional plugin, often messy | First-class — every file is a graph node, with a hard rule against TOC-shape |
| Tasks | Separate todo app | One file per task with full history |
| Daily entry | A blank page | Free dump → structured cross-files automatically |
| Export | Maybe | It's already files. There's nothing to export. |
| Decade-scale | Untested | Designed for it |

---

## Who it's for

- People who've used apps like Roam, Logseq, Obsidian, Notion, Bear, Apple Notes — and felt the system collapse over time as cross-references rotted and the graph became a TOC-around-an-index instead of a real web.
- People who switch jobs / countries / tools and don't want to lose their record each time.
- Engineers and writers who already think in Markdown.
- Anyone who wants an AI agent to compound *with* them over years rather than starting from a blank context every conversation.

---

## How it works (one minute)

```
You type:        /journal worked on phoenix with sarah, prefecture for visa, called mom

Agent does:      1. Append raw text to journal/2026/04/2026-04-25.md (immutable)
                 2. Parse → 5 entities (3 known, 2 new stubs proposed)
                 3. Show diff:
                      + memory/work/{co}/projects/phoenix.md       (+1 log line)
                      + memory/work/{co}/people/sarah.md           (+1 log line)
                      + memory/life/places/prefecture.md           (+1 log line)
                      + memory/life/topics/visa-renewal.md         (new stub)
                      + memory/life/people/family/mom.md           (already exists, +1 line)
                    Apply? [y/n/edit]
                 4. On `y`: writes everything, runs the transform script, commits to git
                 5. Each Log line cross-links the other entities mentioned that day,
                    so the graph reflects "Phoenix-with-Sarah-on-2026-04-25" as a real edge.
```

After 30 days you have a connected web. After 5 years it's a second brain you can grep.

---

## Features at a glance

**Skills (workflows)** — five tool-agnostic Markdown `SKILL.md` files (one per workflow folder at the repo root) that any AI coding agent can read and follow:

- `/journal` — daily free-dump → structured cross-files (default workflow).
- `/start` — first-run setup; optional graph-aware Notion/Confluence scrape that produces a connected graph from day one.
- `/update` — weekly task sync from your wiki, plus an audit that flags drift in the graph.
- `task-management` — file-based tasks with a `TASKS.md` dashboard view.
- `memory-management` — the two-tier memory architecture; how the agent decodes your shorthand.

**Maintenance scripts** — three Python scripts in `system/scripts/` that keep the graph clean:

- `transform.py` — idempotent, runs after every journal entry. Normalizes YAML frontmatter, refreshes wiki-links, regenerates `## Linked from` sections across the whole vault.
- `audit.py` — read-only diagnostic. Reports orphans, half-connected files, missing frontmatter per subgraph (life people, work projects, events, …). Run weekly via `/update`.
- `repair_links.py` — fixes broken wiki-links after file moves.

**Conventions** — documented once in `memory/README.md` § "Graph convention", four rules:

1. YAML frontmatter on every file (`type`, `title`, `created`, `updated`, `tags`).
2. Path-based wiki-links: `[[memory/work/companies/{co}/people/sarah.md|Sarah]]`.
3. Auto-generated `## Linked from` footer.
4. **Link entities to each other, not just through TOCs.** This is what makes the graph mean something.

---

## Getting started

### 1. Clone

```bash
git clone <this-repo> ~/silt
cd ~/silt
```

### 2. Pick your AI agent

Any agent that reads `AGENTS.md` will work — Claude Code (via the symlinked `CLAUDE.md`), Codex CLI, Cursor, Windsurf, etc. The skills are written to be tool-agnostic.

For Codex CLI, link the skills as slash commands once per machine:

```bash
mkdir -p ~/.codex/prompts
for s in journal start update task-management memory-management; do
  ln -sf "$(pwd)/$s/SKILL.md" "$HOME/.codex/prompts/$s.md"
done
```

For Claude Code, just open the folder and the symlinked `CLAUDE.md` auto-loads.

### 3. Bootstrap

In your agent's chat:

```
/start
```

Three short questions (name, city, role), then optionally hand it your company wiki home page for a one-time scrape. Result: a populated `memory/` tree with people, projects, glossary, and your past tasks — fully cross-linked.

### 4. Daily ritual

```
/journal a few sentences about today
```

That's it. The agent does the rest. Run weekly:

```
/update
```

To sync new tasks, pick up new chat-discovered teammates, and run the health-check audit.

### 5. Open in Obsidian (optional but recommended)

**First, copy the canonical Obsidian config** so the graph view filter and link conventions are set up correctly:

```bash
bash system/scripts/setup-obsidian.sh
```

This copies `system/.obsidian-defaults/{graph,app}.json` into your local `.obsidian/` folder. Both are **git-ignored** by design — your local play with the graph view (zoom, color groups, panel layout) won't show as git changes anymore.

Then point Obsidian at the folder. The graph view, backlinks pane, and quick-switcher all just work. The shipped config filters out spine files (CLAUDE.md, indexes, SKILL files) from the graph view so you see meaningful relationships, not pointer-file noise.

**Why some files look "modified" when you didn't edit them.** When you open a markdown file from Obsidian, the OS / file explorer / Obsidian's own pane may flag it as "modified" because the file's mtime (modification timestamp) updated. **That's not a git change** — it's filesystem metadata. Run `git status` to confirm: if no files appear, nothing will be committed and auto-push is safe. The `.gitignore` shipped with the kit excludes every UI-state file Obsidian writes (workspace, cache, theme, plugin state, graph layout, app prefs), so committable churn from opening / browsing the vault is zero.

---

## What's in the box

```
silt/
  AGENTS.md             ← entry-point hot cache (symlinked from CLAUDE.md)
  README.md             ← this file
  TASKS.md              ← thin dashboard over your task files

  system/               ← portable system files (the "kit")
    skills/             ← 5 SKILL files (one per workflow)
    scripts/            ← transform.py, audit.py, repair_links.py + tests
    docs/               ← architecture spec + graph convention
    templates/          ← starter shells for new entities
    version.md          ← convention version

  memory/               ← your curated knowledge base
    me.md               ← identity + milestones
    glossary.md         ← cross-domain decoder
    all-entities.md     ← master TOC
    work/companies/{co}/  people, projects, tasks, glossary, how-tos
    life/               family, friends, events, places, topics, health, home

  journal/              ← immutable daily log
    YYYY/MM/YYYY-MM-DD.md
    YYYY/MM/YYYY-MM.md   ← month overview
    YYYY/YYYY.md         ← year overview
    all-time.md

  .obsidian/            ← Obsidian config (graph filter for #spine)
```

---

## Privacy

This vault contains personal data — names, addresses, employer details, sometimes health information. **Nothing in this system encrypts your data.** Treat the folder like a private journal:

- Don't push to a public git remote.
- Use a private repo for sync, or rely on your usual file-sync (Dropbox, iCloud, Syncthing).
- Add anything you want excluded from git to `.gitignore` (the `.obsidian/workspace.json` file is a good default — it tracks UI state).
- Don't journal credentials or keys. Journal "I rotated my AWS key" — not the key itself.

---

## Status & roadmap

This is a personal-productivity research project. It's been used in production by its author since early 2026 and the conventions have stabilized. The 5 skills + 3 scripts are battle-tested on a vault of ~120 entities and ~1,200 wiki-links.

**Working today:**
- All 5 skills, all 3 scripts, full graph audit
- Obsidian + Claude Code + Codex CLI integration
- 4-rule graph convention with mechanical enforcement

**Roadmap / known gaps:**
- Multi-language slug support (currently Latin-only filenames work best)
- Attachments convention (photos / receipts / voice notes — markdown only today)
- Tested only with Claude Code and Codex CLI; Cursor / Windsurf / others should work but aren't validated
- Test suite for scripts is included but coverage is intentionally narrow (regex / IO sanity)
- No migration tooling between convention versions yet (handled manually for now)

See `system/version.md` for the convention's version history.

---

## Inspirations

Roam Research's bidirectional links. Andy Matuschak's evergreen notes. Tiago Forte's Building a Second Brain. Linus Lee's experimental knowledge tools. Obsidian's graph view. The simple idea that **plain Markdown in git outlives every notes app**.

---

## License

Choose your own — the system is just Markdown files and ~600 lines of Python. No external runtime dependencies beyond Python 3.8+ stdlib.
