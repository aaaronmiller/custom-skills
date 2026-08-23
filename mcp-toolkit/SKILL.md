---
name: mcp-toolkit
description: |-
  Build MCP (Model Context Protocol) servers, or convert an existing MCP server into a CLI tool, standalone script, or Agent Skill. Two gates: BUILD authors a new server in Python (FastMCP) or Node/TypeScript (MCP SDK) with tool design, evaluation harness, and best practices; CONVERT analyses a running server and generates wrappers that preserve its capabilities while reclaiming the context window an always-loaded MCP server consumes.
  Triggers: "build an mcp server", "create mcp server", "mcp tool design", "fastmcp", "mcp sdk", "model context protocol", "convert mcp", "mcp to cli", "mcp to skill", "replace mcp server", "mcp context waste", "wrap this mcp server", "too many mcp tools".
license: Complete terms in LICENSE.txt
metadata:
  version: "1.0.0"
  supersedes: "mcp-builder, mcp-conversion"
tags:
- mcp
- ai/llm
- api
- coding
grade: A
source: custom
---

# MCP Toolkit

Two operations on one subject, sharing one activation surface.

Both were separate skills. They never collided on triggers - one says "build",
the other says "convert" - but they read the same reference material about what
a well-formed MCP server looks like, and a reader who needs one usually needs
the other in the same session. Deciding to convert a server requires knowing
what a good one looks like; building one is easier having seen why servers get
converted away.

## Choose the gate

**BUILD** - you are authoring a new MCP server, or improving one you own.
Load `references/mcp_best_practices.md` first, then the language guide:
`references/python_mcp_server.md` (FastMCP) or
`references/node_mcp_server.md` (TypeScript SDK).

**CONVERT** - an MCP server already exists and its cost is the problem. Every
connected server occupies the context window whether or not its tools are used,
so a server with many tools is expensive to keep loaded for occasional work.
Load `references/conversion-patterns.md`, then the target-shape guide:
`references/cli-patterns.md`, `references/script-patterns.md`, or
`references/skill-patterns.md`.

If unsure which applies: you are converting when the server runs today and the
complaint is context or startup cost. You are building otherwise.

---

## Gate: BUILD

Four phases. Do not skip phase 1; most poor MCP servers are the result of
mirroring an API's endpoint list without deciding what an agent actually needs.

### Phase 1: Research and plan

**API coverage against workflow tools.** Balance comprehensive endpoint
coverage with specialized workflow tools. Workflow tools are more convenient
for a specific task; comprehensive coverage lets an agent compose operations it
was not designed for. Performance varies by client - some do better with code
execution over basic tools, others with higher-level workflows. When uncertain,
prioritize comprehensive coverage.

**Naming and discoverability.** Consistent prefixes and action-oriented names,
so an agent can find the right tool quickly: `github_create_issue`,
`github_list_repos`.

**Context management.** Concise tool descriptions, and filter/pagination
support so results stay focused.

**Actionable errors.** An error message should tell the agent what to do next,
not only what failed.

Study the protocol at `https://modelcontextprotocol.io/sitemap.xml`; fetch any
page with a `.md` suffix for markdown.

### Phase 2: Implement

Follow the language guide for the chosen runtime. Both cover transport setup,
tool registration, schema definition, and error surfaces.

### Phase 3: Evaluate

`references/evaluation.md` defines the harness. `scripts/evaluation.py` runs it
and `scripts/example_evaluation.xml` is a worked example. An MCP server without
an evaluation is a server whose tool descriptions have never been tested
against a model that has to choose between them.

### Phase 4: Verify connections

`scripts/connections.py` checks the server answers over its declared transport.

---

## Gate: CONVERT

### Phase 1: Analyse the server

```bash
python3 scripts/analyze_mcp.py <server-path-or-command>
```

Inventories tools, schemas, and transport, and reports what the server costs to
keep connected.

### Phase 2: Choose the target shape

| target | when | guide |
| --- | --- | --- |
| CLI tool | the operations are discrete commands a human or agent invokes | `references/cli-patterns.md` |
| standalone script | one workflow, run start to finish | `references/script-patterns.md` |
| Agent Skill | the capability needs instructions and judgement, not just invocation | `references/skill-patterns.md` |

### Phase 3: Generate wrappers

`references/conversion-patterns.md` carries the per-shape templates. Preserve
the server's capabilities; the point is reclaiming context, not reducing what
the agent can do.

### Phase 4: Verify

```bash
python3 scripts/validate_conversion.py <original> <converted>
```

Then walk `references/conversion-checklist.md`. A conversion is complete when
every tool the original exposed is reachable through the replacement.

---

## Anti-patterns

- Converting a server that is genuinely used constantly. The context cost is
  the price of a capability you actually want loaded.
- Building a server that mirrors an API one endpoint per tool, with no thought
  to what a model has to choose between.
- Shipping either without an evaluation. Tool descriptions are the interface,
  and an untested interface is a guess.
