---
id: agent-handoff
title: Handoffs must be bounded and replayable
updated: 2026-07-09
---

## Give the agent a surface, not a fog

An effective handoff names the document version, target IDs, direct edits, annotations, evidence, proposal decisions, immutable constraints, expected files, and validation commands.

The agent should not have to infer whether a rejected proposal is still available, whether a local draft already replaced source, or whether a section rename permits changing its stable ID.

## Expected result contract

A revision result should report:

- complete, partial, or blocked status;
- base and result versions;
- changed files;
- applied and unapplied requests;
- validations and their outcomes;
- warnings and remaining proposals.

The result becomes easier to review because the request and response share the same addresses.

## Do not hide execution in the browser

The static reference does not send content to a model or repository. That boundary is deliberate. A production integration may add a server route, but credentials remain server-side, payloads are validated, and every accepted result appends history and a worklog.

The agent is powerful machinery. The handoff is the interlock that keeps it from machining the wrong part of the document.
