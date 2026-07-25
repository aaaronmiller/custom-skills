# Prior Art

> **When to read:** when deciding whether to build vs. reuse, or when
> the user asks "is this S-tier".

## The closest structural analogues

### cass — Coding Agent Session Search
**Repo:** github.com/Dicklesworthstone/coding_agent_session_search
**What it does:** Unified TUI and CLI to index and search local coding
agent session history across 11+ providers. Aggregates sessions from
Codex, Claude Code, Cursor, Gemini CLI, Aider, ChatGPT into a single
queryable Tantivy+SQLite corpus.

**What we use:** everything. cass is the primary intent corpus. The
skill shells out to cass for selection and uses raw JSONL for
extraction (see `references/cass_fidelity.md`).

**What cass does NOT do:** intent distillation, spec archaeology,
three-way join, wiki emission, status vectors, meta-learning. Those
are this skill's contribution.

**URL:** https://github.com/Dicklesworthstone/coding_agent_session_search

### cass_memory_system
**Repo:** github.com/Dicklesworthstone/cass_memory_system
**What it does:** Procedural memory for AI coding agents. Transforms
scattered agent sessions into persistent, cross-agent memory. Ships
an MCP HTTP server and a single `cm context "<task>"` call agents
make before starting work.

**What we use:** the `cm context` pattern as inspiration for closing
the loop — sessions start by querying recovered intent. This skill
emits files; cass_memory ships a runtime interface. The two are
complementary, not competitive.

**What cass_memory does NOT do:** spec archaeology, three-way join,
wiki emission. It's memory, not audit.

**URL:** https://github.com/Dicklesworthstone/cass_memory_system

### spec-kit
**Repo:** github.com/github/spec-kit
**What it does:** Toolkit for spec-driven development with AI coding
agents. Slash commands `/specify.init`, `/specify.plan`, `/specify.spec`
produce `requirements.md`, `design.md`, `plan.md`, `tasks.md`,
`constitution.md`. The constitution gates task completion.

**What we use:** the spec lineage files. Phase 3 (spec archaeology)
looks for `/specify.plan` and `/specify.spec` invocations in cass to
find which version of the spec files was attached when the plan was
made.

**What spec-kit does NOT do:** recover intent from session logs,
triangulate with repo reality, produce status vectors. It's the spec
source, not the audit.

**`/reverse` is an open issue** (github.com/github/spec-kit/issues/264)
— a proposed command for brownfield spec recovery. This skill
effectively implements `/reverse` by joining session intent with
repo reality.

**URL:** https://github.com/github/spec-kit

### stackshift
**What it does:** six-gear brownfield pipeline (analyze → reverse
engineer → create specs → gap analysis → implementation planning →
implementation) with greenfield/brownfield routing, shipped as
skills.

**What we use:** the brownfield/greenfield routing concept, adapted
to the user's five lifecycle states.

**What stackshift does NOT do:** use session logs. It works from code
alone, so it infers what the code does, never what was asked for.
That's the gap the session corpus fills.

**URL:** https://lobehub.com/skills/jschulte-stackshift-reverse-engineer

### spec-gen
**Repo:** github.com/HUGO9K/spec-gen
**What it does:** Automates reverse-engineering of a codebase into
OpenSpec specifications. Uses static analysis and AI to extract
specs.

**What we use:** nothing directly, but the concept of
reverse-engineering specs from code is the "repo reality" leg of our
three-way join.

**What spec-gen does NOT do:** use session logs. Same gap as
stackshift.

**URL:** https://github.com/HUGO9K/spec-gen

### Beads
**What it does:** CLI task tracker for agentic workflows. Tracks
dependencies between tasks and only surfaces work that is actually
ready — no blockers, no wasted effort.

**What we use:** the status vector is optionally written as beads so
the sleep-time agent's task queue picks them up automatically.

**URL:** https://github.com/steveyegge/gastown (Beads CLI) and
https://github.com/joshuadavidthomas/opencode-beads (agent integration)

## Academic prior art

### LiSSA (ICSE 2025)
**Paper:** "LiSSA: Toward Generic Traceability Link Recovery through
Retrieval-Augmented Generation"
**What it does:** LLM + RAG for traceability link recovery between
requirements and code. Latest in a 20-year technique lineage: VSM →
LSI → Jensen-Shannon → hierarchical Bayesian → RAG+LLM.

**Why it matters:** TLR is the named research task this skill
contributes to. Two decades of precision/recall/F1 numbers exist.
The skill's contribution: agent logs dissolve the central difficulty
of TLR (intent was never recorded) by providing intent verbatim,
timestamped, in the developer's words, adjacent to the code change.

**URL:** https://arxiv.org/abs/2503.16416 (LiSSA);
  survey: https://arxiv.org/abs/2503.16416

### UserTrace (2025)
**Paper:** "UserTrace: User-Level Requirements Generation and
Traceability Recovery from Software Project Repositories"
**What it does:** multi-agent system that automatically generates
user-level requirements and recovers live trace links (URs → IRs →
code) from software repositories.

**Why it matters:** closest academic analogue to the spec-archaeology
phase. UserTrace generates requirements from code; this skill recovers
them from session logs. The two could compose.

**URL:** https://arxiv.org/abs/2509.11238

### Trace2Skill (Mar 2026)
**Paper:** "Trace2Skill: Distill Trajectory-Local Lessons into
Transferable Agent Skills"
**What it does:** consolidates broad execution trajectories in
parallel into a unified skill directory through inductive reasoning.

**Why it matters:** Trace2Skill distills trajectory-local lessons
into transferable agent skills. That's the frequency→constitution
pipeline (Phase 6 → cross-cutting `standing_constraints.md` page) in
this skill. The two mechanisms were invented independently and are
near-identical.

**URL:** https://arxiv.org/abs/2603.25158;
  code: https://github.com/Qwen-Applications/Trace2Skill

### ALIGNXPLORE (2026)
**What it does:** synthesizes global preference constraints from
sparse interaction traces by inductive reasoning rather than raw-log
retrieval.

**Why it matters:** ALIGNXPLORE's mechanism is near-identical to the
prompt-wiki's standing-constraints page. Same independent invention
pattern as Trace2Skill.

**URL:** referenced in https://arxiv.org/html/2602.22680v2

### LLM Agent Trajectory Analysis survey (Apr 2026)
**Paper:** "A Survey for LLM Agent Trajectory Analysis: From Failure
Attribution to Enhancement"
**What it does:** systematic review of trajectory analysis for
failure attribution and system enhancement in LLM agents.

**Why it matters:** the research field this skill sits in. The
survey covers the technique space; this skill is a specific
contribution to it.

**URL:** https://www.researchgate.net/publication/401193207

### ICLR 2026 — Reward Hacking in Self-Improving Code Agents
**Paper:** "Reward Hacking in Self-Improving Code Agents"
**Finding:** 73.8% of Kernel-Bench optimizations and 46.8% of
ALE-Bench optimizations exhibit proxy gains without gains on held-out
real tasks.

**Why it matters:** the cautionary tale for the meta-learning loop.
The reason this skill requires "improves held-out score without
regressing any component of the metric vector" as the acceptance
criterion for any edit.

**URL:** https://iclr.cc/virtual/2026/10018648

### DELEGATE-52 (2026)
**Paper:** "LLMs Corrupt Your Documents When You Delegate"
**What it does:** benchmark using round-trip backtranslation as
reference-free evaluation. Key property: no annotation of
intermediate states required.

**Why it matters:** the backtranslation skill (tangential attachment
in the transcript) is the measurement instrument for this system.
Round-trip backtranslation as reference-free evaluation is already
formalized; the skill's distinction is triangulation (multiple sources
sharing a latent cause) vs. round-trip (seed document + known inverse).

**URL:** https://arxiv.org/abs/2604.15597;
  code: https://github.com/microsoft/DELEGATE52

### VeriTrans (2026)
**What it does:** LLM-assisted NL→PL translation with validator-gated
reliability. States that round-trip similarity measures loop
stability, not semantic equivalence.

**Why it matters:** states the limitation the backtranslation skill
also states. Round-trip is not enough; triangulation is needed for
intent recovery.

**URL:** https://arxiv.org/abs/2604.10341

### HELMET (2024)
**Paper:** "HELMET: How to Evaluate Long-Context Language Models
Effectively and Thoroughly"
**What it does:** comprehensive benchmark for long-context LMs across
seven categories including recall, RAG, re-ranking, and
generation-with-citations.

**Why it matters:** the category breakdown shows most frontier models
hold up on recall and RAG as input grows, but degrade badly on
re-ranking and generation-with-citations. The latter is the task shape
here (read transcript, emit typed claims bound to event IDs).

**URL:** https://arxiv.org/abs/2410.02694;
  code: https://github.com/princeton-nlp/HELMET

### Chroma — Context Rot (2025)
**Paper/blog:** "Context Rot: How Increasing Input Tokens Impacts LLM
Performance"
**Finding:** broad evaluation of 18 frontier models found every one
degrades as input length grows. Coherent, well-structured input
degrades attention *more* than shuffled input. Effective capacity is
~60-70% of nominal.

**Why it matters:** grounds the batch-size and item-cap decisions in
Phase 6. Length isn't the binding constraint; homogeneity is.

**URL:** https://www.trychroma.com/research/context-rot

## The genuine contribution

TLR spent twenty years doing information retrieval between requirement
docs and code *because intent was never recorded*. Every technique in
that lineage exists to recover a signal lost at the moment it was
produced, and the precision ceilings in that literature are a
consequence of working from lossy proxies.

The agent-log corpus doesn't have that problem — intent is there
verbatim, timestamped, in the developer's own words, with the code
change adjacent. That's a categorically better input than anything
the field has had, available only because coding agents started
writing everything down two years ago.

The three-way join is good architecture. The observation that agent
logs dissolve the central difficulty of a mature research field is
the actual contribution.
