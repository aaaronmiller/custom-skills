# Claude Online Weekly Report Source Spec (Distilled)

This file preserves the task-specific instructions Aaron was using in Claude online before this local skill was created.

## Critical first step: conversation history review

Before generating any weekly report:

1. Retrieve recent conversations/sessions for the relevant project/window. In Hermes/local CLI, use `session_search` and CASS (`cass timeline`, `cass search`) instead of Claude online's `recent_chats`.
2. Extract:
   - Work completed during the reporting period
   - Challenges and solutions
   - Mentor feedback
   - Project status transitions
   - Technical decisions
   - Accomplishments and metrics
   - Time/cost investments
   - Methodology experiments
   - Validation results
3. Synthesize findings with explicit user input.

Purpose: minimize redundant user questions by gathering maximum context first.

## Report generation process

1. Review conversation/session history first.
2. Read/use weekly report template and prior examples.
3. Ask missing information only when essential; prefer multiple choice.
4. Generate the report following the exact structure.

## Checkbox tracking system

For the personal report and dashboard data model:

- Split each active project into completed work and next validation/action.
- Completed work uses checked boxes.
- Planned/carry-over work uses unchecked boxes.
- Import last week's unfinished boxes into the current week.
- Completed items appear once more after completion, then are omitted.
- If a project reaches final completion, note that its README should be annotated; do not edit it unless asked.

Example:

```markdown
**Project Name (Completed Phase; Description):** Work completed last week.
- [x] Completed item
- [ ] Next validation task or action item for this week
```

## Quality standards

- One page maximum for dad-facing report.
- Follow template structure exactly.
- Think through details before writing.
- Include metrics and progress from conversation history.
- Do not include email header info or response elements from examples.
- Only output the Subject line and report body for dad-facing final report.

## Canonical dad-facing structure

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

## Durable context from Claude online memory

- Aaron/Ice-ninja is pursuing Agentic Engineer roles through a structured portfolio-first job search.
- Goal: demonstrate operational proof of automation/agentic capability in lieu of traditional corporate work history.
- Mentor meetings are paused until an interview is scheduled unless user says otherwise.
- Consulting relationship with jewelry e-commerce client exists; Texitcoin deliverable was paid.
- GitHub username: `aaaronmiller`; GitHub activity is an important employer-facing assessment metric.
- LinkedIn views are a visibility proxy.
- Report preferences: concise, minimize rejection mentions, incorporate GitHub activity, use humanize-writing and deliberative validation when asked.
- Completed pipeline items should be removed after appearing once as completed.

## Additional local requirement added during skill creation

The local skill must produce not only the dad report but also a personal report and dashboard bundle for an HTML/Grafana-style project history site. The HTML/dashboard component should improve over time through the self-improvement loop.
