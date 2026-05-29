---
date: 2026-05-19
ver: 1.0.0
tags: [clawmem, memvid, dream-agent, integration, adapter]
---

# Tier Integration Specification

## What Uses What

| Component | Type | Runtime | Depends On |
|-----------|------|---------|------------|
| yoloshii/ClawMem | Off-the-shelf | Bun + TypeScript | Nothing (standalone) |
| Dream agent | Custom | Python 3.10+ | ClawMem REST API |
| Wiki pages | Data | Plaintext .md | Dream agent writes |
| MemVid V2 | Off-the-shelf | Unknown (.mv2 format) | ClawMem vault dump |
| ClawMem adapter (existing) | To DELETE | Python SQLite | Nothing — being replaced |

## Changing the buttplug/memory ClawMem Adapter

Current state: `src/buttplug_memory/adapters/clawmem.py` is a 250-line stub
that stores SHA-256 hashes as "embeddings" and computes cosine similarity
on byte arrays. It was never intended to be this — agent hallucination.

**Action:** Delete this file. Replace with an adapter that shells out to
the real ClawMem CLI (or calls its REST API).

### New Adapter Interface

```python
# src/buttplug_memory/adapters/clawmem.py (rewritten)

class RealClawMemAdapter(TierAdapter):
    """Thin wrapper around yoloshii/ClawMem v0.10.1 via REST API."""
    
    def __init__(self, config):
        self.base_url = config.get("clawmem_url", "http://localhost:7438")
        self.api_key = config.get("clawmem_api_key", None)
    
    def query(self, prompt, limit=10, filters=None):
        # POST /retrieve with auto-routing
        # Returns: [{text, score, docid, metadata, source_tier}]
        ...
    
    def ingest(self, content, metadata):
        # POST to ClawMem's file watcher or write .md file
        # into ClawMem's indexed collection
        ...
    
    def health_check(self):
        # GET /health
        ...
```

## What Needs to Run

| Service | How to Start | Notes |
|---------|-------------|-------|
| `clawmem serve` | `clawmem serve --port 7438` | REST API for dream + adapter |
| `clawmem watch` | systemd user unit | Auto-indexes wiki pages/ on change |
| `clawmem-embed.timer` | systemd user timer | Daily embedding refresh |
| Dream agent | systemd idle timer | `dream/scheduler.py --cycle` |
| MemVid encode | Monthly cron | Reads ClawMem vault, writes .mv2 |

## Startup Order

1. `clawmem serve` (REST API)
2. `clawmem watch` (file watcher)
3. `clawmem-embed.timer` (daily embed)
4. Bootstrap ClawMem collections: add wiki/pages/ as a collection
5. Dream agent scheduler (systemd idle timer)
6. MemVid cron (monthly)

## Status Checklist

- [ ] `npm install -g clawmem`
- [ ] `clawmem init` (creates vault at ~/.cache/clawmem/index.sqlite)
- [ ] `clawmem collection add /home/cheta/code/karpathy-wiki/wiki --name wiki`
- [ ] `clawmem update --embed` (initial index + embed)
- [ ] `clawmem setup hooks` (if using Claude Code)
- [ ] `clawmem serve --port 7438 &`
- [ ] Delete old `src/buttplug_memory/adapters/clawmem.py`
- [ ] Write new adapter that uses REST API
- [ ] Install systemd units (watch, embed, dream timer)
- [ ] Schedule monthly MemVid encode
