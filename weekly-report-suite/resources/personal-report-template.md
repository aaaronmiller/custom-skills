# Personal Weekly Report Template

## Purpose

The personal report is Aaron's operating-history record and dashboard source. It can be longer and more technical than the dad report. It should preserve evidence, caveats, carry-over tasks, and dashboard-ready categories.

## Exact structure

```markdown
# Week Ending <Date> -- Personal Weekly Report

## Executive Summary
Short narrative summary. State the week's primary theme and whether work was shipped, designed, tested, or blocked.

## Evidence Reviewed
- Prior weekly report(s): <paths>
- CASS/session sources: <commands or session IDs>
- Git/filesystem sources: <paths>
- User input: <brain dump or corrections>

## Work Done
### <Project>
- [x] <Completed item>
- Evidence: <file path / commit / session / command output>
- Status: shipped/tested/designed/scaffolded/running

## Work In Progress
### <Project>
- Current state:
- Blockers:
- Next validation:

## Work Planned
- [ ] <Carry-over or new planned item>

## Project Pipeline with Carry-Over
**<Project Name (State; Activity):** One-sentence description.
- [x] Completed carry-over item from last week
- [ ] New action for next week

## Metrics and Dashboard Notes
- Sessions:
- Projects touched:
- Commits:
- Files changed:
- Work done / WIP / planned counts:
- Momentum score (if computed):

## Risks / Blockers / Caveats
- <Do not bury caveats; future Aaron needs them.>

## Dad Report Relationship
Explain how the dad report compresses this personal report and which details were intentionally omitted.

## Self-Improvement Notes
- Evidence gap:
- Metric to add:
- Visualization to improve:
- Template/rubric adjustment:
```

## Rules

- Preserve enough evidence that next week's agent can reconstruct the week without asking Aaron to repeat himself.
- Put exact file paths and commands here, not in the dad report.
- Include uncertainty. Use "estimated" or "not verified" where appropriate.
- Keep work planned as real next actions, not aspirations.
- Include carry-over items from the prior week and mark their status.
