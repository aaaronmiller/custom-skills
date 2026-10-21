---
name: notes-sweeper
description: |-
  Monthly recovery + audit of live scratchpad notes (Windows Notepad/Notepad++ tabs) into durable project files. Use for recovering unsaved tabs, classifying clipboard/crash remnants against the project index, and keeping notes programs empty and clean.
  Triggers: "sweep notes", "recover notepad", "notepad recovery", "monthly notes", "unsaved tabs", "clipboard audit", "scratchpad cleanup", "notes-sweeper".
license: MIT
metadata:
  version: "1.0"
  cadence: monthly
tags:
- notes
- recovery
- triage
- onboarding
---

# Notes Sweeper 1.0

> From live scratchpad chaos to durable project files — monthly, without losing anything.

Proven on the 2026-10-21 run: 78 Notepad++ tabs + 120 Notepad bins → 81 extracted → 73 dossier pages + vault topics + human-review queue. Preservation before interpretation, always.

## Rules (standing)

- Never close/touch the live apps until snapshots are read-only.
- File-backed notes (actual files on disk): ignore, already preserved.
- Notepad vs Notepad++ distinction is meaningless — merge.
- Resource-file notes attach their location to the dependent note, don't route separately.
- Email-killed and user-dropped items stay dropped (record the rule, don't re-litigate).
- Classes: actionable / plan-input / project-input / vault-topic / transcript-done / task-completed / junk-drop / unknown → human review.
- Multi-topic notes split (accidental) or keep whole (intentional consolidation — verify before splitting).
- Clean spelling/grammar/toolcall noise at route time, never in the exact layer.

## Operation 1: Snapshot (scripts/recover.py)

Run `python3 scripts/recover.py` — it snapshots `%LOCALAPPDATA%/Packages/...Notepad.../LocalState` (TabState + WindowState) and `%APPDATA%/Notepad++/backup + session.xml + config.xml` via `/mnt/c`, hashes everything (SHA-256 → `reports/source-hashes.csv`), marks snapshots read-only, and parses:
- Notepad++: `session.xml` entry → backup buffer (byte-for-byte into `extracted-exact/`); file-backed entries become catalog refs.
- Notepad: GUID `.bin` UTF-16 parse (longest printable run = content, `^[A-Z]:\\` run = saved path); `.0/.1.bin` state + WindowState for order.

## Operation 2: Secrets + classify

Secrets scan over extracted content (key/token/private-key patterns) → `sensitive-local-only/`, redacted stub only. Then classify each note against the project index (`~/LIVING_DOCUMENTS/projects/ (unchanged)` + assignments catalog) with 1–3 `cass search` probes per hypothesis. Confidence ≥75 auto-routes; below goes to `unassigned/` or the human-review queue.

## Operation 3: Route

Write new dated pages into dossiers (never overwrite), vault topics to the scratchpad, actionables as task files. Record splits/merges/drops in the reconciliation report. Unclassifiable → `HUMAN-REVIEW-<date>.md`, not forced.

## Resource files

| File | Read when |
|------|-----------|
| `references/monthly-cadence.md` | Scheduling the sweep; delta-only runs (new tabs since last snapshot) |
| `references/classification-rubric.md` | Class definitions, split/merge rules, confidence thresholds |
| `scripts/recover.py` | Every snapshot + parse run (defaults to `~/agent-notes/recovery/`) |
| `~/agent-notes/` | Evergreen root: `scratchpad/` vault + `recovery/` runs; commit + push per sweep |
| `reports/process-notes.md` (per-run) | Steering rules accumulated across runs |
