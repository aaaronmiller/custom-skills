---
date: 2026-05-18 10:00:00 PDT
ver: 1.0.0
author: ice-ninja
model: claude-opus-4-7
tags: [strata, research, prior-art, checklist]
---

# Prior Art Research Checklist

Mandatory in Phase 2. The minimum is a floor, not a ceiling. Always survey how others approached the problem and extract reusable patterns and documented pitfalls. Findings land in `intent.md` section 9, never in a separate scratch file.

## Step 1: Local workspace scan (always first)

Check for existing agent configs and related projects that already solve or partially solve the problem: `.claude/`, `.cursor/`, `.agents/`, `skills/`, `.skillshare/`, `.kiro/`, `.windsurf/`, `.openclaw/`, `~/.config/hermes/`, `.specify/`, `openspec/`, and any existing `strata/` tree (an existing tree means this skill does not apply).

## Step 2: Skill registries (minimum 2 searches)

`skills.sh`, `agentskills.io`, `npx antigravity-awesome-skills`, `mcpmarket.com/tools/skills`.

## Step 3: Code search (minimum 3 searches)

Direct problem description, alternative framing, technology-specific framing. For each relevant result extract repository, stars, last commit, license, how they solved the core problem, strengths, weaknesses, and reusable architectural patterns.

## Step 4: Web research (minimum 2 searches)

Current state of the art with the current year, and a comparison or "best of" framing. Also check package registries for sub-problem libraries and practitioner forums for real-world failure reports. Ground every claim in a current search; do not assume training knowledge is current.

## Step 5: Competitive analysis (if commercial)

Three to five closest competitors, feature parity, differentiation, pricing, IP concerns.

## Synthesis

If an existing tool fully solves the problem, stop, surface it with a comparison, and ask the user explicitly whether to proceed and what gap this fills. Do not proceed until confirmed. If it partially solves, document coverage and gaps, adopt its strengths into the design, and define the unique value. If nothing exists, document that the search was thorough and consider why no one has built it.

## Output

Comparison table, patterns adopted, and patterns avoided go into `intent.md` section 9. Process notes go nowhere. If a known project is later found to have been missed, append a ledger entry recording what was missed, when it surfaced, and why it matters, then update `intent.md`.
