# CASS Self-Improvement Protocol

> Progressive-disclosure resource. The prompt-mine SKILL.md references this file
> for post-run reflection. An agent SHALL read this file when the `reflect` action
> is triggered or when ending a prompt-mine invocation.

## Post-Run Reflection Protocol

After delivering the response to the user, execute these steps silently:

### Step 1 — Log the session

```bash
mkdir -p ~/.prompt-mine/refinement-log
cat >> ~/.prompt-mine/refinement-log/$(date +%Y-%m).md << 'REFLECTION'

## Run: $(date --iso-8601=seconds)

### What was requested
<user's request>

### What commands were run
- cass search "..." --robot --limit 10
- cass timeline --today --json
- ...

### What worked well
- The semantic mode caught a relevant hit that lexical missed
- The `--aggregate` flag saved multiple round-trips

### What could be improved
- I should have used `--agent claude` to narrow results
- The limits were too high (50 results when 10 sufficed)
- Could have piped directly to format instead of manual parsing

### Tool use assessment
- Was --robot used consistently? YES/NO
- Was JSON parsed correctly? YES/NO
- Was the right search mode chosen? YES/NO
- Were limits appropriate? YES/NO
- Were aggregations used when available? YES/NO
- Was cass triage the opening move? YES/NO

### Skill refinement suggestions
- [ ] Add a new report type for <gap>
- [ ] Update search flag defaults for <pattern>
- [ ] Fix error handling for <edge case>
- [ ] <any other improvement>

### Pattern notes (repeated across sessions)
- <pattern observed>

REFLECTION
```

### Step 2 — Check for pattern emergence

```bash
grep -c "\[x\] Add" ~/.prompt-mine/refinement-log/*.md 2>/dev/null || echo "0"
```

### Step 3 — Apply refinements when a pattern hits threshold (3+)

When the same suggestion appears 3+ times across any 7-day window:
1. Propose the specific change to the user (file, old text, new text)
2. Ask: "Shall I apply this refinement? Pattern observed N times."
3. If approved, modify the skill file and update all affected agent files
4. Log the refinement in the changelog

## Refinement Types

| Type | What Changes | Threshold |
|------|-------------|-----------|
| **Flag tuning** | Update default `--limit`, `--mode`, `--fields` | 3 observations |
| **New report type** | Add to report types collection | 2 observations of same need |
| **Error handling** | Add recovery steps for known failures | 1-2 occurrences |
| **Agent retargeting** | Update agent file instructions | 3 observations |
| **Removal** | Strip obsolete patterns | 3 obs of better alternative |

## Reading Past Lessons

Before starting any new request, quickly check recent lessons:

```bash
tail -n 60 ~/.prompt-mine/refinement-log/$(date +%Y-%m).md | head -n 60
grep "\[ \]" ~/.prompt-mine/refinement-log/*.md | tail -5
```

This surfaces what's been learned recently and what pending refinements exist.

## Reflection-Driven Agent Files

The agent files (`agents/*.md`) are themselves subject to improvement:

- `agents/skill-refiner.md` is invoked when the reflection backlog hits thresholds
- `agents/report-architect.md` is invoked when a new report type is recognized
- All agent files get updated when the main SKILL.md is refined
