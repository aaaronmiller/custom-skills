# Spec Writing Patterns — Reference Guide

**Purpose:** Patterns and anti-patterns for writing `spec-as-designed.md` entries
that feed clean backtranslation. Load during Phase 1 when the project is complex
or when the first draft needs quality review.

---

## Pattern 1: The Problem-First Structure

Every D-XXX entry should be structured so the Problem field naturally generates
a question. The Problem describes WHAT needs solving; the Solution describes
WHAT YOU BUILT to solve it.

**Good:**
```
### D-005: Memory Tiering
- **Problem:** The system needs to retrieve recent session context in under 5ms
  while also maintaining a permanent knowledge archive that can grow indefinitely
  without consuming active compute resources. These two workloads have fundamentally
  different access patterns and cost profiles.
- **Our Solution:** Three-tier architecture: hot/warm (SQLite with FTS5 + vector
  search for sub-ms retrieval), permanent (compiled markdown wiki pages), cold
  (MemVid V2 with video-codec compression for archival).
```

**Bad (solution-first, no problem isolation):**
```
### D-005: Memory Architecture
- **Problem:** We need memory. We built ClawMem, wiki pages, and MemVid.
- **Our Solution:** ClawMem (hot/warm SQLite), wiki (permanent markdown),
  MemVid V2 (cold archival).
```

**Why it matters:** The first version produces a clean question: "For a system
that needs sub-5ms retrieval AND indefinite archival with minimal compute, how
should memory be tiered?" The second version can't produce a question without
referencing the specific technologies.

---

## Pattern 2: Atomic Clauses

Split compound decisions into separate D-XXX entries.

**Bad (bundled):**
```
### D-008: Agent Configuration
- **Problem:** The agent needs flexible configuration.
- **Our Solution:** Support hooks, external MCP servers, and separate
  model/provider configs for agent behavior vs tool calls with fallback chains.
```

This produces one question that covers three independent decisions. If the model
agrees on hooks but disagrees on MCP servers, you can't separate those signals.

**Good (atomic):**
```
### D-008: Agent Extensibility
- **Problem:** The agent needs a mechanism for users to inject custom behavior
  at defined points in the execution lifecycle.
- **Our Solution:** Hook system with pre/post execution hooks on major lifecycle
  events.

### D-009: External Tool Integration
- **Problem:** The agent needs to interact with external tool servers beyond
  its built-in capabilities.
- **Our Solution:** MCP (Model Context Protocol) server support allowing
  registration of external tool providers.

### D-010: Model/Provider Separation
- **Problem:** The agent's reasoning model and tool-execution model may have
  different requirements (cost, latency, capability), and each needs
  independent provider configuration with fallback chains.
- **Our Solution:** Separate model/provider configurations for primary agent
  behavior and tool calls, with independent fallback chains.
```

Three questions, three independent divergence signals.

---

## Pattern 3: Constraint Documentation

Constraints are what separate "the model found something better" from "the model
doesn't know about our constraints." Be explicit.

**Good:**
```
- **Constraints:** Must run locally on Apple Silicon (M-series Mac). No cloud
  dependency. Maximum 8GB RAM for memory subsystem. Must work offline. No
  external database server — embedded storage only.
```

**Bad:**
```
- **Constraints:** Local only.
```

The second version will misclassify divergences. If the model proposes a
PostgreSQL-backed system, "local only" doesn't tell you WHY — is it a security
requirement? A latency requirement? An offline requirement? These different
reasons produce different INFEASIBLE classifications.

---

## Pattern 4: Problem Field Precision

The Problem field must be precise enough that a question derived from it will
produce a focused answer. Vague problems produce vague questions produce
unclassifiable divergences.

**Good:**
```
- **Problem:** When multiple sources provide contradictory information about the
  same topic, the system needs a principled method for determining which version
  to include in the compiled knowledge base, balancing source reliability,
  corroboration, recency, and authoritativeness.
```

**Bad:**
```
- **Problem:** Information conflicts need to be resolved.
```

---

## Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Writing the Problem field with knowledge of the Solution | Problem field subtly references the solution ("we need a tiered approach") | Write Problem as if you DON'T know the solution yet |
| Missing constraints | Model's "better" answer can't be implemented but gets classified as DIVERGENT-BETTER | Fill in every constraint that bounded the decision |
| Non-atomic clauses | One question covers multiple decisions; divergence signal is coarse | Split into separate D-XXX entries |
| Implementation-specific Problem field | Problem field says "SQLite is too slow for..." — presupposes technology choice | Describe the performance REQUIREMENT, not the technology's limitation |
| Omitting rationale | Council can't determine whether your solution was a deliberate tradeoff | Always include rationale with explicit tradeoffs accepted |

---

## Project-Type Patterns

### Agentic Systems
Key decisions to document: agent architecture, tool integration, model selection,
fallback chains, memory/context management, scheduling, confidence scoring,
human-in-the-loop thresholds.

### APIs
Key decisions to document: endpoint design, auth model, rate limiting, error
handling, versioning strategy, data serialization, pagination approach.

### Data Pipelines
Key decisions to document: ingestion method, transformation logic, schema
evolution, error handling, backpressure, checkpointing, idempotency guarantees.

### UI Frameworks
Key decisions to document: component model, state management, rendering strategy,
accessibility approach, theming, internationalization, responsive breakpoints.

---

*Expand with patterns specific to your project type as you write your spec.*
