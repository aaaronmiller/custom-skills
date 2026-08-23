---
name: aaron-job-search
description: Run Aaron's structured Seattle job hunt — small startups first. Use when the user asks for Seattle jobs, startup jobs, Wellfound/AngelList searches, agentic engineering roles, or says "aaron job search" / "find me jobs". Triggers on any request to find, filter, rank, or log Seattle-area positions with fit/income/likelihood scoring.
tags:
- jobs
- career
- seattle
- startups
grade: A
source: custom
---

# Aaron Job Search

Four-hunt, 400-job pipeline for Aaron (Cheta) — Seattle area, small companies preferred, all roles including agentic engineering.

## When to Use

User says: "find me jobs", "seattle jobs", "wellfound", "angel list", "startup jobs nearby", "aaron job search", "hunt for jobs". Default location is Seattle unless overridden. Always attempt to locate Aaron's resume first (see Resume Discovery).

## Resume Discovery

Before scoring jobs, try to load Aaron's resume to calibrate likelihood/fit:

1. **Local scan** (no network): search Windows partition + Linux home for resume files
   - Windows: `/mnt/c/Users/*/Documents/`, `/mnt/c/Users/*/Downloads/`, `/home/cheta/Documents/`
   - Patterns: `*resume*`, `*Resume*`, `*CV*`, `*Aaron*Mc*`, `*Aaron*Meer*`, `*.pdf` with resume-like names
   - `find <dir> -maxdepth 3 -type f \( -iname "*resume*" -o -iname "*cv.*" \) 2>/dev/null`
2. **Indeed**: if local not found, prompt user for Indeed URL or search `site:indeed.com` for profile
3. **Fallback**: if neither found, log `resume: not found <timestamp>` and proceed with profile inferred from browsing/wiki/downloads (do not block the hunt)

When resume is found, extract: title, years, stack, domains, education (UW CHID), location. Feed into scoring rubric Likelihood and Skill Leverage.

## Hunt Architecture

```
Hunt 1 (100) → Evaluate → Refine Skill → Hunt 2 (100) → Merge & Re-rank Top 100
      → Hunt 3 (100) → Merge & Re-rank → Hunt 4 (100) → Final Top 100 + Minor Leagues (300)
```

- **No limit per hunt** — aim 100, log overflow.
- **Filter step** after each hunt: merge new 100 with current Top 100 → re-rank → keep best 100, demote rest to Minor Leagues.
- **Minor Leagues** carries same fields as Top 100 (never stripped).
- **Log everything**: every site scanned, every job reviewed, timestamp, date of assessment.

### Angles — Different Each Hunt

Pick a different angle per 100. See [angle-library.md](references/angle-library.md).

1. **Angle 1 — Wellfound / AngelList small startups (2–50, Seattle filter)**
2. **Angle 2 — Built In Seattle + GeekWire 200 under-the-radar**
3. **Angle 3 — Remote-first but Seattle-friendly + YC / TinySeed alumni**
4. **Angle 4 — Niche-fit: AI infra / security / hardware / repair (profile-matched)**

Each hunt starts with: **Target → Rationale → Things Learned From Prior Hunts** (3-section header).

### Scoring — 6 Factors (see scoring-rubric.md)

Every job scored 1–10 on:

1. **Likelihood of success** — skill match, years required vs Aaron's depth, hiring velocity, application friction
2. **Income** — base + equity/bonus, Seattle-adjusted
3. **Growth potential** — learning, promotion path, skill compounding
4. **Stability** — funding stage, runway, reputation, Glassdoor signal
5. **Flexibility / Location** — hybrid/remote, commute, Seattle proper vs Eastside
6. **Skill leverage** — how much Aaron's cross-domain edge (AI agent orchestration, WSL2/systems, hardware repair, semiconductor thesis, knowledge systems) is a differentiator vs commodity

**Ranking:** Weighted composite. Likelihood × 1.5, Income × 1.3, others × 1.0. Tie-break by likelihood.

### Output Per Job (Table Row)

| Logo | Company (link) | Role (application link) | What the business does (1 sentence) | Required to apply | Why Aaron is a good fit | Est. income (Seattle) | Likelihood | Composite |
|------|----------------|-------------------------|--------------------------------------|--------------------|--------------------------|-----------------------|------------|-----------|

- Logo: `https://logo.clearbit.com/<domain>` or company site favicon fallback.
- Links: both live, verified 200 or noted if blocked.
- Income: range from listing or Levels.fyi / Glassdoor / Wellfound band; mark [INFERRED] if estimated.
- Likelihood: `S/A/B/C/D` with one-line reason.

Include collapsible **Minor Leagues** table with identical columns (300 rows max after 4 hunts).

### Site Grading (S/A/B/C/D/E)

After each hunt, grade every site scanned. See [site-grading.md](references/site-grading.md).

- **S** — dense, Seattle-small-startup, high signal, apply in 1 click
- **A** — strong but some noise
- **B** — useful with filtering
- **C** — low density / stale
- **D** — mostly irrelevant / paywalled
- **E** — spam / broken

Log: site URL, date/time scanned, jobs reviewed count, grade, 1-sentence rationale.

### Hunt Log

Append to `hunts/hunt-N.md`:
- Target / Rationale / Learned-from-prior
- Sites scanned table (with grades)
- Top 100 table
- Minor Leagues table
- Overall evaluation: what went well, what dragged, 3 improvements for next hunt
- Skill evaluation: does SKILL.md need changing? If yes, patch it and log diff.

### Deliberative Refinement (Every 100)

After each hunt, run **2 rounds** on the skill itself:
- Round 1: critic pass — does the skill produce the table the user actually wants? Is scoring calibrated?
- Round 2: integration pass — apply fixes, re-check hunt output against SKILL.md
- Log both rounds in `hunts/skill-evolution.md`.


### Browser Bypass Runbook (Hunt 2 Proven)

- **Wellfound SSR pagination:** `https://wellfound.com/location/seattle?page=N` renders server-side without login. Prefer `requests+BeautifulSoup` with salary-line anchors (`$MBk–$UBk` as anchors, backwards scan for role/company/size) over headless Chrome. Browse daemon (`~/.claude/skills/gstack/browse/dist/browse`) times out on burst — use as fallback only. Proven: 4 pages → 66 jobs SSR.
- **Built In regex extraction:** `data-id="job-card"` + `company-title` / `job-card-title` is more reliable than JSON-LD (which lacks company/salary). Seattle URL filter leaks national jobs — pre-filter via company profile employee count when possible.
- **GeekWire 200:** Full list is JS widget behind Cloudflare challenge after SSR shell. iPhone UA via urllib gets shell but no table. Articles (Q1 March + Q2 June) give partial ranks (33/200). Full 200 needs browse with CF solve + wait + snapshot (queued for Hunt 3).
- **General:** If browse times out mid-burst, fall back to `requests` + iPhone UA + salary-line anchor parsing immediately — don't retry browse 3 times.

### Resume Forks

Three variants live in `notes/`: `resume-ai-infra.md` (Platform/Infra/SRE), `resume-solutions.md` (Solutions/Forward Deployed), `resume-startup.md` (Startup Generalist). Scoring must note `resume_fork` per row; `why_aaron_fits` must cite the fork's proof points (HNSW, 300M tokens, cost cut, etc.). Merged Top 100 carries `Fork` column.

### Technique Notes

Keep `notes/technique.md` live — what sources yield S-tier jobs for Aaron specifically, which filters waste time, salary calibration drift.

## References

- [Scoring rubric](references/scoring-rubric.md) — 6-factor 1–10 scales + weighting
- [Site grading](references/site-grading.md) — S→E definitions + log template
- [Angle library](references/angle-library.md) — 4 angles + how to pick the next
- [Hunt template](references/hunt-template.md) — markdown skeleton for each hunt file

## Scripts

- `scripts/rank.py` — composite scoring + re-rank (likelihood×1.5, income×1.3)
- `scripts/site_log.py` — append site scan row with timestamp
- `scripts/hunt_report.py` — scaffold hunt-N.md from template
