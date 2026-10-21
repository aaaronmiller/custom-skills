---
title: Classification rubric
version: "1.0"
tags: [notes-sweeper, classification, rubric]
---

# Classification rubric

| Class | Meaning | Route to |
|---|---|---|
| `actionable` | Executable now (task prompt, triage question, matrix to build) | Task file in target dossier |
| `plan-input` | Feeds a plan/backlog, not directly executable | Backlog or plan-input page |
| `project-input` | Evidence/spec/fragment for a dossier | Dated findings page |
| `vault-topic` | Project-agnostic reference (fonts, research, craft) | Scratchpad reference/ or Obsidian vault |
| `transcript-done` | Transcript already converted/ingested elsewhere | Drop with pointer |
| `task-completed` | No open action (session log, status note, decided handoff) | History page or drop |
| `junk-drop` | Keysmash, bare path, orphan quote, tool noise | Drop with reason |
| `unknown` | Too thin even after CASS + index + vault checks | HUMAN-REVIEW queue, never forced |

Split accidental consolidations (finance↔career, dashboard↔census); keep intentional ones whole (session logs). Merge verbatim dupes, keep the cleaner copy. Confidence ≥75 auto-routes.
