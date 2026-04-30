---
type: note
title: founding-essay
tags:
  - note
---

# founding-essay

> **Silt is a second brain that compounds over decades, as plain Markdown files you own.**
>
> Five SKILL files for your AI coding agent (Claude Code, Codex, Cursor, Windsurf) — no app, no cloud, no account. Three you call directly:
>
> - **`/start`** — one-time bootstrap. Optionally scrapes your company's Notion / Confluence / Google Docs wiki, classifies every page (project / person / glossary / skip), and writes a fully cross-linked company graph to your disk in minutes. The intuition most engineers spend three months building, on day one.
> - **`/journal`** — daily ritual. Type 2–10 free-form lines about what happened; the agent parses people, places, projects, tasks, and events, cross-files dated log lines into the right files, *and links every entity to every other entity it actually relates to*. The trip file links to the people on it; each person links back to the trip; the project links to the task; the task links to the teammate. Every write is previewed as a diff (`Apply? [y/n/edit]`) — nothing happens silently.
> - **`/update`** — weekly sync. Pulls this week's tasks from your wiki, picks up new teammates discovered in chat connectors, audits the graph for drift and broken links.
>
> Two more skills work behind the scenes. **`task-management`** turns each task into its own Markdown file with full history — over years, `tasks/done/` becomes a browseable record of exactly what you shipped, the raw material for your CV in your own words. **`memory-management`** is a two-tier memory (hot cache + full tree) that lets the agent decode your shorthand: *"ask Todd about the PSR for Phoenix"* → *"ask Todd Martinez (Finance lead) about the Pipeline Status Report for Project Phoenix"* without you spelling it out twice.
>
> **The graph self-heals.** Three Python scripts keep it clean — `transform.py` regenerates wiki-links and `## Linked from` backlink footers after every entry, `audit.py` flags orphans and drift weekly, `repair_links.py` fixes references after file moves. Index files are tagged `#spine` and filtered out of the graph view, so what you see is meaningful relationships, not TOC noise — *a web, not a star around an index*.
>
> Every file is plain Markdown with path-based wiki-links — so the folder opens as a real, navigable knowledge graph in **Obsidian, Logseq, Foam, or any wiki-link-aware editor**, with no import step and no proprietary format. Or skip the graph view entirely and just `grep` the folder. Both work because the substrate is the same files.
>
> **External scraped sources are inputs, not pointers.** Wiki and chat connectors feed your tree, but nothing from them is stored — no URLs, no message IDs, no "last synced" fields. Lose Notion access tomorrow and your local memory is unaffected.
>
> After a year, *"what papers did I submit at the prefecture?"* or *"what was I working on with a colleague in March?"* answer themselves in five seconds. The folder lives on your laptop — back it up however you want (private git, iCloud, encrypted disk, or nowhere at all). When you leave the job, the country, or the platform, the folder comes with you unchanged. Open source under MIT — [github.com/example/silt](https://github.com/example/silt).
>
> *Below: why I built it, after three notes-app graveyards in six years.*

---

# I left a job after three years and lost everything I had learned

When I packed my last desk at the company I'd worked at for three years, I assumed I was carrying my work with me. Three years of decisions, three years of conversations, three years of "this is how we ship to that client without breaking the other one." It was in my head, but it was also — I thought — in my notes app.

Two weeks into the new job, someone asked me a question I had answered cleanly a year before. I knew I had answered it. I had even written it down somewhere. I went looking.

It was gone.

Not literally gone. The note still existed somewhere in my old account. But "the place where Todd's PSR escalation logic lives" was fused to a workspace I no longer had access to, an app whose URL my browser had stopped autocompleting, a tag system whose mental model had decayed the moment I stopped maintaining it. The information existed and was inaccessible to me. That's the same as gone.

This wasn't the first time. It was the third.

Every two or three years, I move countries, jobs, or both. Every time, the same pattern: a notes system I was sure would carry me forward turns into a graveyard the moment my context shifts. Roam Research workspaces I no longer log into. Notion databases inside companies I no longer work for. Apple Notes that survive but were never structured to begin with. Obsidian vaults that I started clean three times because the previous one had become a TOC pointing at empty pages.

After the third time, I stopped blaming the apps and started looking at what was actually breaking.

## What actually breaks

The breakage is structural. It's not "the app got worse" — most of these apps are excellent. The breakage is that almost every notes system in 2026 makes three assumptions that turn out to be wrong over decades:

**One: the graph builds itself.** Every notes app sells you on bidirectional links. The pitch is: just type, the graph emerges. What actually happens is that you type, and three months later you have a thousand notes that all link to a single index file called "Projects" or "People." Open the graph view and you see a star, not a web. The graph view is the most brutally honest diagnostic in any notes app — it shows you exactly how connected your knowledge isn't.

**Two: maintenance is free.** Cross-references rot the second you rename a file. Tags drift. The taxonomy you set up at month one stops fitting your life by month six. You either spend Sunday afternoons doing maintenance or you let entropy win, and entropy always wins.

**Three: the app survives the user.** It does not. The moment you leave the job, the country, the platform, or the laptop, you find out exactly how much of your second brain was actually in the app's database and not on your hard drive.

The combination of these three is what turns notes apps into graveyards. Not bad apps. Bad assumptions.

## What I built instead

After the third graveyard, I sat down to figure out what I actually wanted. Stripped to the bone, it was four things:

I wanted my notes to be **plain Markdown files in a folder**. Nothing else. No database, no proprietary format, no sync service. If I leave the next job in 2029 or the next country in 2031, the folder comes with me unchanged. If I never want to open a graph view, the files still grep, still open in any text editor, still survive every notes app dying.

I wanted a **graph that's optional but real when I want it**. Not a star around an index. A web of files where the friend's file links to the events they were in, where the project links to the people who own it, where the trip links to the city. I want it there when I'm exploring; I don't want to be paying for it when I'm not.

I wanted to **write once and have it cross-file itself**. The reason every system I've used eventually rotted is that maintenance was always pushed onto me. I had to remember to update the project page when I journaled about a meeting. I had to remember to add the tag. I had to do the bookkeeping. So I stopped, and the system rotted. What I wanted was to dump three sentences about my day and have those three sentences become five log lines on the right entity files automatically — without me thinking about it.

I wanted **the AI to be the parser, not the vault.** The AI agent should read what I wrote, route it, write it as plain text into the right files, and stay out of the storage layer. The vault is files I can open in Obsidian or `cat` from the terminal. The agent is an assistant that maintains it, not a service that owns it.

These four shapes — file-based, graph-optional, parsed-not-typed, AI-as-parser — turned into the system I now run my life on.

I named it Silt.

## Why it's called Silt

Silt is what builds quietly. River sediment, the kind that takes a hundred years to accumulate into something solid you can walk on. Each daily journal entry is a grain. After a week, you have nothing visible. After six months, you have a connected substrate you can stand on. After five years, you have a record you couldn't reproduce by trying.

The name is also a warning to my future self. I won't get to walk on the silt I deposit today. Future-me will. The discipline is to keep depositing without expecting an immediate payoff — the same discipline that ruins most journals after week three.

## What recovering an old detail feels like

The graph view is what people screenshot. The thing that actually changed my life is more boring: the moments when I needed something from my own past and got it back in five seconds.

A few weeks ago I was writing a request for a recommendation letter from a professor I had four years ago. I could see his face. I could not for the life of me remember his name. Pre-Silt, that's a dead end — the email I sent them lives in an old university account I no longer have access to. Now: two queries against the journal. Found the person on the second one, where I'd written "office hours with [name] about the project." The letter went out the same hour.

Last month I needed to update my CV with what I actually shipped in 2023. Two and a half years ago. I have always been bad at this — the work blurs together once it's done, and the version of me writing the CV is not the version of me who wrote the code. Pre-Silt, I would have stared at the bullet "shipped X improvements to Y" and produced something vague. Now I have 600 daily journal entries from that period, all dated, all cross-linked to the projects and people involved. The bullets wrote themselves out of three short queries.

Last week I needed the date I applied for my French residence permit and the exact list of papers I submitted. The renewal is coming up in six months and I want the same documents ready. Pre-Silt, that's a panic search through old emails and a folder on a hard drive I don't backup. Now: open [[memory/life/topics/titre-de-sejour.md|Titre De Sejour]], scroll the Log section, every appointment, every document, every prefecture interaction is dated and listed.

And — the one I use most often — looking up things I was thinking three years ago. The plan I sketched for a project I never shipped. The constraints I'd identified before they became obvious to everyone else. The conversations I had about it with people whose names I'd otherwise have forgotten. There's something specific that happens when you can read your past self's actual notes — not the reconstructed memory you have, the actual notes, dated, in your own words. It's the closest thing to time travel I've found.

These are the recoveries that compound. They don't show up in the graph view. They show up when life asks me a specific question about my own past and the folder has the answer.

## How it actually installs

I want to be concrete about how Silt arrives in your workflow, because it's smaller than it sounds.

Silt ships as **five SKILL files for an AI coding agent**. If you already use Claude Code, Codex CLI, Cursor, or Windsurf — you're already running an agent that reads `AGENTS.md` and slash-command-style skill prompts. Silt is just five of those, plus a folder convention. There's no app to install, no service to sign up for, no daemon to run. You drop the files in, your agent reads them on the next prompt, and you type slash commands.

- `/start` — first-time setup. Three short questions, then **optionally a one-time scrape of your company's Notion / Confluence / Google Docs wiki**. The skill walks every reachable page, classifies it (project / person / glossary / past task / handbook-skip / confidential-skip), proposes a write plan, and on `y` writes a fully cross-linked company sub-tree to plain Markdown on your disk. Day one, you have a graph that takes most engineers a year to fail to build.
- `/journal` — the daily ritual. Free-dump 2–10 lines, the agent parses entities, shows you a diff, commits on `y`. The cross-filing is automatic.
- `/update` — weekly. Pulls this week's tasks from your wiki, picks up new teammates discovered in chat connectors, runs the audit, flags drift in the graph.
- `task-management` — file-based tasks (one Markdown file per task, full history). `TASKS.md` is a thin dashboard view.
- `memory-management` — the two-tier memory (hot cache + full tree) that lets the agent decode shorthand without making you spell it out twice.

The `/start` connector scrape is the sneaky-magic part. Most engineers join a new company and spend two or three months building intuition by pattern-matching across Slack threads and stale wiki pages. `/start` does that pattern-matching once, in your terminal, in a few minutes, and writes the result to plain Markdown that's yours forever. When you leave the company — and you will leave — the local memory is unaffected. The wiki could go offline tomorrow and your file tree wouldn't notice.

That's the whole install. Five files into your agent's folder, one slash command to bootstrap, one slash command per day after that.

## What it looks like in practice

Today is a Sunday in April 2026. I just opened my terminal, typed two sentences:

```
/journal sunday run with Sam, dress fitting confirmed for the wedding,
helix component library v3 primitives are ready for review
```

My agent did six things in the next four seconds:

It dropped the raw line into today's journal file (immutable record of what I said). It identified five entities — my running partner, my mother, my sister's wedding, a client project, a specific task. It opened my running partner's file and added one dated log line. It opened the wedding event file and added another. It opened the project file and the active task file and added log lines on each. It showed me the diff. I typed `y`. Three seconds later all six files were updated, the cross-references were live, and the entry was committed to git.

In six months I have ~150 daily entries and forty-five entity files. Each entry took less than a minute to write. The system did the cross-filing.

## The graph is just one way in

There's a knowledge graph because the wiki-links between files form one. If I open the folder in Obsidian, I can scroll the graph view and see clusters — the trip-with-colleagues cluster, the apartment-hunt cluster, the work-project cluster. It's beautiful and useful when I'm exploring.

But the graph is layered on top. Underneath it is just a folder of files.

If I never open the graph view, the files still answer questions. `grep -r "PSR escalation" memory/` returns the line. The file [[memory/life/topics/titre-de-sejour.md|Titre De Sejour]] opens in TextEdit and reads as a normal document. I can `cat memory/life/people/family/partner.md` from a terminal on a flight in 2031 and see exactly what I wrote about her in 2026, dated, with the cross-references intact.

That's the durable contract. The graph is a feature; the files are the product. Different humans want different access paths — some scroll graph views, some grep, some open files in a markdown editor and read top-to-bottom, some build their own queries. All of those work because the substrate is just plain Markdown.

This matters because future-me's tools are going to be different from today-me's tools. The graph view I use today might not exist in 2036. The agent I use today might be replaced. The folder will still be a folder.

## Your data, your machine, your choice

There's no Silt cloud. There's no account. There's no sync service that owns your files. The folder lives on your laptop and goes wherever you take it.

Where you want it backed up is your call:

- **Local-only.** The folder lives on your hard drive and nowhere else. No one — not even me, the author — can see it. If you want a second brain that no service can ever index, this is the default. Most users probably want this for the personal files (health log, family, journal) and never push them anywhere.
- **A private git remote.** GitHub private repo, Gitea, GitLab self-hosted, a private Forgejo instance. Sync between your machines and have a backup, but you're the only one who can read it. This is what I do.
- **Disk sync, no git.** Drop the folder in iCloud Drive, Dropbox, Syncthing, a Time Machine backup. Same files, no git history. Works fine if you don't care about commit history but want sync.
- **Encrypted disk.** Put the folder on a FileVault disk, on an encrypted external drive, inside a VeraCrypt container. The files are still plain Markdown — just behind an encryption layer.

You can also mix and match. My setup: the work tree is in a private git repo so I can sync between my laptop and my work machine. The most-personal sub-tree (`memory/life/health/`) is git-ignored and stays on my laptop only. Different files, different storage, same vault.

The point is: privacy is a property of where the files live, not of the tool. Silt doesn't ship with encryption because Silt doesn't ship with storage. You decide the privacy model. Nothing in the system phones home, has telemetry, or knows you exist.

## What I lost when I left, and what I won't lose again

I'm going to leave this employer too. Probably in a year or two. Probably for another country. The pattern doesn't change.

What changes is that this time, when I close the laptop on the last day, I am closing it on a folder that I wrote and I own. The cross-references work because the wiki-links use real paths, not internal database IDs. The graph view works because it reads the files. The agent works because the prompts are part of the repo, not part of a service. If every server in the world disappeared tonight, the folder would still open in any text editor on any laptop and tell me what I worked on, who I worked with, and what I learned.

I don't think this is the right system for everyone. It assumes you are willing to have a folder. It assumes you are willing to type a free-form sentence about your day at least three days a week. It assumes you have an AI agent in your terminal — Claude Code, Codex, whatever you use — and you don't mind that the agent is the interface. If those three things are alien to you, this isn't your tool today.

But if you've watched a notes app die under your hands the way I've watched three of them die — or if there's a fact about your own past life you'd like to be able to look up in five seconds three years from now — Silt is a folder you can clone today, point your agent at, and start depositing into.

Five years from now you'll have something you can stand on.

---

Silt is open source under MIT. The repo, the example vault, and the four-rule graph convention that keeps it from collapsing are all at [github.com/example/silt](https://github.com/example/silt).
