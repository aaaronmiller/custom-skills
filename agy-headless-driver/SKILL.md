---
name: agy-headless-driver
description: Protocol, prompt encapsulation, and execution architecture for driving high-effort headless Antigravity (agy) sessions with frontier models (Claude Opus 5.5, Claude Sonnet 5.5, Gemini 3 Pro/Flash) under strict quota constraints without compromising iteration depth, reasoning intensity, or artifact quality.
---

# AGY Headless Driver Skill

## Overview

This skill establishes the authoritative execution architecture for dispatching headless Antigravity (`agy -p ...`) agent sessions. It enables automated agents to extract maximum cognitive performance from frontier reasoning models while operating safely within the quota mechanics of the AGY platform.

This protocol explicitly rejects quality-compromising anti-patterns. It does **not** advocate reducing model reasoning effort, downgrading to sub-frontier models for high-stakes tasks, or abandoning multi-pass iteration. Instead, it eliminates infrastructural waste—quadratic context compounding, uncacheable output bloat, and monolithic thread lockouts—allowing frontier models to perform exhaustive, multi-pass deliberation without hitting rate-limit barriers.

---

## 1. The Antigravity (AGY) Harness Architecture

To optimize headless execution, an agent must account for the underlying resource and metering infrastructure:

### A. Dual-Window Quota Mechanics
* **5-Hour Rolling Burst Window:** Meters short-term compute and token throughput. Refreshes continuously every 5 hours.
* **Cumulative Weekly Ceiling:** An overriding safety ceiling across a 7-day rolling period. If cumulative spend breaches this boundary, access to third-party models is locked for the remainder of the weekly cycle (often triggering `429 RESOURCE_EXHAUSTED` with reset timers reaching 160+ hours).
* **Post-Hoc Settlement Hazard:** In-flight execution is permitted to run to completion. When a large autonomous loop finishes, the entire multi-turn token cost is settled against the account ledger at once. An unconstrained loop can clear the 5-hour limit and simultaneously trip the weekly ceiling in a single calculation.

### B. Separated Model Pools
* **Native Gemini Pool (Flash & Pro):** Powered by Google TPU infrastructure and drawn from an elastic, shared token pool. Generous throughput, resilient against multi-day lockouts, and suited for high-volume context ingestion.
* **Third-Party Partner Pool (Claude Opus & Sonnet):** Billed at commercial licensing rates ($15/$75 per million for Opus; $3/$15 for Sonnet). Strictly bounded on paid tiers (e.g., $20 Google AI Pro allocates an estimated $3 to $5 weekly partner wholesale budget).

### C. Context and Caching Limits
* **200k Token Upstream Ceiling:** Hard API limit for Claude models. Context approaching 200k degrades reasoning precision ("lost-in-the-middle") and risks hard HTTP 400 aborts.
* **5-Minute Cache TTL:** Ephemeral prompt cache entries expire after 5 minutes of idle time. Multi-step reasoning loops exceeding 5 minutes between model calls invalidate the cache, incurring full-price re-ingestion.
* **Output Token Asymmetry:** Prompt caching discounts input tokens only (up to 90%). Thinking/reasoning tokens and generated text are **never cached** and are billed at maximum rates ($75/M on Opus). Full document regenerations during iterative passes rapidly drain the partner pool regardless of input cache hits.

---

## 2. The Optimal Encapsulation Pattern (XML Sandwich)

Every prompt dispatched to a headless AGY session must be wrapped using the **XML Sandwich Pattern**. This cleanly separates operating protocols, mission parameters, and resource boundaries, preventing the model from confusing instructions with reference data.

```markdown
<execution_protocol>
[STRICT OPERATING MODE: STATE-EXTERNALIZED REFINEMENT]
You are a stateless, file-based execution engine. You must abide by these non-negotiable operational rules:
1. CONTEXT ISOLATION: Do not front-load entire directories or read large files whole. Ingest data on demand via bounded line ranges or targeted grep probes.
2. ASYMMETRIC MUTATION (DIFFS ONLY): Never regenerate an entire existing artifact during refinement passes. Evaluate first, then output strictly targeted unified diffs or replacement blocks applied directly to the file on disk.
3. PERSISTENCE: Write intermediate critiques to dedicated audit files (`critique-pass-<N>.md`). Mutate target files on disk; do not retain compounding draft transcripts in conversational context.
4. OUTPUT ECONOMY: Suppress conversational pleasantries, status chatter, and polite preambles. Output strictly the requested machine-readable artifacts.
</execution_protocol>

<task_instructions>
  <objective>
    <!-- Precise description of the goal, target artifacts, and expected outcome -->
  </objective>

  <context_references>
    <!-- Explicit paths to files on disk. Instruct model to inspect bounded slices -->
  </context_references>

  <iterative_workflow>
    <!-- Structured definition of passes, lenses, evaluation rubrics, and validation scripts -->
  </iterative_workflow>

  <environment_constraints>
    <!-- Filesystem write boundaries, non-interactive shell flags, tool execution limits -->
  </environment_constraints>
</task_instructions>

<resource_and_quota_guardrails>
### RESOURCE SAFEGUARDS AND CEILINGS
1. Read Bounds: Restrict file inspections to targeted line ranges (`StartLine`/`EndLine`) or exact grep outputs.
2. Generation Budget: Restrict intermediate critique and audit logs to high-signal findings (under 1,000 tokens per pass).
3. In-Place Modifications: Apply patches directly to disk. Do not reprint unaffected sections of target documents.
4. Terminal Exit: Upon completing all assigned passes and verifying validation criteria, output strictly a concise status summary and terminate.
</resource_and_quota_guardrails>
```

---

## 3. Model-Specific Optimization Profiles

### Profile A: Claude Opus 5.5 (High Reasoning Depth)
* **Role:** Architectural design, complex dialectic trade-offs, adversarial security audits, and high-consequence system verification.
* **Cost Profile:** $15.00/M input, $75.00/M output/thinking. Output is the primary cost driver.
* **Non-Compromising Rules:**
  1. **Asymmetric Iteration:** Run genuine sequential passes, but enforce the **Audit & Patch** split. The model outputs a compact critique (`critique-<N>.md` ~800 tokens) detailing specific flaws, then outputs surgical line replacements. It must never regenerate the entire 20k plan.
  2. **No Front-Loaded Corpus Dumps:** Forbid the model from reading entire project histories, living document dossiers, or massive specs upfront. Force on-demand probing against disk.
  3. **Session Decoupling:** For multi-pass chains exceeding 3 to 5 passes, decouple execution into scripted single-turn CLI invocations with file-based handoffs (`after-pass-01/`, `after-pass-02/`). Each invocation begins with a clean context slate, avoiding quadratic input compounding.

### Profile B: Claude Sonnet 5.5 (Autonomous Agentic Workhorse)
* **Role:** Multi-file code generation, extensive test suite authoring, component refactoring, and structured implementation.
* **Cost Profile:** $3.00/M input, $15.00/M output/thinking (5x cheaper than Opus across both dimensions).
* **Execution Rules:**
  1. **Higher Turn Headroom:** Suitable for multi-turn tool-calling loops within a single headless session, provided working state is externalized to disk.
  2. **Bounded Log Ingestion:** Redirect verbose test, lint, or build command outputs to disk files (`cmd > /tmp/run.log 2>&1`) and inspect only failure lines (`grep -E 'ERROR|FAIL' /tmp/run.log`).
  3. **Batch Edits:** Group related edits into single patch passes rather than triggering separate model invocations for minor cosmetic line changes.

### Profile C: Gemini 3.1 Pro & Gemini 3.8 Flash (Elastic Scaled Compute)
* **Role:**
  * **Gemini 3.1 Pro:** Massive document synthesis, project-wide dependency mapping, comprehensive initial drafting, and high-volume AST analysis.
  * **Gemini 3.8 Flash:** Rapid repository reconnaissance, symbol searches, real-time command execution, linting, and continuous verification gates.
* **Cost Profile:** Managed under Google's internal TPU quota pool. Vastly higher throughput; resilient against multi-day third-party lockouts.
* **Execution Rules:**
  1. **Leverage Large Contexts Safely:** Pro models easily handle 500k+ token codebases without quota penalty.
  2. **The Spotter Pattern:** Use Flash to locate files, extract exact line ranges, and summarize facts into a compact scratchpad before handing off to Claude Opus for deep deliberation.

---

## 4. Execution Workflow: The Scripted Pipeline Pattern

When orchestrating complex multi-pass tasks, the calling harness or bash script must manage state externalization:

1. **Clean Directory Roots:** Maintain clear separation between working trees and pass snapshots:
   * Working tree: `/path/to/project/`
   * Snapshot trees: `/path/to/project-snapshots/after-pass-01/`, `after-pass-02/`
2. **Deterministic Validation Gates:** Execute deterministic validation scripts (e.g., linters, structural checkers, eval manifests) at the conclusion of every pass.
3. **Resilience and Auto-Recovery:** If a headless run fails or triggers a temporary rate limit:
   * Verify the last passing snapshot.
   * Parse the reset timer from the error log (`Resets in Xh Ym Zs`).
   * Resume precisely from the uncompleted pass without re-running earlier validated work.
4. **Shell Invariant:** Always use non-interactive file commands (`command cp -f`, `command mv -f`, `command rm -rf`) to prevent headless processes from hanging on interactive confirmation prompts.
