---
name: weekly-report-suite
description: >-
  ALWAYS invoke when Aaron/Cheta/Ice-ninja asks for a weekly progress report,
  dad-facing report, mentor/parent update, personal weekly report, in-depth weekly
  report, report dashboard, weekly HTML report, project-history analytics, or a
  combined weekly narrative plus dashboard. Generates two coordinated outputs:
  (1) a one-page dad/mentor-facing report in the established Subject/Greetings/
  Strategic Overview format, and (2) a richer personal report/data pack for an
  HTML/Grafana-style dashboard. Triggers: "weekly report", "dad report", "progress
  report", "week ending", "make the report for my dad", "personal report", "HTML
  weekly dashboard", "project history dashboard", "Daily Radar".
tags:
  - automation
  - data
  - writing
grade: A
source: custom
---

# Weekly Report Suite

Generate Aaron's weekly report system: a concise dad-facing report plus a richer personal report/data pack that can drive a live project-history dashboard.

This skill exists because the weekly reports are not generic retrospectives. They are trust-building communications for a non-technical parent/mentor and a personal operating history for Aaron's agentic engineering portfolio. The report must compress messy cross-agent work into a clear narrative without overclaiming.

## Default deliverables

Unless the user says otherwise, produce these outputs:

1. **Dad-facing weekly report**: one-page maximum target, `Subject:` line first, ends with `-A`.
2. **Personal weekly report**: more detailed technical report for Aaron, with evidence, caveats, work done / work in progress / work planned.
3. **Dashboard bundle**: JSON metrics + static HTML dashboard assets suitable for later conversion into a richer site.
4. **Self-improvement notes**: short audit of what the skill should improve next week (new metrics, categories, visualizations, or evidence gaps).

If the user provides exact paths, write to those paths. If not, use:

```text
/home/cheta/code/weekly-report-YYYY-MM-DD.md
/home/cheta/code/weekly-report-YYYY-MM-DD-personal.md
/home/cheta/code/weekly-report-dashboard/YYYY-MM-DD/
```

## Core workflow

### 1. Review history first

Before asking the user questions, gather as much context as possible from existing sources.

Use these sources in order:

1. `session_search` for recent Hermes history and prior report sessions.
2. CASS if available:
   - `cass health --json`
   - `cass timeline --since <start> --until <end> --json --group-by day`
   - `cass search "<topic>" --json` for likely workstreams.
3. Filesystem and git evidence under `/home/cheta/code`, `/home/cheta/code2`, `/home/cheta/wiki`, and relevant project dirs.
4. Existing weekly reports from the prior week(s).
5. User-supplied brain dump, corrections, metrics, and mentor notes.

Do not ask broad questions until this evidence sweep is done. The goal is to minimize user burden.

### 2. Separate what was done from what was planned

The reports must distinguish:

- **Shipped / verified**: working code, committed files, generated reports, successful runs.
- **Designed / scaffolded**: plans, specs, dashboards, scripts, templates that exist but have not run end-to-end.
- **In progress / blocked**: work with known next actions or unresolved issues.
- **Ongoing operations**: scheduled jobs, trackers, monitoring, reports that continue running.

This distinction matters more than making the week sound impressive. Honest status builds trust.

### 3. Generate the dad-facing report

Use the dad/mentor template in `references/templates/dad-report.md` and detailed guidance in `references/dad-report-template.md`.

Characteristics:

- One-page target, usually 550-750 words.
- Smart non-technical reader; explain terms by function, not jargon.
- Do not condescend.
- Focus on theme and significance, not a tool dump.
- Keep project pipeline to 3-5 active items.
- Minimize rejection notices or negative job-search details unless user explicitly requests them.
- If no mentor meeting happened, say so briefly.
- End with `-A`.

### Voice calibration (2026-08-30, mandatory before drafting)

The 2026-08-29 report took seven drafts. Five operator corrections produced the
calibration; do not repeat them. Full record:
`~/LIVING_DOCUMENTS/projects/weekly-reports/version-analysis-2026-08-29.md`.

Canonical voice exemplar (memorize before drafting — pattern-match against it,
do not imitate abstractly):

> You instructed me to move faster on the job search, so this week I began the
> pivot. I'll be shifting most of my time towards applying and meeting people
> next week. I sent 45 applications on Friday, the most in several months. The
> rest of the tooling gets finished in the coming weeks alongside the job
> search.

Drafting rules that follow from it:

1. **Tense honesty.** Past tense for finished acts, future for shifts that
   start later. Never present-perfect for planned work.
2. **Zero unsolicited justifications.** State the decision; if the reader
   wants the reason, they ask. A sentence explaining why a choice was
   reasonable gets cut unless the reader asked.
3. **Self-measured superlatives.** Every quantitative claim carries its
   comparison where a baseline exists ("the most in several months", "up from
   last week").
4. **Instructor-to-executor register.** The reader gave direction; report
   execution. "You instructed me", not "you told me".
5. **Next-week items are goals, not commitments.** Open the section with the
   goals-not-commitments framing; a goal that produces no data still taught
   something.
6. **Every next-week goal carries method and analysis**, not a list line. The
   reader is a teacher: paragraphs, not bullets.
7. **Prose over bullets** for the whole document.

### Pre-send checklist (executes the rules; run before showing the report)

- [ ] Every claim is past (done) or future (planned) — no present-perfect for planned work
- [ ] Zero unsolicited justification sentences
- [ ] Every number carries its self-comparison where a baseline exists
- [ ] Next-week section opens with the goals-not-commitments framing
- [ ] Every next-week goal has method and analysis in prose
- [ ] Word count inside the target; no em dashes in the body
- [ ] Register check: read paragraph one aloud — does it sound like an
      executor reporting to an instructor?

### 4. Generate the personal report

Use `references/templates/personal-report.md` and `references/personal-report-template.md`.

Characteristics:

- Technical and evidence-aware.
- Includes work done, work in progress, work planned.
- Includes carry-over items from last week plus new items.
- Includes metrics and caveats.
- Designed to feed the HTML dashboard and future weekly reports.
- May include file paths, session IDs, hashes, CASS findings, and exact blockers.

### 5. Generate dashboard bundle

Use `scripts/collect_weekly_evidence.py` to create or refresh a metrics JSON pack. Then use the canonical dashboard generator at `weekly-report-dashboard/scripts/build_dashboard.py` to produce the self-contained `index.html`.

Dashboard generation (canonical):

```bash
python3 /home/cheta/code/weekly-report-dashboard/scripts/build_dashboard.py
# or with flags:
python3 /home/cheta/code/weekly-report-dashboard/scripts/build_dashboard.py --weeks 13 --dark-work-threshold 8.0 --stall-age 3
python3 /home/cheta/code/weekly-report-dashboard/scripts/build_dashboard.py --check  # validate without writing
```

The single-week renderer `scripts/render_dashboard.py` is retired; use the canonical generator above for all dashboard builds. Historic per-week bundles under `weekly-report-dashboard/YYYY-MM-DD/` are preserved.

For live metrics, `scripts/prometheus_exporter.py` serves a Prometheus-compatible `/metrics` endpoint and a JSON `/data` endpoint. Grafana is the natural dashboard partner for Prometheus.

### 6. Run the self-improvement loop

At the end of each weekly report task, run a brief audit using `references/self-improvement-loop.md`:

- What evidence was easy/hard to gather?
- Which metrics were missing or noisy?
- What categories should be added next week?
- Which dashboard visualization should improve?
- Did the dad report overclaim, under-explain, or get too long?
- Did the personal report preserve enough evidence for future dashboards?

Write improvements to the personal report or a dashboard `improvement-notes.md` file. Do not silently edit the skill itself unless the user asks to improve the skill.

## Required report sections

Dad-facing report uses this exact section order:

```text
Subject: Week Ending <Date> -- <Theme>

Greetings,

Strategic Overview

Active Project Pipeline

Progress This Week

Mentor Feedback

Next Milestone (Upcoming Week)

Career Positioning

-A
```

Personal report uses this section order:

```text
# Week Ending <Date> -- Personal Weekly Report

## Executive Summary
## Evidence Reviewed
## Work Done
## Work In Progress
## Work Planned
## Project Pipeline with Carry-Over
## Metrics and Dashboard Notes
## Risks / Blockers / Caveats
## Dad Report Relationship
## Self-Improvement Notes
```

## Checkbox protocol

When the user wants checkbox tracking, use it in the personal report and optionally in the dad report only if the examples for that period include checkboxes.

Rules:

- Import last week's unchecked items into this week's planned/carry-over list.
- Mark completed carry-over items as `[x]` once in the current week.
- Completed items appear one more time after completion, then are omitted in future weeks.
- New planned items are `[ ]`.
- If a project reaches final completion, note whether its README should be annotated; do not edit project READMEs unless explicitly asked.

Format:

```markdown
**Project Name (State; Activity):** One-sentence description.
- [x] Completed item from last week
- [ ] Next validation/action item
```

## HTML and analytics direction

The dashboard should not replace the written report. The graphics show the pattern; the written report explains meaning.

The dashboard should include sections for:

- Week headline and written summary.
- Work done.
- Work in progress.
- Work planned / carried over.
- Project activity table.
- Agent/session activity if CASS data is available.
- Git commit/file-change activity.
- Momentum score and a computed **Trends vs Last Week** table — not placeholders.
  Prior bundles are already on disk under
  `/home/cheta/code/weekly-report-dashboard/YYYY-MM-DD/`, so the deltas are a
  lookup, not an estimate. Three columns, Last / Now / Delta, one row per metric
  that has a prior value:

  | metric | last | now | delta |
  | --- | --- | --- | --- |
  | test ratio | 22% | 41% | ↑19pp |

  Omit a row when there is no prior bundle rather than showing a zero delta —
  "no comparison available" and "no change" are different claims.
- A closing classification pass over the week's commits: **likely bug fixes /
  likely tech debt / likely net-new functionality**. Hedged deliberately — the
  split is inferred from diffs and messages, not declared by the author — and it
  feeds both the personal report and the dashboard categories.
- Evidence/caveat panel to show which metrics are verified vs estimated.
- Self-improvement backlog.

Use the dashboard spec in `references/dashboard-and-metrics-spec.md`.

## Prior-work context

This skill inherits ideas from Daily Radar and project_dashboard, but it is more specific: Daily Radar is broad multi-cadence activity synthesis; this skill is the weekly reporting product for Aaron's dad/mentor plus Aaron's personal dashboard. See `references/prior-work-audit.md` before modifying dashboard assumptions.

The Claude-online source instructions and durable report memory are distilled in `references/claude-online-source-spec.md`. Read that reference when changing the report-generation protocol, checkbox behavior, or dad-facing style rules.

## Quality checklist before final response

- [ ] Reviewed history before asking questions.
- [ ] Used prior report examples for length/style.
- [ ] Dad report starts with `Subject:` and ends with `-A`.
- [ ] Dad report is concise and non-technical.
- [ ] Personal report explicitly separates shipped, designed, in progress, and planned.
- [ ] No generated HTML/dashboard claim unless files were actually written.
- [ ] Dashboard bundle includes JSON metrics and static HTML if requested.
- [ ] Word counts and file paths verified with real tool output.
- [ ] In-depth/personal report not modified unless requested.
- [ ] Self-improvement loop captured next improvements.
