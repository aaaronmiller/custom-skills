---
date: 2026-05-18 10:00:00 PDT
ver: 1.0.0
author: ice-ninja
model: claude-opus-4-7
tags: [strata, data-architecture, context-derivation, hosting]
---

# Data Architecture Decision Guide

Reference for Phase 3. These decisions are derived by the system into `context.md`, each cited back to an `intent.md` constraint and, where it exists, a ledger entry. They are never authored by the human.

## Storage type decision

Does the system persist data at all. If no, client-side or in-memory only; stop. If yes, is it primarily relational. If relational and over 10GB or concurrent multi-user writes, a server relational store; otherwise single-file relational. If not relational: key-value or document shaped goes to a document or key-value store depending on schema variability; graph-structured goes to a graph store or relational with recursive queries if the graph is secondary; similarity-searched goes to a vector store; time-series goes to a partitioned or time-series store; otherwise simple file storage.

## Schema principles

Relational: normalize to third normal form first, denormalize only when a recorded read pattern demands it, document every denormalization. Standard elements: sortable non-leaking id, created and updated timestamps, soft delete unless hard delete is an intent requirement. Index columns used in filtering, joining, and ordering; composite indexes put equality columns before range columns; partial indexes for filtered queries. Document stores: embed when accessed together and small and rarely updated, reference otherwise; keep nesting shallow. Key-value: namespaced keys, TTL on all ephemeral data.

## Access pattern classification

Read-heavy favors caching and materialized views. Write-heavy favors write-optimized storage and batched async writes. Append-only favors partitioned time-indexed storage. Search-heavy favors a dedicated search or vector index. Each entity's pattern is recorded as a derivation input in `context.md` section 3.

## Hosting derivation

The deployment target is an `intent.md` constraint, not a choice made here. This guide derives the data and infrastructure that satisfy that constraint. Edge and cost-sensitive and static-or-API workloads suit edge isolates with their paired edge data stores. Background jobs and long-running and SSR suit a serverless or always-on host with its paired managed stores. Full control, GPU, or strict privacy suits self-hosting. When the intent constraint changes, this entire derivation is rerun and the delta is appended to the ledger; it is never patched in place.

## Security baseline

TLS in transit always, encryption at rest when storing personal data, least-privilege credentials, input validation before storage, secrets in environment never in repo, automated backups with tested restore, audit trail for sensitive mutation. Each appears in `context.md` section 7 with the intent or spec identifier it satisfies.
