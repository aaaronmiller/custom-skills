---
name: skill-audit
description: 'Audit skill ecosystems for quality, redundancy, structural integrity,
  and description quality.

  CRITICAL: The description field is the SKILL ACTIVATION MECHANISM — it tells the
  model when to load the skill. Do not strip "Use when:" or trigger phrases. Descriptions
  need TRIGGER COVERAGE, not brevity.

  Use when: reviewing skills for junk/keep decisions, evaluating SKILL.md quality,
  checking description trigger coverage, reducing always-loaded token waste (without
  removing triggers), identifying single-use "pre-curate" skills, comparing against
  S-tier reference skills, generating removal recommendations, assessing description
  trigger quality and token efficiency, checking for duplicates/redundant task clusters,
  running quarterly maintenance sweeps, or onboarding skills from new sources.

  Triggers: "audit skills", "find junk skills", "clean up skills", "skill review",
  "which skills should I keep", "are my skills good", "skill quality check", "remove
  useless skills", "evaluate description", "check trigger coverage".

  '
license: MIT
metadata:
  author: ice-ninja / Hermes Agent
  version: '2.0'
tags:
- planning
- automation
grade: A
source: custom
---

# Skill Audit

> Systematic evaluation of skill quality using binary PASS/FAIL + heuristic categorization.

## Mechanical checks (run these first)

Two checks are arithmetic, not judgement, and neither is reliable done by eye.
Run them before any deep read so the judgement work starts from facts.

```bash
python3 scripts/audit_mechanical.py <skills-root>
python3 scripts/audit_mechanical.py <skills-root> --json --threshold 50
```

**Trigger collision.** Two skills quoting the same trigger phrases compete for
the same activation, and which one loads is arbitrary. Name similarity does not
find this: in the 2026-08-22 audit, `deprecated/strata` and `strata-authoring`
shared 100% of their quoted triggers while two skills with near-identical names
turned out to be a pipeline split rather than a duplicate. The inverse matters
as much - a skill quoting no trigger phrases cannot activate on intent at all,
and is a resource in everything but filing.

**Progressive-disclosure integrity.** A skill whose `references/`, `scripts/`
or `assets/` targets are missing is inert regardless of how good its prose is.
On that corpus, 21 of 39 skills had every target missing, silently: a script
had emptied the directories five weeks earlier and the SKILL.md files were
untouched, so nothing looked wrong from the index.

Exit status is non-zero when a collision at or above the threshold exists, so
this can gate a commit.

## Core Audit Framework

### The 5 FAIL Criteria (Binary — PASS or FAIL)
A skill is **BROKEN** if ANY ONE of these is true:

1. **BROKEN** — SKILL.md missing, malformed YAML frontmatter, references files promised but absent, tools referenced don't exist in current context
2. **DANGEROUS** — Contains destructive commands without safeguards, prompt injection vectors, data exfiltration patterns
3. **OUTDATED** — References deprecated APIs, tools, or workflows that no longer work
4. **DUPLICATE** — Same topic covered better elsewhere, multiple skills doing identical job
5. **USELESS** — No general utility, single-session task saved as skill, "pre-curate" one-shot workflow

**Pass ≠ perfect.** The bar is "can this skill do its job correctly." Fix failures; don't refactor passing skills.

### The "Pre-Curate" Junk Pattern

Skills created by agent automation before curation existed typically exhibit:

| Indicator | Signal |
|-----------|--------|
| Single cron job as a skill | Mentions cron/daily/schedule as core feature |
| References browser tools outside scope | `browser_navigate`, `browser_vision` in non-browser task |
| Narrow to one project workflow | eBay scraper, one specific Electron bug fix |
| Redundant cluster | 4+ skills doing the same thing (eBay scrapers) |
| Created during debugging session | `electron-white-screen-*`, `ci-cd-workflow-repair` |
| <10 lines or >400 lines with checklists | Too short for real value, or project plan masquerading as skill |

### S-Tier Skill Indicators (Reference: skills-USER/)

**High-quality skills exhibit:**
- Comprehensive description with specific trigger phrases (30+ listed triggers)
- Version tracking in YAML frontmatter
- Author attribution
- External resources / references directory for progressive disclosure
- Working code examples with proper syntax highlighting
- Clear "When to Use" section
- Not overly long: under 300 lines for body, deeper content in references/
- No TODO/FIXME markers or unchecked checklists (those are project plans, not skills)

## Quick Start

### 1. Profile the Skill Ecosystem
```
Count total SKILL.md files across all directories.
Identify categories: bundled, user, third-party, hermes-created.
Document total lines, average size, outliers.
```

### 2. Run Junk Detection
```
Check for: duplicate topic clusters (ebay, macbook, electron),
skills referencing narrow tools (browser_navigate),
skills mentioning cron as core purpose,
tiny skills (<30 lines minimal structure),
skills with TODO/FIXME/phase headers (project plans).
```

### 3. Deep-Read Suspect Candidates
```
For each flagged junk candidate: read full SKILL.md.
Assess: Is this a general workflow or a single-session task?
Would this skill be useful to someone else? Next month?
Check: references/ dir exists? Version info? Proper frontmatter?
```

### 4. Categorize
```
Default (bundled) → Good or Low-Utility
User-created → Presumed Good (skip)
Third-party → Check creator field, verify via web
Hermes-created → Good or Junk (requires full read)
```

### 5. Generate Recommendations
```
DELETE: Confirmed junk (duplicate ebay scrapers, unused single-task skills)
CONSOLIDATE: Duplicate skills on same topic (electron debuggers)
HIDE FROM CONTEXT: Low-utility defaults (pokemon, gaming, niche tools)
KEEP: Everything else
```

## Validation Checklist

Use this for each skill under review:

- [ ] SKILL.md exists with valid YAML frontmatter
- [ ] `name:` and `description:` fields present
- [ ] Description uses third person with specific triggers
- [ ] Body uses imperative/infinitive form (not second-person)
- [ ] Under 300 lines (lean), deeper content in references/
- [ ] References exist if referenced in SKILL.md
- [ ] No unchecked `- [ ]` checklists (project plan flag)
- [ ] No `TODO:` or `FIXME:` markers
- [ ] Tools referenced actually exist in current agent context
- [ ] Not a duplicate of another skill (same function, different name)
- [ ] Has general utility beyond one project/session/cron job
- [ ] Version field present for tracking

## Decision Matrix

| Condition | Action |
|-----------|--------|
| BUNDLED SKILL — bundled in manifest | Keep (don't delete, may be restored on update) |
| LOW UTILITY — bundled, niche use | Can hide from always-loaded context |
| HERMES-CREATED — good quality | Keep, optionally promote to user skills |
| HERMES-CREATED — single-session junk | Delete (hermes-created, recoverable via curate) |
| USER SKILL — user-created | Keep (always, user explicitly said not to delete) |
| THIRD-PARTY — installed via hub | Keep (reinstallable if needed) |
| THIRD-PARTY — junk quality | Suggest removal, user decides |
| DUPLICATE CLUSTER (3+ copies same task) | Delete extras, keep 1 consolidated version |

## Cross-Skill Comparison

When you find a marketplace skill that overlaps with one you already have,
or when deciding whether to adopt a new skill vs keep an existing one:

1. **Load the rubric**: Read `references/scoring-rubric.md` — it contains the
   10-category scoring system, comparison protocol, and merging methodology.
2. **Score both skills**: Grade each independently using the rubric.
3. **Compare**: If yours wins by 10+ points, keep yours. If theirs wins,
   adopt theirs. If close (<10), merge the best parts of both.
4. **Merge**: Start with the higher-scoring base, port elements from the other,
   save the result to Skills-USER/.
5. **Validate**: Run deliberative refinement (V(3,1,0) LITE) on the merge.

The rubric also covers marketplace gap analysis — how to check what's trending
on skills.sh, ClaudSkills, Agensi, etc., and whether we're missing something. |

## Description Audit (Understanding How Descriptions Work)

**CRITICAL: The description is the SKILL ACTIVATION MECHANISM, not a summary.**

The model sees a flat list of descriptions in context and decides which skills to load
by matching the current task against description text. More trigger phrases = higher
recall. Longer descriptions with detailed trigger coverage are NOT wasteful — they are
functionally necessary for correct activation.

### What the Description Does

- `Use when: thinking through problems, making decisions...` → Tells model conditions
- `Triggers: "help me decide", "which should I"...` → Exact phrases to pattern-match
- `AUTOMATIC ACTIVATION: Use whenever generating prose...` → Forces activation
- `Content types: blog posts, emails, essays...` → Output format matching

### How to Identify a Bad Description (Detection Signals)

Check for these red flags. ANY ONE indicates the description will under-trigger:

| Signal | Example | Problem |
|--------|---------|---------|
| **Generic name, no triggers** | `"Systematic approach to diagnosing service connectivity issues"` | Model can't tell when to fire. Needs "Use when: connection refused, port issues." |
| **No "Use when:" or "Triggers:"** | `"Read, search, create, and edit notes in the Obsidian vault"` | Model has no trigger conditions to match against. May never fire. |
| **Passive framing** | `"Helps with managing Linear issues"` | "Helps with" is weak. Use active: "Manage Linear issues via GraphQL." |
| **Describes WHAT not WHEN** | `"Comprehensive PDF manipulation toolkit for extracting text"` | Tells what it does but not when to invoke it. |
| **Keyword stuffing** | `"...and much more, etc., various tasks"` | Adds token cost without adding trigger value. |
| **Too short (<8 words)** | `"For documents"` | No trigger surface at all. |
| **Wrong person** | `"You can use this to process data"` | Second person. Description should be in third person. |

**Assessment framework by skill type:**

| Skill Type | Bad Signal | Good Signal |
|-----------|-----------|-------------|
| Distinctive name (axolotl, vllm) | None of these apply | `"Tool: what it does."` is fine — name IS trigger |
| Generic name (troubleshooting, review) | Missing "Use when:" | Has "Use when:" + 3+ trigger phrases |
| High-priority S-tier | Only 1-2 triggers | Has 10+ triggers with "Triggers:" section |

**For detailed fix guidance** (how to rewrite bad descriptions, before/after examples,
tiered length recommendations), see `references/description-research-findings.md`.

### What NOT to Do

❌ **Do NOT strip "Use when:" preamble** — It signals "these are activation conditions"
❌ **Do NOT remove trigger phrases** — They're the matching surface. More = better recall
❌ **Do NOT condense trigger lists** — 40 triggers is BETTER than 5
❌ **Do NOT shorten descriptions below trigger coverage needs** — Hurts activation accuracy

### What CAN Safely Be Trimmed

| Element | Why | Typical savings |
|---------|-----|----------------|
| Version strings in description | Already in `version:` frontmatter field | ~5 tokens each |
| URLs in description | Belong in SKILL.md body or references | ~10 tokens each |
| Redundant boilerplate | "This skill should be used when" → "Use when" | ~3 tokens each |
| Markdown artifacts bleeding into frontmatter | Fix YAML parsing boundary | ~5-15 tokens |

### Realistic Token Budget

With 260 skills at ~47 tokens avg = ~12,330 total.
Safe trimming (no trigger removal) saves at most ~400-800 tokens.
**Under 10K is achievable; under 5K requires architecture changes (tiered descriptions).**

Do not promise 5K unless the user explicitly accepts reduced trigger coverage.

### Assessment Criteria

| Category | Assessment | Action |
|----------|-----------|--------|
| Has "Use when:" + 10+ triggers | Excellent trigger coverage | Keep as-is |
| Has "Use when:" + 3-9 triggers | Adequate coverage | Could add more triggers |
| Has "Triggers:" with quoted phrases | Strong pattern-matching | Keep as-is |
| Has no "Use when:" or triggers | No activation mechanism | May never fire. Needs triggers or identify as junk. |
| Has only a one-liner (Tool: description) | Bundled-style concise | OK if tool name is self-explanatory |
| Has version/URL info bleeding in | YAML parsing issue | Clean up frontmatter boundary |

## Resource File Understanding

Resource files (`references/`) do NOT need YAML frontmatter descriptions.
They are loaded when the model reads the SKILL.md body and encounters a reference:

```markdown
For the scoring rubric, see `references/scoring-rubric.md`.
```

The model decides to load the file because the SKILL.md body INSTRUCTED it to.
No frontmatter required. The filename should be descriptive enough for the model
to know what it contains (`troubleshooting.md`, not `stuff.md`).

### When Filenames ARE a Problem

| Problem | Example | Fix |
|---------|---------|-----|
| Cryptic names | `ref1.md`, `notes.md` | Rename to `architecture.md`, `patterns.md` |
| Duplicate names across skills | `troubleshooting.md` in 10 skills | OK — they're in different skill dirs |
| Missing reference files | SKILL.md says see X but X doesn't exist | Create or remove reference |

### What to Check in Resource Files

- [ ] Files referenced in SKILL.md actually exist
- [ ] No orphaned files (not referenced from SKILL.md)
- [ ] Filenames are descriptive of content
- [ ] No circular references (ref A loads ref B that loads ref A)
- [ ] Not bloated with content that belongs in SKILL.md body

## Description-Only Audit Mode

When the task is specifically about description quality (not full skill audit):

### 1. Extract All Descriptions
Programmatically extract `description:` field from every SKILL.md.

### 2. Calculate Token Cost
Format: `skill-name (category/path): description text`
Count tokens (characters ÷ 4). Sum total. Report vs target.

### 3. Check for Trigger Coverage
- Does it have "Use when:" or "Triggers:"?
- How many trigger phrases?
- Are they specific enough?
- Would the model actually fire this skill?

### 4. Identify GENUINE Waste (not trigger data)
- Version strings duplicating frontmatter
- URLs in description
- YAML parsing artifacts (markdown leaking into frontmatter)
- Truly empty descriptions

### 5. Categorize by Origin
- **Bundled**: Assess trigger coverage. Don't modify — may be restored on update.
- **User-created**: Present trigger coverage analysis. User decides on changes.
- **Hermes-created**: Fix trigger coverage if missing. Add "Use when:" pattern.
- **Third-party**: Assess. Suggest improvements but may revert on resync.

### 6. Propose Changes
For each change, explain WHY it's safe (doesn't reduce trigger coverage).
Use OLD → NEW format only for genuine waste removal or trigger ADDITION.
Do NOT propose stripping triggers.

## Integration with Skill Ecosystem

### Progressive Loading Strategy
```
TIER 1 — Always Loaded:     High-utility descriptions (<5k tokens)
TIER 2 — On Match:          Full SKILL.md when trigger phrase matches
TIER 3 — Undeployed:        Edge-case skills, manually triggered only
```

### Audit Cadence
- **Monthly**: Quick scan for new hermes-created skills (curator handles this)
- **Quarterly**: Full ecosystem audit (bloat, duplicates, quality drift, token budget)
- **Per cleanup request**: Deep read + categorization

## Related Skills
- `skill-ecosystem-audit` — Automated bash-based scan of skill directory metrics
- `prd-audit-and-gap-analysis` — For auditing PRD document collections
- `template-evolution-audit` — For compliance/drift analysis on document templates

## Reference Files

### Detailed rubrics and templates:
- **`references/scoring-rubric.md`** — 100-point quality assessment rubric (10 categories) + cross-skill comparison protocol + marketplace gap analysis methodology + merging protocol. Use this when comparing two skills that do similar things to determine which is better, or when evaluating whether to adopt a marketplace skill. See the Comparison section for when to use this.
- **`references/audit-report-template.md`** — Standardized audit report format
- **`references/pre-curate-detection.md`** — Detailed heuristics for identifying auto-generated junk skills
- **`references/description-revision-guide.md`** — Complete guide for revising descriptions with before/after examples
- **`references/resource-file-audit.md`** — Reference file assessment methodology

### Templates:
- **`references/templates/skill-audit-report.md`** — Blank report template for new audits
- **`references/templates/individual-skill-assessment.md`** — Per-skill assessment template
- **`references/templates/description-revision-template.md`** — Template for bulk description revisions

### Key Reference: Research Findings on Description Mechanics

**`references/description-research-findings.md`** — Comprehensive research across 15+
authoritative sources (Anthropic docs, Hermes Agent docs, GitHub issues, community guides)
on how skill descriptions actually work in the system prompt. Covers:

- Why distinctive tool names (axolotl, vllm, notion) don't need "Use when:" but generic
  names (service-troubleshooting, code-review) do
- The 60-char truncation bug (#13944) that proved descriptions ARE the routing signal
- Why skills under-trigger by default and how to compensate
- The Hermes bundled skill pattern (short descriptions without triggers)
- Tiered approach: when to use extensive triggers vs minimal descriptions

This file should also be referenced in any skill-creation skill as a resource, since
understanding description mechanics is essential for authoring skills that fire reliably.


