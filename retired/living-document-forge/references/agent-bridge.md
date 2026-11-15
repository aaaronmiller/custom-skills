---
title: Agent bridge reference
version: 2.0.0
---

# Agent bridge reference

## Portable default

The reference browser never invokes a model or writes repository files. It exports a change-request JSON file. An operator or trusted server passes that request to an agent with repository access.

This boundary keeps credentials, filesystem authority, and execution logs outside the browser.

## Local coding-agent route

A local bridge may invoke Codex CLI, Claude Code, or another coding agent with:

- explicit workspace root;
- apply or plan-only mode;
- bounded target IDs and expected files;
- change-request path;
- skill path;
- sandbox and approval policy;
- result schema and result file;
- validation commands.

The prompt should point to structured files rather than embedding the entire rendered document.

## Server-backed route

A Hono or equivalent API may accept a validated change request. It must:

- authenticate the operator;
- validate document ID, schema, and base version;
- reject traversal and unknown target IDs;
- keep provider and repository credentials server-side;
- stage changes before canonical write;
- append history and worklog records;
- return a structured result;
- retain enough information to replay or audit the operation.

## Credentials

Never place secrets in:

- browser local storage;
- manifest or Markdown;
- annotations;
- change requests;
- worklogs;
- exported archives;
- model prompts that may be logged.

## Failure recovery

If an agent partially edits files and validation fails:

- preserve the request and run logs;
- report the inconsistent state;
- do not claim completion;
- revert only with explicit authorization or a verified version-control operation;
- return which files changed and which checks failed.
