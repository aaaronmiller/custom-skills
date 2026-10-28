---
name: harness-config-audit
description: >-
  Audit an agent harness's configuration against its current documentation, so
  that features shipped in an update are actually switched on. An updated binary
  keeps the old config file, and a feature gated behind a key you have never set
  stays dark with no error and no warning — jcode's memory subsystem sat inert
  behind two unset keys, and ante's model router was disabled by an empty
  modelPool. Checks the harness is current, upgrades it when not, enumerates
  every option the build accepts, reports which are unset, and recommends a
  value for each.

  Also owns the model assignment policy: which provider and model to use for
  each role, what they cost, and what to fall back to when a rate limit is hit.

  Use when: auditing a config file, after upgrading a harness, when a documented
  feature "does not work", when adding a new harness, when choosing a model for
  delegated or subagent work, or when a worker hits a per-minute quota.

  Triggers: "audit the config", "check my harness config", "is my config up to
  date", "why isn't this feature working", "config drift", "which model should I
  use", "model assignment", "rate limited", "pick a model for subagents",
  "harness settings", "config.toml", "settings.json".
license: MIT
metadata:
  version: 1.0.0
tags:
  - TOOL
---

# Harness config audit

An agent harness updates. The binary changes; the config file does not. Anything
the new version gates behind a key you have never written stays off, silently —
no error, no warning, and the feature simply appears not to exist.

Two measured examples from this machine:

- **jcode**: the entire memory subsystem was inert. `[features] memory` and
  `[agents] memory_sidecar_enabled` were both unset, and nothing said so. The
  config was 30 bytes and had one section.
- **ante**: `"modelPool": []` meant the model router had nothing to route to, so
  every query fell through to spawning a full Claude Code — 679 MB instead of
  4 MB. The config parsed fine.

Neither is a bug. Both are the same failure: **a default that means "off"
combined with a config written before the feature existed.**

## The audit

### 1. Is the harness current?

Check the installed version against the latest release before auditing
anything — auditing a stale build tells you about options that have since
changed.

```bash
jcode --version && jcode update          # self-updating
omp --version                            # bun upgrade / package manager
claude --version                         # npm -g
ante --version
```

Record the version you audited against. A config audit is only true for one
build.

### 2. Enumerate what the build actually accepts

Documentation lags. The binary does not. Prefer the binary as the source of
truth, and use the docs to learn what each key *means*.

For a Rust binary the config struct field names are in the string table, in
declaration order, usually concatenated:

```bash
strings -n 6 "$BINARY" | grep -E '^\[[a-z][a-z_.]{2,24}\]$' | sort -u   # sections
python3 - <<'PY'                                                        # fields
d=open(BINARY,'rb').read()
i=d.find(b'AgentsConfig')          # the struct name
print(repr(d[i:i+400]))            # fields follow it, run together
PY
```

That is how `memory_embedding_backend`, `memory_embedding_model`,
`memory_embedding_dim` and `swarm_max_concurrent_agents` were found for jcode —
none of them documented anywhere.

For JSON-configured harnesses, look for the serde struct names the same way
(`struct Settings`, `struct ModelPoolEntry`).

### 3. Diff accepted keys against the config file

Three categories, and they need different responses:

| finding | response |
| --- | --- |
| key accepted by the build, absent from config | the audit's real output — decide a value |
| key in config, not accepted by the build | removed upstream; delete it, it is silently ignored |
| key present with a stale value | compare against the recommendation below |

Watch for keys whose default is `false` or `[]`. Those are the ones that hide
whole subsystems.

### 4. Prove the feature actually runs

A key being set is not evidence. Exercise the feature and look for a side
effect — a file, a log line, a process.

```bash
jcode memory stats                              # 0 memories means it is not running
ls ~/.jcode/logs/memory-events-*.jsonl          # embedding_started / embedding_complete
```

Config that parses and does nothing is the normal failure here. Do not report a
key as fixed until something observable changed.

### 5. Recommend a value for every unset key

State the reasoning, not just the value. Cost, memory, and blast radius all
count: `swarm_max_concurrent_agents` is bounded by host memory, not by
preference — a worker costs 275–580 MB and the host has 7 GB.

## Model assignment

`references/model-assignment.md` holds the current policy: which model for which
role, what each costs, measured intelligence scores, and the fallback order for
when a per-minute quota is hit. Read it before choosing a model for delegated
work.

Re-derive it rather than trusting it when more than a month has passed —
catalogues change weekly, and a free model can disappear or stop being free.
`references/model-assignment.md` documents how it was built.

## Per-harness notes

`references/harness-configs.md` records where each harness keeps its config,
which keys were found unset, and what was decided. Add a section when you audit
a new harness; that file is the memory this skill is for.
