---
name: notes-sweeper
description: "Monthly recovery + audit of live scratchpad notes (Windows Notepad/Notepad++ tabs) into durable project files. Use for recovering unsaved tabs, classifying clipboard/crash remnants against the project index, and keeping notes programs empty and clean. Triggers: 'sweep notes', 'recover notepad', 'notepad recovery', 'monthly notes', 'unsaved tabs', 'clipboard audit', 'scratchpad cleanup', 'notes-sweeper'."
license: MIT
metadata:
  version: "1.1"
  cadence: monthly
  tags: "notes, recovery, triage, onboarding"
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
- Fuzzy/typo-tolerant folder & project matching: older notes and voice dictations frequently misspell or hyphenate project/folder names differently from disk (e.g., `001-pspace-lab` ↔ `ai-book-writing/ai_novel/p-space-lab` and `p_space_observability_lab`; `dot claud/agents` ↔ `.claude/agents` / `agents`; `realtime-voice-ass` ↔ `voice-agent`; `clear mobile hotsppot` ↔ vault `clear mobile hotsppot reverse engineer information.md`; `adrf` ↔ `ardf`; `orchest` ↔ `orchestrator-stack`; `newcomputersscript`; `MODEL-DASHOARD`; `orchestration-mastrerplan`; `MacroMap-my prodiuctivity app`;
`findit-small temrinal utility to find ish`). Always match against all four roots (`~/code`, `~/code2`, `~/LIVING_DOCUMENTS/projects`, and the Windows Obsidian vault `/mnt/c/Users/Administrator/Documents/chetaz`) using normalized/fuzzy token matching before placing anything in `unassigned/`.
- Naming guard: folder name = GitHub remote name = lowercase-dash, always (with `~/LIVING_DOCUMENTS` ↔ `living-docs-content` / `living-documents-corpus` as the sole grandfathered exception). Any new checkout or created repo whose folder name does not match its remote gets flagged/renamed at creation, never left mismatched.

## Operation 1: Snapshot (scripts/recover.py)

Run `python3 scripts/recover.py` — it snapshots `%LOCALAPPDATA%/Packages/...Notepad.../LocalState` (TabState + WindowState) and `%APPDATA%/Notepad++/backup + session.xml + config.xml` via `/mnt/c`, hashes everything (SHA-256 → `reports/source-hashes.csv`), marks snapshots read-only, and parses:
- Notepad++: `session.xml` entry → backup buffer (byte-for-byte into `extracted-exact/`); file-backed entries become catalog refs.
- Notepad: GUID `.bin` UTF-16 parse (longest printable run = content, `^[A-Z]:\\` run = saved path); `.0/.1.bin` state + WindowState for order.

## Operation 2: Secrets + classify

Secrets scan over extracted content (key/token/private-key patterns) → `sensitive-local-only/`, redacted stub only. Then classify each note against the project index (`~/LIVING_DOCUMENTS/projects/ (unchanged)` + assignments catalog) with 1–3 `cass search` probes per hypothesis. Confidence ≥75 auto-routes; below goes to `unassigned/` or the human-review queue.

## Operation 3: Route

Write new dated pages into dossiers (never overwrite), vault topics to the scratchpad, actionables as task files. Record splits/merges/drops in the reconciliation report. Unclassifiable → `HUMAN-REVIEW-<date>.md`, not forced.

## Operation 4: Organize into the library (scripts/organize.py)

Run after every snapshot, and whenever the operator asks where a note is. Snapshots alone are not the deliverable: an extraction nobody can browse is the failure the 2026-11-04 run left behind.

`OPENCODE_GO_API_KEY=... python3 -I scripts/organize.py` reads every run under `~/agent-notes/recovery/`, then:
- **Gather** every Notepad TabState text (current, autosave and deleted history), every Notepad++ backup buffer, and saved Notepad++ tabs in scratch locations (Downloads, Documents, Desktop, `~/tmp`). Aggregate saved files count too: the 534k-char `YEEZYS TURN ME INTO A LIVIGN DOCUMENT ALREEDY.MD` is one. Saved files over 1.5M chars, such as the Apple Notes export, are a separate corpus and are skipped with a log line.
- **Merge versions.** Exact copies across runs collapse, and an older copy of a tab contained in a newer one is recorded as a version.
- **Slice.** Split on headings, separators and blank-line gaps, then have Gemini 4 Argon on OpenCode Go group the blocks into separate notes. That model's listed terms are no training and zero retention. The same call gives each note a title, kind, summary, 1 to 3 Living Documents project ids, themes, a has-tasks flag and a status.
- **Cluster** near-identical notes across tabs into one note with its copies listed.
- **Write** `~/agent-notes/library/`: `notes/<project>/<date>-<slug>-<id>.md` with YAML frontmatter, `sources/<tab>.md` listing each tab's sections in order, `catalog.json` and a self-contained `index.html`. The index has search, project, kind, status and has-tasks filters, plus a by-tab view and copy buttons that give Windows paths.

Secrets are redacted before text leaves the machine, and the library holds only redacted text; raw text stays in the read-only recovery snapshots. Model plans are cached per tab in `library/.cache/plans/`, so a rerun only pays for new tabs.

## Resource files

| File | Read when |
|------|-----------|
| `references/monthly-cadence.md` | Scheduling the sweep; delta-only runs (new tabs since last snapshot) |
| `references/classification-rubric.md` | Class definitions, split/merge rules, confidence thresholds |
| `scripts/recover.py` | Every snapshot + parse run (defaults to `~/agent-notes/recovery/`) |
| `scripts/organize.py` | After every snapshot: slice, title, tag, de-duplicate and index into `~/agent-notes/library/` |
| `~/agent-notes/` | Evergreen root: `scratchpad/` vault + `recovery/` runs; commit + push per sweep |
| `reports/process-notes.md` (per-run) | Steering rules accumulated across runs |
