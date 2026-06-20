# Post-Cycle Retrospective

After completing a Bugbear synthesis cycle, answer these questions honestly. Use findings to improve the next cycle.

## Process Quality

### Phase 1: Inventory (Score: __ /5)
- [ ] Did I read EVERY file before forming opinions?
- [ ] Did I correctly identify the best version on first pass?
- [ ] Did I catch duplicates early (before wasting time re-analyzing them)?
- [ ] Did I check the user's workspace for existing infrastructure?
- [ ] Was the scratchpad file inventory table useful? Missing columns?

### Phase 2: Intent Extraction (Score: __ /5)
- [ ] Did I correctly identify the user's ACTUAL intent vs. model suggestions?
- [ ] Did I find the origin statement (earliest description)?
- [ ] Did I track intent evolution across conversations?
- [ ] Could I have extracted the intent faster?

### Phase 3: Idea Harvest (Score: __ /5)
- [ ] Did the synthesis matrix surface ideas I would have missed?
- [ ] Were contradictions identified and resolved correctly?
- [ ] Were unique good ideas from minority files captured?
- [ ] Were code snippets worth preserving identified?

### Phase 4: Ground Truth Research (Score: __ /5)
- [ ] Did I search for existing tools? How many?
- [ ] Did I check the user's ACTUAL codebase for working infrastructure?
- [ ] Did research change the requirements significantly?
- [ ] Was the "reinventing the wheel" trap avoided?

### Phase 5: Synthesis (Score: __ /5)
- [ ] Do the requirements clearly separate "already works" from "needs building"?
- [ ] Does the design extend existing infrastructure rather than replacing it?
- [ ] Are deliverables actionable enough for a build agent to start immediately?

## Timing & Communication

- [ ] Were questions asked at the right time? (after forming a thesis, not before reading)
- [ ] Were too many questions asked at once?
- [ ] Would the user have benefited from an earlier progress update?
- [ ] Was the final presentation clear and concise?

## Output Quality

- [ ] Would a different agent be able to START BUILDING from these deliverables alone?
- [ ] Are the requirements specific enough to prevent misinterpretation?
- [ ] Is the design concrete enough (types, interfaces, pseudocode) to guide implementation?
- [ ] Were all user constraints honored (tech stack, privacy, existing tools)?

## Cycle Score

| Category | Score |
|----------|-------|
| Phase 1: Inventory | __ /5 |
| Phase 2: Intent | __ /5 |
| Phase 3: Harvest | __ /5 |
| Phase 4: Research | __ /5 |
| Phase 5: Synthesis | __ /5 |
| **Cycle Average** | **__ /5.0** |

Scale: 1=Failed · 2=Major gaps · 3=Adequate · 4=Good · 5=Excellent

## Key Failures (Be Honest)

List the top 3 things that went wrong or could have been better:

1. [Failure 1] → [How to prevent next time]
2. [Failure 2] → [How to prevent next time]
3. [Failure 3] → [How to prevent next time]

## Improvements for SKILL.md

Based on this retrospective, list any changes to make to the Bugbear skill:

- [ ] [Change 1]
- [ ] [Change 2]
- [ ] [Change 3]

---

## AgentForge Session Retrospective (Built-In Lesson)

This is the retrospective from the FIRST use of the Bugbear process (before the skill existed), used to calibrate the skill design:

### What Went Well
- File inventory was thorough and correctly identified spec-v2.md as best
- Market research (8+ tools) prevented reinventing the wheel
- Duplicate detection (paste1.md = Z-transl.md) saved analysis time
- Requirements doc had clear user stories and functional requirements

### What Went Wrong
1. **CRITICAL: Missed existing infrastructure** — Built requirements for a system that replaces sync.sh + skillshare, when the user already had a 759-line working sync system. The FIRST thing to do should have been checking the user's actual codebase, not just the files in the target folder.
   → **Fix:** Phase 4 (Ground Truth Research) now mandates checking the user's workspace before writing requirements.

2. **Asked questions too late** — Already wrote full requirements and design before asking clarifying questions. User's answers (e.g., "all tools equal priority", "SkillScope IS core") required a complete rewrite.
   → **Fix:** Phase 2 (Intent Extraction) now runs BEFORE synthesis. But questions are asked AFTER showing deliverables — users give better answers with context.

3. **Spec v1 was dismissed as "irrelevant"** — The SkillScope spec was labeled as "narrow" and deferred to Phase 4. The user corrected this — SkillScope is core functionality for deciding which skill to keep.
   → **Fix:** Phase 3 (Idea Harvest) now explicitly warns against dismissing docs. Even narrow docs may contain core features.

4. **Scratchpad was unstructured** — Free-form notes made it hard to track which ideas came from which files.
   → **Fix:** Scratchpad template now has structured tables for inventory, synthesis matrix, and gap analysis.

5. **No code snippets preserved** — The spec documents contained TypeScript schemas, YAML formats, and algorithm pseudocode that were valuable. They were summarized but not preserved in a form a build agent could use.
   → **Fix:** Phase 3 now explicitly preserves code snippets in starter-code.md reference file.
