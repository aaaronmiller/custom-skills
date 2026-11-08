---
name: "skill-doctor"
description: "Grades agent skills by scoring recent local agent conversations for efficiency, code quality, procedure compliance, and verbosity, then drafts concrete skill edits and a local report. Works from any harness. Use when the user wants their agent setup graded from real conversation history, asks which installed skills are actually working, or asks why a skill did not fire."
version: "1.0.0-local.1"
source: adapted
upstream: "https://github.com/warpdotdev/common-skills/tree/8792394ff1b655e0af451b8fabb68ef0cfcbd208/.agents/skills/skill-doctor"
upstream_commit: "8792394ff1b655e0af451b8fabb68ef0cfcbd208"
attribution: "Original skill-doctor by Warp (Denver Technologies, Inc.), MIT License; full notice in LICENSE.upstream. Collector is upstream and unmodified; render_report.py hardened (http(s)-only cta_url, <>& escaped in embedded JSON); scorers unmodified except one widened example of rule files in procedure-compliance.md."
license: MIT
adapted: "2026-11-08: harness-agnostic startup, extra session sources (omp, cass export), canonical-source edit targets, no vendor call to action. See references/local-setup.md."
tags:
- skills
- evaluation
- retrospective
---
# skill-doctor

Grade the user's agent setup by scoring recent local agent conversations, then propose concrete skill edits and render one local report page.

The report can cover conversations in the current repository, conversations in selected projects, or all local conversations. It can evaluate project skills alone or project and global skills together.

Everything runs locally. Never upload transcripts, session files, or any excerpt of them anywhere. Score only in the current agent or in subagents of the same harness and provider. Never send transcripts to a different provider, a free endpoint, or a headless lane.

Let `SKILL_ROOT` be the directory containing this SKILL.md.

## Step 0: Start the run

### Any harness may run this skill

The harness that runs this skill only sets which tools you have. The conversations come from session files on disk, whichever harness wrote them. Do not stop because the current harness is missing from a list. Read `$SKILL_ROOT/references/supported-harnesses.md` for the sources the collector parses, and `$SKILL_ROOT/references/local-setup.md` when it exists for this machine's extra sources and skill locations.

### Choose the scope

Take the scope from the request when it states one. Otherwise use these defaults, and do not ask:

- Conversations: this repository when `git rev-parse --show-toplevel` succeeds, otherwise all conversations.
- Skills: project skills and global skills.

Ask only when the user asked to choose, or when the request names projects that do not resolve. To ask, use the harness's question tool when it has one, otherwise ask in plain text. Expand and validate every chosen project path as a git repository. One run produces one combined report.

For an all-conversations run, "project skills" means skills from local git repositories inferred from the conversations' working directories.

Never write artifacts into the user's repo. Create one fresh, collision-free scratch directory per run and use it as `REPORT_DIR` for every artifact:

```bash
REPORT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/skill-doctor-XXXXXXXX")"
```

## Step 1: Collect

Build the collector arguments from the scope:

- Current repository: `--repo "$REPO"`.
- Selected projects: repeat `--repo PATH` for every project.
- All conversations: `--all-conversations`.
- Project and global skills: add `--include-global-skills`.
- Project skills only: do not add `--include-global-skills`.

```bash
python3 "$SKILL_ROOT/scripts/collect_sessions.py" \
  --out "$REPORT_DIR" \
  <conversation-scope arguments> \
  <skill-scope arguments>
```

By default `--harness auto` scans every locally available source the collector parses. Read `$SKILL_ROOT/references/supported-harnesses.md` for source identifiers, storage details, skill locations, source-specific override flags, and the extra passes for sources the collector does not parse.

Useful flags:

- `--harness VALUE`: which local session sources to scan; use the reference's collector IDs.
- `--repo PATH`: include a project; repeatable.
- `--all-conversations`: do not filter conversations by project.
- `--include-global-skills`: also grade global skills.
- `--days N`: lookback window (default 45).
- `--max-sessions N`: cap on sampled sessions (default 12).
- `--skills-dir PATH`: nonstandard skill locations.
- `--include-subagents`: include child or sidechain sessions.

Then run the extra passes from the reference for every other source that has sessions in the window. Record in the report which sources were collected, which were found but not parsed, and why. Never report a source as covered when no transcript from it was read.

Read `$REPORT_DIR/inventory.json`. If `sessions_sampled` is 0 across all passes, tell the user there is nothing recent to score in the selected scope (suggest raising `--days` or choosing different projects) and stop. If `skills_found` is 0, continue: the report becomes a case for creating skills, and `skill_coverage` is 0.

## Step 2: Score each sampled transcript

Scoring is based on efficiency, code quality, procedure compliance, and verbosity for the sessions sampled. Process datasets of 50 transcripts or fewer in a single batch. For datasets with more than 50 transcripts, use parallel batches (20 transcripts per batch recommended), within the privacy rule above. Pass the following rubrics as context:

- `$SKILL_ROOT/scorers/efficiency.md`
- `$SKILL_ROOT/scorers/code-quality.md`
- `$SKILL_ROOT/scorers/procedure-compliance.md`
- `$SKILL_ROOT/scorers/verbosity.md`

Instructions: For each transcript in `$REPORT_DIR/transcripts/` (and the extra-pass transcript directories), read it and judge it against all four rubrics. For each scorer record: label, numeric score (from the rubric's label table), and a 1–3 sentence reason citing specifics from the transcript. Apply the code-quality scorer only where the transcript shows code changes; otherwise record `insufficient_evidence` and exclude that result from the code-quality average and failed-conversation filter. A transcript that lacks tool calls (some exports carry only messages) gets `insufficient_evidence` for efficiency instead of a guessed score.

## Step 3: Aggregate

- `raw_efficiency` = mean of efficiency scores across all scored sessions, excluding `insufficient_evidence`.
- `raw_code_quality` = mean of code-quality scores, excluding `insufficient_evidence`. If no session had enough evidence, set it to 0.5 and say so in the findings.
- `raw_procedure_compliance` = mean of procedure-compliance scores across all scored sessions.
- `raw_verbosity` = mean of verbosity scores across all scored sessions.
- Curve qualitative rubric means into letter-grade report scores with `curve(score) = 0.5 + 0.5 * score`.
- `efficiency = curve(raw_efficiency)`.
- `code_quality = curve(raw_code_quality)`.
- `procedure_compliance = curve(raw_procedure_compliance)`.
- `verbosity = curve(raw_verbosity)`.
- `skill_coverage` = fraction of sampled sessions where at least one installed skill was detected. If `skills_found` is 0, coverage is 0.
- `overall = 0.25 * efficiency + 0.25 * code_quality + 0.2 * procedure_compliance + 0.15 * verbosity + 0.15 * skill_coverage.`

Then, define `failed_conversations` from each conversation's raw, uncurved scorer results. A conversation fails when at least one applicable efficiency, code-quality, procedure-compliance, or verbosity score is below `0.5`. An `insufficient_evidence` result does not make a conversation fail. Use only `failed_conversations` as evidence for skill-improvement suggestions and draft skill edits.

Then derive the substance:

- `top_findings`: the 3 most impactful, specific patterns across sessions. These lead the report and the spoken summary. Make each summary concrete and concise, following the STE-100 standard.
- `suggestions`: concrete skill changes, if any. Each names a skill (existing or proposed-new) and a specific change: a trigger-description fix so it fires when it should, a missing step or check, a command to encode, a new skill to create. Suggestions must trace back to observed waste or defects in `failed_conversations`, not generic best practices: cite the failed session, scorer, and moment that motivated each one. An installed skill that never triggered in a failed conversation is usually a description problem and worth a suggestion of its own.

## Step 4: Draft skill edits

Follow `$SKILL_ROOT/references/skill-improvements.md` to propose improvements based only on `failed_conversations`.

1. Find the skill's canonical source before reading it. The path in `inventory.json` is often a deployed copy or a symlink in a harness directory; an edit there is overwritten at the next sync. Resolve it as `$SKILL_ROOT/references/local-setup.md` describes, or with `realpath` when no local setup exists. Record both paths in the suggestion.
2. Write the full improved version to `$REPORT_DIR/proposed/<skill-name>/SKILL.md`, changing only what the evidence justifies. Improve the parts the sessions actually exercised: the trigger description that failed to fire, the missing preflight check, the step the agent had to figure out by trial and error.
3. Produce a unified diff between the canonical source and the proposal (`diff -u <canonical> <proposed>`) and put it in the suggestion's `diff` field so it renders in the report.

For a proposed-new skill, write the complete new SKILL.md to the same `proposed/` directory and set `diff` to its full content as an addition.

Do not modify the user's real skill files in this step. A skill owned by a third-party upstream gets a proposal only; adapting it is a separate, user-approved change.

## Step 5: Write report.json and render

Write `$REPORT_DIR/report.json`. Store the curved `efficiency`, `code_quality`, `procedure_compliance`, and `verbosity` values, literal `skill_coverage`, and weighted `overall` in `scores`; do not store the raw rubric means there. Set `harness` to the sources actually collected (for example `claude+codex+omp`), not the harness running the skill.

```json
{
  "title": "Agent Skill Report",
  "generated_at": "<ISO timestamp>",
  "harness": "<sources collected>",
  "handle": "<repo_name from inventory.json>",
  "stats": {
    "sessions_analyzed": 0, "sessions_scanned": 0,
    "skills_found": 0, "skills_used": 0, "window_days": 45
  },
  "scores": {
    "efficiency": 0.0,
    "code_quality": 0.0,
    "procedure_compliance": 0.0,
    "verbosity": 0.0,
    "skill_coverage": 0.0,
    "overall": 0.0
  },
  "top_findings": ["", "", ""],
  "suggestions": [
    {
      "skill": "",
      "change": "<one-sentence summary of the edit>",
      "evidence": "<which session(s) and what happened that motivates this>",
      "proposed_path": "<path under proposed/, if an edit was drafted>",
      "diff": "<unified diff, or full content for a new skill>"
    }
  ]
}
```

```bash
python3 "$SKILL_ROOT/scripts/render_report.py" "$REPORT_DIR/report.json"
```

This writes a single self-contained `$REPORT_DIR/report.html`. Add `--open` only when the host can open a browser; it does nothing on headless and WSL hosts. The page is upstream's renderer and keeps its Warp styling, share button and a Warp Factories link in the footer; the share image is made locally.

## Step 6: Output

Report the grade, the three findings, which sources were and were not collected, and the suggestions with their canonical target paths, in text. Give the report as a bare absolute path on its own line:

    $REPORT_DIR/report.html

Applying any suggestion is a separate step that the user approves; do not end the run by applying edits.
