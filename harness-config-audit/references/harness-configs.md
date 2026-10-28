# Per-harness config audits

One section per harness. Record where the config lives, what the build accepts,
what was unset, and what was decided — so the next audit starts from the last
one instead of from nothing.

---

## jcode — audited 2026-08-25, v0.80.1

**Config**: `~/.jcode/config.toml`
**Binary**: `~/.jcode/builds/versions/<ver>/jcode-linux-x86_64.bin` (the thing on
PATH is a shell shim; audit the `.bin`)
**Docs**: `1jehuang/jcode`, 18.5k★, self-described as "the most RAM efficient harness"

### State found

30 bytes, one section:

```toml
[display]
debug_socket = true
```

The entire memory subsystem was dark. `jcode memory stats` reported 0 memories
and gave no indication that memory was switched off rather than merely empty.

### Sections the build accepts

`[acp] [agents] [ambient] [dictation] [display] [display.colors] [features]
[gateway] [hooks] [image] [keybindings] [notifications] [power] [provider]
[safety] [safety.notifications] [safety.notifications.sms] [safety.rules]
[sponsors] [terminal] [tools] [websearch]`

`AgentsConfig` fields, in declaration order — none of these are documented:

```
swarm_model  swarm_gallery_max_pct  swarm_strip_layout
memory_model  memory_sidecar_enabled
memory_rerank_cadence  memory_rerank_votes  memory_rerank_min_agree
memory_embedding_backend  memory_embedding_model  memory_embedding_base_url
memory_embedding_dim
swarm_max_concurrent_agents
```

`FeatureConfig`: `check_updates  memory  swarm  mermaid  auto_poke
message_timestamps  persist_memory_injections  kv_cache_miss_notices
update_channel`

### Applied

```toml
[features]
memory = true
persist_memory_injections = true

[agents]
memory_sidecar_enabled = true
memory_embedding_backend = "local"
memory_embedding_model = "all-MiniLM-L6-v2"
memory_embedding_dim = 384
memory_rerank_cadence = 4
memory_rerank_votes = 3
memory_rerank_min_agree = 2
swarm_max_concurrent_agents = 4
```

Local embedding was chosen over an API backend because embedding runs on every
turn: a network call there is a per-token cost and a latency floor on the hot
path. The bundled `all-MiniLM-L6-v2` is 384-dimensional and needs no key.

`swarm_max_concurrent_agents = 4` is a memory bound, not a preference — 4 × ~300 MB
against a 7 GB host that already carries 3 GB of interactive sessions.

### Verified

```
Project memories: 1   Unique tags: 4
- [fact] ... [quartermaster, loadout, optimal-2026-08, skills]
```

and `~/.jcode/logs/memory-events-2026-08-25.jsonl` showing `embedding_started` ×6,
`embedding_complete` ×1. Config that parses is not evidence; this is.

### Three models, not one

| role | key | constraint |
| --- | --- | --- |
| primary | `-p` / `-m` at invocation | any of 30+ providers |
| embeddings | `memory_embedding_*` | local MiniLM, no key |
| memory sidecar LLM | `memory_model` | **OpenAI or Claude only** |

The sidecar restriction is enforced with `Ignoring unsupported memory sidecar
model override '...'; expected an OpenAI or Claude model`. Tracking issue #679;
unmerged implementation at `alecuba16/jcode`, branch
`feature/memory-sidecar-provider`, adding
`memory_sidecar_backend = auto|openai|claude|provider`.

### Still open

- `[features] swarm` is unset, so `swarm_max_concurrent_agents` has nothing to
  bound. Multi-turn orchestration is unexercised.
- `memory_model` unset, so the sidecar runs on a default rather than a chosen
  model.

---

## ante — audited 2026-08-25

**Config**: `~/.ante/settings.json`
**Repo**: `aaaronmiller/ante-preview` — a personal fork, **not** `antigmalabs/ante`

### Finding

`"modelPool": []`. With an empty pool the router has nothing to route to and
every query falls through to spawning the Claude CLI. Measured: ante's own
processes 4 MB, ante plus what it spawns 679 MB.

This is not a misconfiguration. `ModelPoolEntry` has exactly six fields —
`modelId  capabilityScore  costPer1kInput  costPer1kOutput  contextLimit
enabled` — with **no** `baseUrl`, `apiKey` or provider field. The binary
contains `Claude CLI not found in PATH; install 'claude' or set
ClaudeOptions::cli_path`, and the README's first line says ante is "an
extensible agent runtime **wrapping Claude Code**".

`modelPool` therefore selects *which Claude model*, not which provider. There is
no configuration that makes this build independent of Claude Code, and
`--model claude-sonnet-4-5` still measured 666 MB.

`antigmalabs/ante` (1850★, "self-contained agent harness") is a different
product with the same name and is not installed.

---

## omp — not yet audited

Measured at 460–578 MB per fresh headless worker; an aged interactive session
reached 1,004 MB. Three such sessions were holding 3,016 MB during this audit.
Config location and accepted keys not yet enumerated.

---

## claude-code — not yet audited

Measured 586–1,242 MB per session. Config is `~/.claude/settings.json` plus
`~/.claude/CLAUDE.md`, the latter already managed through Quartermaster's
guidance pipeline.
