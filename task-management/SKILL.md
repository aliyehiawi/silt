---
name: task-management
description: File-based task management with graph convention — one file per task under work/companies/{co}/tasks/, with TASKS.md as the dashboard-index view. Reference this when the user asks about their tasks, wants to add/complete tasks, or needs help tracking commitments.
user-invocable: false
type: skill
tags:
  - skill
  - graph
  - tasks
  - spine
---

# Task Management

Tasks are **files**, not lines. Each task gets its own markdown file with YAML frontmatter, Description, and a dated Log. `TASKS.md` at the repo root is a thin dashboard pointing to the files. Over years, the `tasks/done/` folder accumulates a dated record of exactly what you shipped — the raw material for your CV.

## File Locations

**Task files** live under the current company's folder:

```
memory/work/companies/{co}/tasks/
  active/{slug}.md           # currently working on
  waiting/{slug}.md          # blocked on someone else
  done/{YYYY-MM-slug}.md     # shipped — year-month prefix for chronological sort
  done/archive/{YYYY}/       # done tasks older than ~2 years, rolled up by year
```

**`TASKS.md`** lives at the repo root (same dir as `CLAUDE.md`). It's the dashboard view:

```markdown
# Tasks

## Active
- [ ] **[[memory/work/companies/{co}/tasks/active/phoenix-cutover-runbook.md|Write Phoenix cutover runbook]]** — due 2026-05-01

## Waiting On
- [ ] **[[memory/work/companies/{co}/tasks/waiting/review-onboarding-rfc.md|Review onboarding RFC]]** — waiting on Maya

## Someday

## Done (last 30 days)
- [x] ~~[[memory/work/companies/{co}/tasks/done/2026-04-phoenix-step-3.md|Phoenix step 3]]~~ (2026-04-20)
```

Rules:
- TASKS.md contains **only wiki-link pointers** to task files. Never duplicate description content.
- All internal links in TASKS.md must use wiki-link format: `[[path|Display]]`
- Tasks older than 30 days in Done roll off TASKS.md (the files stay in `tasks/done/` forever).
- TASKS.md is regenerated from the task files on demand — it's a view, not a source of truth.

## Task File Format

Every task file, regardless of status:

```markdown
---
type: task (active)
title: Phoenix cutover runbook
status: active (as of 2026-04-25)
project: phoenix
created: 2026-04-18
due: 2026-05-01
updated: 2026-04-25
tags:
  - work
  - company/wiremind
  - task
---

# Phoenix cutover runbook

## Description

Write the runbook for the Phoenix system cutover. Covers pre-cutover checks, cutover steps, rollback procedures, and post-cutover validation. Target audience: ops team and on-call engineers. Coordinate with Sarah (infrastructure) for rollback procedures and review sign-off.

## Log

- 2026-04-18 — picked up, outlined approach
- 2026-04-20 — drafted the runbook skeleton, blocked on Sarah's rollback sign-off
- 2026-04-22 — sign-off received, added rollback section
- 2026-04-24 — review round 1 done, 2 small fixes requested
- 2026-04-25 — shipped, merged
```

The `## Log` section is append-only. It grows as `/journal` entries reference the task. Never rewrite past log lines.

## Slug Rules

- Lowercase, hyphen-separated, ASCII: `phoenix-cutover-runbook.md`
- Active / waiting: `{slug}.md` (no date prefix — title alone identifies it)
- Done: `{YYYY-MM}-{slug}.md` — year-month of completion, so `ls done/` sorts chronologically
- Archive: `done/archive/{YYYY}/{YYYY-MM}-{slug}.md`

When in doubt, be more specific. `fix-api-race.md` is fine; `fix.md` is not.

## Lifecycle — Status Changes Are Moves

Status changes are file moves, not silent field edits. The move leaves a trail.

**Every lifecycle action below is previewed before it runs**, per [[memory-management/SKILL.md|Memory Management Skill]] § Universal preview rule. That includes file moves, Log-line appends, TASKS.md edits, and task-file creations. The user sees `Apply? [y / n / edit]` and nothing writes until they answer `y`.

| Change | What to do |
|---|---|
| Pick up a new task | Create `tasks/active/{slug}.md` with Status: active (as of today), Created: today. Append line to TASKS.md using wiki-link format. |
| Task blocked on someone | Move `active/{slug}.md` → `waiting/{slug}.md`. Bump Updated:. Append Log line: `YYYY-MM-DD — waiting on {person} for {reason}`. Update TASKS.md section. |
| Unblocked | Move back to `active/`. Log line: `YYYY-MM-DD — unblocked, resumed`. |
| Shipped | Move to `done/`, rename to `{YYYY-MM}-{slug}.md`, set Completed: today. Append Log line: `YYYY-MM-DD — shipped`. Move TASKS.md line to Done section with strikethrough. |
| Cancelled | Move to `done/`, rename to `{YYYY-MM}-{slug}.md`, set Completed: today. Log line: `YYYY-MM-DD — cancelled: {reason}`. Status: `task (cancelled)`. Still archived — you still did work thinking about it. |
| Archive old done | Files older than ~2 years → `done/archive/{YYYY}/`. Done during quarterly maintenance. |

Never delete a task file. Even cancelled ones stay — they're part of your work history.

## How to Interact

All write paths below go through the universal preview → confirm → write gate. Reads are free; writes always show the diff first.

**When user asks "what's on my plate" / "my tasks":** (read-only, no preview needed)
- Read TASKS.md Active + Waiting sections
- For each line, optionally open the pointed-to file for more detail
- Highlight anything overdue (compare Due against today)

**When user says "add a task" / "remind me to X":**
- Build the proposed new file `tasks/active/{slug}.md` with Title, Status: active (as of today), Created: today, YAML frontmatter
- Build the proposed wiki-link pointer line for TASKS.md Active section
- Show preview: `Proposed: + tasks/active/{slug}.md (new), TASKS.md (+1 line). Apply? [y/n/edit]`
- On confirm, write both

**When user says "done with X" / "finished X":**
- Find the task file (fuzzy match on title across `active/` and `waiting/`)
- Propose: move to `tasks/done/{YYYY-MM}-{slug}.md`, set Completed: today, append Log line `YYYY-MM-DD — shipped` (or user's summary), move TASKS.md line to Done section with strikethrough + date
- Show preview and ask `Apply? [y/n/edit]`
- On confirm, write; then offer: "Add a final summary to the Description?"

**When user says "pause X" / "waiting on Y for X":**
- Propose: move task file from `active/` to `waiting/`, append Log line `YYYY-MM-DD — waiting on {who}: {why}`, move TASKS.md line to Waiting On section
- Show preview and ask `Apply? [y/n/edit]`
- On confirm, write

**When user says "what am I waiting on":**
- List TASKS.md Waiting On section
- For each, note how long it's been waiting (since the last Log line's date)

**When user asks "what did I ship last month" / CV-style query:**
- `ls memory/work/companies/{co}/tasks/done/2026-03-*.md`
- Read each file, pull Title + Description + last Log line
- Present as a list the user can copy into a CV bullet

## Conventions

- **Bold** the task title in TASKS.md for scannability
- Task title in the file `# Header` matches the slug (human-readable version)
- Include `project:` in YAML when the task relates to a project (creates the cross-ref)
- Include `due:` for deadlines — plain ISO date, no "due X days"
- Keep Description scoped to the task. Related context (meetings, decisions) belongs in the Log or the project file
- Sub-bullets under a Log line are fine for nested detail on a single day

## Extracting Tasks

When summarizing meetings, chat threads, or conversations, offer to create task files for:
- Commitments the user made ("I'll send that over")
- Action items assigned to them
- Follow-ups they mentioned

Always ask — don't auto-create. Each added task becomes a file, not just a line.

## What This Skill Does NOT Do

- Does not mirror external task sources. Tasks from the wiki (Notion etc.) are pulled in by `/productivity:update` and *written* as local files with plain Description — no links, no IDs, no external pointers.
- Does not delete tasks. Cancelled / mistaken tasks are marked and archived, not removed.
- Does not rewrite Log lines. Appends only.

## Dashboard Setup (First Run)

A visual dashboard is available for managing tasks and memory. **On first interaction with tasks:**

1. Check if `dashboard.html` exists in the current working directory
2. If not, create it in the current working directory
3. Inform the user: "I've added the dashboard. Run `/productivity:start` to set up the full system."

The dashboard reads TASKS.md and shows the wiki-link pointer view. Clicking a task opens the underlying task file.

## Graph Convention

Every file written by this skill follows the vault's Obsidian-style graph convention: YAML frontmatter at top, path-based wiki-links for cross-references (`[[path|Display]]` — never `[Text](path.md)`), `## Linked from` footer regenerated by the transform script. Full spec in [[memory/README.md|Memory README]] § "Graph convention".

## Transform Script

After a batch of writes, run `python3 system/scripts/transform.py` from the workspace root to normalize frontmatter, refresh wiki-links, and regenerate the `## Linked from` sections across the vault. The script is idempotent — safe to run anytime.

## Linked from

- [[CLAUDE.md|Working Memory]]
- [[journal/SKILL.md|Journal Skill]]
- [[memory-management/SKILL.md|Memory Management Skill]]
- [[memory/README.md|Memory README]]
- [[start/SKILL.md|Start Skill]]
- [[update/SKILL.md|Update Skill]]
