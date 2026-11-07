---
title: Task ledger implementation and verification
updated: 2026-11-07
status: implemented-local
---

# Task ledger

Local implementation is complete. Browser layout verification is unavailable because installed Chromium cannot launch in this environment. No commit, push, installation, network request, model API call or Dashboard Artifact publication was performed.

## Acceptance evidence

- `python3 -I -m pytest -q tests`: 94 passed.
- `python3 -I scripts/dashboard-data.py`: all six datasets generated below 256,000 bytes.
- tasks.csv: 100 distinct task keys and page paths, 225,718 bytes. Sources: 60 mesh, 15 Workflow, 25 Codex. Outcomes at refresh: 66 done, 22 partial, 8 failed, 4 running.
- 100 current run pages plus runs/index.md exist. Every CSV page path resolves locally. A second unchanged refresh wrote zero run pages.
- `node tests/task-dashboard-check.cjs dashboard/index.html`: passed sorting, filtering, outcome chips, expansion, focus retention, native button semantics, literal text rendering and unknown-metric checks. This is a synthetic DOM test, not browser or layout validation.
- Dashboard JavaScript passed `node --check`; `git diff --check` passed.
- The browse skill's installed-browser preflight failed both with default flags and with its documented no-sandbox option: `BROWSER_UNAVAILABLE Chromium did not launch via node (browserType.launch: Target page, context or browser has been closed)`. No installer or daemon was started. Actual Enter/Space behavior, screenshots, the 390 px layout and native Dashboard Artifact refresh behavior remain unverified.

## Coverage and interpretation

The mesh summaries include one non-job .pytest_cache directory, which is excluded. Telemetry-only jobs are retained. The telemetry producer at /home/cheta/code/laptop-mesh/bin/mesh-telemetry maps big-surface to big and peer to little. Those aliases and the hostnames in the summary files are normalized before joining, so a job is counted once.

Codex dispatch attempts join call records only through their explicit session IDs. Unmatched historical sessions remain separate, partial records with unavailable briefs and terminal results. Their call outcomes do not establish task completion. The running c5 log includes quoted output from older logs; terminal token parsing excludes these quotes. The c4 wrapper repeats its answer after the token footer, which is handled when its final EXIT confirms termination. Codex totals are separate from output tokens. The final c4 total is 136,807.

Workflow journals do not contain timestamps in these inputs. Adjacent agent transcripts supply the prompt, timestamps, model and usage. Repeated message IDs are deduplicated. Workflow completion means all launched agents returned; it is not an independent acceptance gate. Paths observed in Write/Edit calls may include attempted writes. Missing cost remains unknown rather than zero.

Codex and Workflow rows are marked subscription. Mesh billing is unknown because the cached summary does not identify its authentication or billing route. Reported mesh cost is list price. No missing price is fabricated. Remote result text is capped at 4,000 characters by the existing collector, and output names at 60. Full available source text is retained in the run page; dashboard excerpts are 1,200 prompt characters and 600 result characters after redaction. The CSV shows the first 20 output names and the recorded total count.

The required project-archive redact helper runs recursively over free text and again at serialization. Redacted source identities receive deterministic short hash identifiers to avoid collisions. Prompt and result code fences adapt to embedded backticks. Oversized CSV exports fail before replacement, preserving every task rather than silently omitting rows.

## Outputs and refresh

Dataset: /home/cheta/.local/state/capacity-watch/dashboard/tasks.csv

Full record index: /home/cheta/LIVING_DOCUMENTS/projects/masterplan/runs/index.md

Run `python3 -I scripts/dashboard-data.py` to rebuild from current local inputs. Refresh remote summaries through the configured mesh SSH routes only when network work is authorized. Publishing or registering the tasks dataset in the hosted artifact is a separate action and was not attempted.

## Recovery

During verification, the first export used separate little and peer identities. The correction superseded 38 generated pages, including old host-suffixed filenames. They were moved intact to /home/cheta/LIVING_DOCUMENTS/projects/masterplan/runs/.task-ledger-checkpoints/2026-11-07-host-alias-correction/. Its manifest.json records original paths, checkpoint paths and verified SHA-256 checksums. No existing operator pages were removed. A first attempted checkpoint move to the state directory failed with EXDEV before moving any file; the final checkpoint stays on the run-pages filesystem.

Only the requested masterplan runs subtree was changed. No dossier-wide ensure/render/continuity mutation was run because this request forbids touching other dossier files. Existing source changes and the pre-existing untracked scripts/job-summary-remote.py were preserved. To roll back local implementation, review the file diff and restore only the task-ledger changes; generated records are independently reviewable through the index. No commits, index entries or remote refs were changed.

## Sample records

| Title | Outcome | Minutes | List cost USD | Subagents |
|---|---|---:|---:|---:|
| anthropic-orchestration | done | 14.137 | 4.6449 | 0 |
| ld-p2-rebase | done | 58.672 | 47.0703 | 6 |
| c4-mp13-phase3 | done | 11.78 | unknown | unknown |

## Changed source files

- SKILL.md
- dashboard/index.html
- scripts/dashboard-data.py
- scripts/task-ledger.py
- tests/test_task_ledger.py
- tests/task-dashboard-check.cjs
- references/task-ledger-2026-11-07.md

## Next safe action

Refresh from current local evidence when needed. Once a browser can launch, verify the desktop and 390 px view with actual keyboard interaction and inspect screenshots. Register the tasks dataset and publish the source only under separate explicit publication authorization.
