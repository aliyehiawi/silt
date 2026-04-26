---
type: readme
title: Memory Architecture
created: 2026-04-24
updated: 2026-04-26
tags:
  - readme
  - architecture
  - graph-convention
  - spine
---

# Memory Architecture

> **TL;DR for any agent reading this file fresh:**
>
> - **Two views.** [[journal/SKILL.md|journal/]] = immutable daily log (what happened). [[memory/README.md|memory/]] = curated entity files (what's true now), each with a dated `## Log`.
> - **This is an Obsidian-style knowledge graph.** Every cross-reference is a path-based wiki-link. Every file has YAML frontmatter. Every file ends with a `## Linked from` section listing inbound references. Full spec below in § "Graph convention".
> - **Every line dated.** Every file has `created:` + `updated:` (in frontmatter). Every Log line starts `- YYYY-MM-DD — ...`. Every time-sensitive fact has `(as of YYYY-MM-DD)`. No exceptions.
> - **Entity routing.** Person → `work/companies/{co}/people/` (work) or `life/people/{family,friends,flatmates}/` (life). Place → `life/places/`. Org → `life/orgs/`. Event → `life/events/{YYYY-name}.md`. Ongoing matter → `life/topics/{name}.md`. Health provider → `life/health/providers/`. Self-state obs → `life/health/log.md`.
> - **`me.md` is a slow file.** Identity + current state + milestones. Only updates on current-state change or user-confirmed first-time milestone. Never touched by regular days.
> - **Tasks are files, not lines.** Each task lives at `work/companies/{co}/tasks/{active,waiting,done}/{slug}.md` with its own Description + dated Log. `TASKS.md` is the dashboard view.
> - **External sources are ephemeral inputs.** Wiki and chat feed the local tree but never get stored — no URLs, no IDs, no "last synced" fields. Leaving the company costs zero local data.
> - **Inferred vs user-provided.** The agent parses and routes what *you wrote*. It never invents traits, feelings, or motives.
> - **Archival, never delete.** `status: archived` in frontmatter + move to `archive/` subdir. Full history always recoverable.
>
> Workflow contract is [[journal/SKILL.md|journal/SKILL.md]]. That's the workflow that writes into this shape. This file defines the shape itself.

---

## Graph convention (Obsidian-compatible)

Everything in this vault is a node in a knowledge graph. Three rules govern what gets written, and **all skills (start, update, journal, task-management, memory-management) honor these rules**.

### Rule 1 — YAML frontmatter at the top of every `.md` file

```yaml
---
type: <type>                       # required, see "Type values" below
title: <H1 title>                  # the human name; should match the # heading
aliases:                           # optional, only if the entity has nicknames
  - <alias 1>
  - <alias 2>
status: active (as of YYYY-MM-DD)  # active | past | archived | etc.
created: YYYY-MM-DD
updated: YYYY-MM-DD
# Type-specific extras (any subset of):
relation: <family | friend | coworker | …>
role: <text>
team: <slug>
country: <name>
city: <name>
project: <slug>
codename: <name>
dates: YYYY-MM-DD to YYYY-MM-DD
companions: <comma-list>
places: <comma-list>
opened: YYYY-MM-DD
closed: YYYY-MM-DD
due: YYYY-MM-DD
completed: YYYY-MM-DD
kind: <project | process | learning | life-matter>
tags:                              # auto-derived from path + type
  - <tag 1>
  - <tag 2>
---
```

- `type` is required. It drives default tags and the file's role in the graph.
- `tags` are auto-derived from the file's path and its type. Don't hand-edit them; the transform script regenerates them.
- All time-sensitive fields live in frontmatter (status, created, updated, dates). The `(as of YYYY-MM-DD)` suffix on `status` is preserved.
- Don't keep the old `**Type:** ...` style key/value lines in the body — those move into frontmatter.

### Rule 2 — Path-based wiki-links for every cross-reference

Format: `[[<path-from-vault-root>|<display>]]`

Examples:

- `[[memory/work/companies/wiremind-cargo/people/mathilde-bleu.md|Mathilde Bleu]]`
- `[[memory/life/events/2024-08-motorcycle-accident.md|motorcycle accident]]`
- `[[memory/work/companies/wiremind-cargo/projects/pythie-cargo.md|Pythie-cargo]]`
- `[[TASKS.md|TASKS]]` (root-level files use just the filename)

Rules:

- **Path is from the vault root** (where `CLAUDE.md` lives). Always include the `.md` extension. This makes Obsidian, file managers, and grep all happy.
- **Always include a display alias** (`|Display`). The alias is what the reader sees in prose; the path is the graph edge.
- **Use wiki-links instead of**: `[Display](relative/path.md)`, `→ relative/path.md`, `'memory/path.md'`, `../people/sarah.md`, etc.
- When mentioning an entity in prose for the first time in a section, prefer wiki-link form. Subsequent mentions in the same paragraph can drop the link.
- **External URLs stay as standard markdown links** (`[Excalidraw](https://...)`) — only internal cross-references become wiki-links.

### Rule 3 — Every file ends with a `## Linked from` section

Lists every other file that links TO this file (inbound references). Format:

```markdown
