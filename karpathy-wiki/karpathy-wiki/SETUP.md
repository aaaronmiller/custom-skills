# Karpathy-Wiki Setup Guide

## Quick Start

```bash
# 1. Ensure prerequisites
cd ~/code/skills-USER/karpathy-wiki

# 2. Run the setup script (detects your agents automatically)
./setup.sh

# 3. Or with a preset for your hardware
./setup.sh --preset lightweight   # CPU-only, minimal
./setup.sh --preset balanced      # GPU-assisted, default
./setup.sh --preset high-quality  # Full RAG pipeline
./setup.sh --preset max-context   # All encodings, long archive

# 4. See what would happen without touching anything
./setup.sh --dry-run

# 5. Selective setup
./setup.sh --skip-clawmem --skip-mcp --skip-dream
```

The setup script handles **all 7 agents**:

| Agent | Configures |
|-------|-----------|
| [Pi Agent](https://pi.ai) | Skill symlink, plugin, MCP, hooks |
| [Claude Code](https://claude.ai) | Skill symlink + .md, MCP, hooks |
| [Ante Agent](https://github.com/ante) | Skill symlink, MCP |
| [Hermes Agent](https://hermes.ai) | Skill, MCP, shell hooks |
| [KiloCode](https://kilocode.ai) | Skill symlink, MCP, hooks dir |
| [OpenCode](https://opencode.ai) | Skill symlink (incl. cross-discovery), MCP |
| [Antigravity CLI](https://github.com/) | Direct data access via `~/.local/share/ai-wiki/` |

For full options: `./setup.sh --help`

---

## Architecture

```
┌─────────────────────────────────────────────┐
│  ~/.local/share/ai-wiki/     (data)         │
│  ├─ raw/          ← Agent drops sources     │
│  ├─ pages/        ← Compiled knowledge      │
│  ├─ .meta/        ← Dream agent state       │
│  └─ .git          ← Version history         │
└──────────────────────┬──────────────────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
┌──────────────────┐    ┌──────────────────────┐
│ ClawMem          │    │ Dream Agent          │
│ localhost:7438   │    │ (systemd idle timer) │
│ MCP + REST API   │    │ 6-phase sleep-time   │
│ Hybrid search    │    │ compile loop         │
└──────────────────┘    └──────────────────────┘
          │                         │
          └────────────┬────────────┘
                       ▼
      ┌──────────────────────────────────┐
      │ Pi / Claude / Ante / Hermes /    │
      │ KiloCode / OpenCode / Antigravity │
      │ Read wiki via ~/.local/share/    │
      └──────────────────────────────────┘
```

**Backend services** (all optional, auto-fallback):

| Service | Port | Purpose |
|---------|------|---------|
| `clawmem-rest` | 7438 | REST API + MCP server |
| `clawmem-llama-embed` | 8088 | GPU embedding server |
| `clawmem-llama-expand` | 8089 | Query expansion LLM |
| `clawmem-reranker` | 8090 | Cross-encoder reranking |

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| **Python 3.10+** | For dream agent |
| **Git** | For wiki versioning |
| **Bun 1.0+** | For ClawMem (`curl -fsSL https://bun.sh/install \| bash`) |
| **systemd --user** | Linux only (timer); macOS uses launchd |
| **GPU 4GB+ VRAM** | Recommended for ClawMem embedding (CPU fallback works) |

---

## Manual Steps (if setup.sh is insufficient)

### 1. Install ClawMem

```bash
# Option A: npm (recommended)
npm install -g clawmem

# Option B: From source
git clone https://github.com/yoloshii/clawmem.git ~/git/ClawMem
cd ~/git/ClawMem && bun install
ln -sf "$PWD/bin/clawmem" ~/.bun/bin/clawmem

# Bootstrap wiki vault
clawmem bootstrap ~/.local/share/ai-wiki/pages --name wiki
```

### 2. Install MemVid (optional)

```bash
git clone https://github.com/yoloshii/memvid.git ~/git/memvid
cd ~/git/memvid && bun install
ln -sf "$PWD/bin/memvid" ~/.bun/bin/memvid
memvid init && memvid start  # Port 7440
```

### 3. Start GPU services (optional — ClawMem falls back to in-process)

```bash
llama-server -m embeddinggemma-300M-Q8_0.gguf \
  --embeddings --port 8088 -ngl 99 -c 2048
llama-server -m qmd-query-expansion-1.7B-q4_k_m.gguf \
  --port 8089 -ngl 99 -c 4096
llama-server -m Qwen3-Reranker-0.6B-Q8_0.gguf \
  --reranking --port 8090 -ngl 99 -c 2048
```

### 4. Start the dream agent

```bash
# Systemd timer (Linux)
./setup.sh --skip-clawmem --skip-mcp --skip-skills --skip-hooks --skip-env

# Or manually
python3 dream/dream_agent.py --idle 600

# Or daemon mode (macOS)
python3 dream/scheduler.py --daemon
```

---

## Configuration Reference

All configuration is defined in `config.schema.yaml`:

```bash
# List all configurable parameters
grep -E '^\s+\w+:' config.schema.yaml | head -50
```

Key presets:

| Preset | ClawMem | MemVid | Dream Budget | LLM Model | Use Case |
|--------|---------|--------|-------------|-----------|----------|
| `lightweight` | BM25 only | Off | 10%/30min | Llama 3.2 1B | Laptop, CPU-only |
| `balanced` | BM25+vector | Off | 25%/2hr | Llama 3.2 3B | Desktop, default |
| `high-quality` | Full+rerank | On | 50%/4hr | Qwen 2.5 7B | Research, knowledge |
| `max-context` | Deep+all | All encodings | 75%/8hr | Qwen 2.5 14B | Archives, long-term |

---

## Verification

```bash
./setup.sh --dry-run               # Preview changes
./setup.sh --preset balanced       # Apply and verify
```

Or check manually:

```bash
[ -d ~/.local/share/ai-wiki/pages ]        && echo "✅ data dir"
[ -L ~/ai-wiki ]                           && echo "✅ symlink"
curl -sf http://localhost:7438/health      && echo "✅ ClawMem"
python3 dream/dream_agent.py --idle 10 --quiet 2>/dev/null && echo "✅ dream agent"
```

---

## File Reference

| File | Location |
|------|----------|
| **Setup script** | `skills-USER/karpathy-wiki/setup.sh` |
| **Config schema + presets** | `skills-USER/karpathy-wiki/config.schema.yaml` |
| **Quick install** | `skills-USER/karpathy-wiki/install.sh` |
| **SKILL.md** | `skills-USER/karpathy-wiki/skill/SKILL.md` |
| **Dream agent** | `skills-USER/karpathy-wiki/dream/dream_agent.py` |
| **Scheduler** | `skills-USER/karpathy-wiki/dream/scheduler.py` |
| **Session hooks** | `skills-USER/karpathy-wiki/hooks/pre_compact.py`, `session_end.py` |
| **Pi plugin** | `skills-USER/karpathy-wiki/plugin/plugin.json` |
| **Specs** | `skills-USER/karpathy-wiki/specs/` (8 files) |
| **Wiki data** | `~/.local/share/ai-wiki/` |
| **ClawMem source** | `~/git/ClawMem/` |
| **ClawMem vault** | `~/.cache/clawmem/index.sqlite` |

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|------|
| Dream agent exits with no output | ClawMem not running | `clawmem start` or check `localhost:7438` |
| Wiki pages not updating | Collection not indexed | `clawmem collection add ~/.local/share/ai-wiki/pages --name wiki` |
| systemd timer never fires | `IdleWaitSec` too strict | Check `loginctl show-user $USER --property=IdleSinceHint` |
| MCP tools not visible | MCP not registered | `./setup.sh --skip-clawmem --skip-skills --skip-env` |
| Dream agent timeout | Budget > cycle limit | `--idle 300` or reduce `budget_percentage` in config |
| `clawmem` not found | Bun/bin not in PATH | Add `export PATH="$HOME/.bun/bin:$PATH"` to shell rc |
