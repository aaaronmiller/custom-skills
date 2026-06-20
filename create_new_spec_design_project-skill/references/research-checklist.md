# Prior Art Research Checklist

> Mandatory research protocol executed in Phase 2. The minimum is a floor, not a ceiling.

## Research Sequence

### Step 1: Local Workspace Scan (always first)

Check for existing agent configs and related projects that may already solve or partially solve the problem:

```
Directories to check:
- .claude/          (Claude Code configs, skills, commands)
- .cursor/          (Cursor rules and configs)
- .agents/          (Cross-platform agent configs)
- skills/           (Project-level skills)
- .skillshare/      (Skillshare-managed skills)
- .kiro/            (Kiro specs)
- .windsurf/        (Windsurf configs)
- .openclaw/        (OpenClaw configs)
- ~/.config/hermes/ (Hermes agent configs)
- .specify/         (SpecKit project files)
- openspec/         (OpenSpec project files)
```

### Step 2: Skill Registries (minimum 2 searches)

Check if existing skills or tools already handle this use case:
- `skills.sh` catalog
- `agentskills.io` registry
- `npx antigravity-awesome-skills` catalog
- `mcpmarket.com/tools/skills` listings

### Step 3: Code Search (minimum 3 searches)

Search GitHub for existing open-source projects solving the same problem:

**Query construction:**
- Search 1: Direct problem description (e.g., "chrome grammar extension local LLM")
- Search 2: Alternative framing (e.g., "offline grammar checker browser")
- Search 3: Technology-specific (e.g., "Harper fork messaging bot")

**For each relevant result, extract:**
- Repository: name, stars, last commit date, license
- Architecture: how they solved the core problem
- Strengths: what they do well
- Weaknesses: where they fall short
- Patterns: reusable architectural decisions

### Step 4: Web Research (minimum 2 searches)

Search for current state of the art and recent developments:
- Search 1: "[problem domain] 2026" or "[problem domain] latest"
- Search 2: "[problem domain] comparison" or "best [solution type]"

**Also check (as appropriate):**
- npm / PyPI / crates.io for libraries solving sub-problems
- Reddit / HN / Stack Overflow for practitioner perspectives
- arXiv / Google Scholar for research papers (if domain is academic/ML)
- Community lists (awesome-*) for curated alternatives

### Step 5: Competitive Analysis

If the project has commercial potential:
- Identify 3-5 closest competitors
- Map feature parity (what they have that this project needs)
- Map differentiation (what this project offers that they lack)
- Analyze pricing models (free tier availability, cost structure)
- Check for patent/IP concerns in the space

## Synthesis Protocol

After research is complete:

1. **If existing tools fully solve the problem:**
   - STOP. Surface them to the user immediately.
   - Present a comparison table: existing solution vs proposed project.
   - Ask explicitly: "Given [tool X] exists, do you still want to build this? If so, what specific gap does your project fill?"
   - Do not proceed until user confirms.

2. **If existing tools partially solve the problem:**
   - Document what they cover and what they miss.
   - Incorporate their strengths into the project's design.
   - Define the project's unique value proposition against them.
   - Note lessons from their approaches (architecture, UX, community patterns).

3. **If no existing tools found:**
   - Document the search was thorough (list searches performed).
   - Note this is either a genuinely novel problem space or a niche the market has not addressed.
   - Consider why no one has built this (too niche? too hard? recently made possible?).

## Output Location

Research findings go into the requirements document under:
- Section 8: Prior Art Analysis
  - 8.1: Existing Solutions (comparison table)
  - 8.2: Patterns Adopted (borrowed good ideas)
  - 8.3: Patterns Avoided (lessons from others' mistakes)

## Failure Documentation

If a known existing project is later discovered to have been missed:
- Document: what was missed
- Document: when it was discovered
- Document: why it matters
- Update the requirements document's Prior Art section
