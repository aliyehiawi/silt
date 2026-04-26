---
type: journal-index
title: All-time journal index
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags:
  - journal
  - index
  - spine
---

# All-time journal index

> **Template.** `/journal --reindex` regenerates this file: a flat list of every year that has at least one entry, each year wiki-linked to its yearly index. The yearly indexes in turn list months; each monthly index lists days. Every wiki-link is path-based per the [[memory/README.md|graph convention]].

```
journal/
  YYYY/
    YYYY.md           ← yearly index (regenerated)
    MM/
      YYYY-MM.md      ← monthly index (regenerated)
      YYYY-MM-DD.md   ← daily entry (immutable)
```

## Years

_No entries yet. Your first `/journal` call creates the daily entry and stubs the year + month indexes._
