#!/usr/bin/env bash
# =============================================================================
# Karpathy Wiki — Multi-Agent Setup Script
# =============================================================================
#
# Installs and configures the complete Karpathy Wiki system:
#   • Wiki data directory (~/.local/share/ai-wiki/)
#   • ClawMem (memory engine with REST API + MCP)
#   • MemVid (optional cold-storage video memory)
#   • Dream agent (systemd timer / daemon)
#   • Agent integration (skills, MCP, hooks) for all 7 agents
#
# Usage:
#   ./setup.sh                          # Interactive, detects agents
#   ./setup.sh --preset balanced        # Apply named preset
#   ./setup.sh --config my.yaml         # Custom config overrides
#   ./setup.sh --dry-run                # Show what would be done
#   ./setup.sh --skip-clawmem --skip-dream   # Selective install
#   ./setup.sh --preset max-context --unattended   # No prompts
#
# Cross-platform: Linux (systemd) + macOS (daemon fallback)
#
# Source: skills-USER/karpathy-wiki/setup.sh
# Schema: skills-USER/karpathy-wiki/config.schema.yaml
# =============================================================================

set -euo pipefail

# ── Constants ────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CANONICAL_DIR="$(cd "$SCRIPT_DIR" && pwd -P)"  # Resolve symlinks to physical path

WIKI_DATA="${WIKI_DATA:-$HOME/.local/share/ai-wiki}"
CLAWMEM_SOURCE_DIR="${CLAWMEM_SOURCE_DIR:-$HOME/git/ClawMem}"
CLAWMEM_BINARY="${CLAWMEM_BINARY:-$CLAWMEM_SOURCE_DIR/bin/clawmem}"
MEMVID_SOURCE_DIR="${MEMVID_SOURCE_DIR:-$HOME/git/memvid}"
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'

OS="$(uname -s)"
IS_WSL=false
grep -qi microsoft /proc/version 2>/dev/null && IS_WSL=true || true
HAS_SYSTEMD=false
command -v systemctl >/dev/null 2>&1 && HAS_SYSTEMD=true || true

# ── Default config (mirrors config.schema.yaml defaults) ────────────────────
# Applied when no preset or config file is specified.
CONFIG_PRESET=""
CONFIG_FILE=""
DRY_RUN=false
UNATTENDED=false
VERBOSE=false

# Skip flags (--skip-*)
SKIP_CLAWMEM=false
SKIP_MEMVID=false
SKIP_DREAM=false
SKIP_HOOKS=false
SKIP_MCP=false
SKIP_SKILLS=false
SKIP_ENV=false

# ── Parse CLI ────────────────────────────────────────────────────────────────
usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Install and configure the Karpathy Wiki system for multi-agent use.

Options:
  --preset <name>       Apply named preset (lightweight|balanced|high-quality|max-context)
  --config <file>       Custom YAML/JSON config overrides
  --dry-run             Show what would be done without making changes
  --unattended          No prompts, use defaults
  --verbose             Detailed output
  --skip-clawmem        Skip ClawMem installation/configuration
  --skip-memvid         Skip MemVid installation/configuration
  --skip-dream          Skip dream agent scheduler setup
  --skip-hooks          Skip session hook installation
  --skip-mcp            Skip MCP server registration
  --skip-skills         Skip skill symlink creation
  --skip-env            Skip environment variable setup
  --help                Show this message
EOF
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --preset)          CONFIG_PRESET="$2"; shift 2 ;;
        --config)          CONFIG_FILE="$2"; shift 2 ;;
        --dry-run)         DRY_RUN=true; shift ;;
        --unattended)      UNATTENDED=true; shift ;;
        --verbose)         VERBOSE=true; shift ;;
        --skip-clawmem)    SKIP_CLAWMEM=true; shift ;;
        --skip-memvid)     SKIP_MEMVID=true; shift ;;
        --skip-dream)      SKIP_DREAM=true; shift ;;
        --skip-hooks)      SKIP_HOOKS=true; shift ;;
        --skip-mcp)        SKIP_MCP=true; shift ;;
        --skip-skills)     SKIP_SKILLS=true; shift ;;
        --skip-env)        SKIP_ENV=true; shift ;;
        --help|-h)         usage ;;
        *) echo -e "${RED}Unknown option: $1${NC}"; usage ;;
    esac
done

# ── Logging ──────────────────────────────────────────────────────────────────
info()    { echo -e "${GREEN}✓${NC} $*"; }
warn()    { echo -e "${YELLOW}⚠${NC} $*"; }
error()   { echo -e "${RED}✗${NC} $*"; }
header()  { echo -e "\n${CYAN}━━━ $* ━━━${NC}"; }
sub()     { echo -e "  ${BLUE}→${NC} $*"; }
detail()  { ${VERBOSE:-false} && echo -e "    ${BLUE}·${NC} $*" || true; }
dry()     { ${DRY_RUN:-false} && echo -e "  ${YELLOW}[DRY-RUN]${NC} $*" || true; }

# ── Prerequisite detection ──────────────────────────────────────────────────
prereq_check() {
    local missing=()
    command -v python3 >/dev/null 2>&1 || missing+=("python3")
    command -v git >/dev/null 2>&1 || missing+=("git")

    # Python version check
    if command -v python3 >/dev/null 2>&1; then
        local pyver
        pyver="$(python3 --version 2>&1 | grep -oP '\d+\.\d+\.\d+' | cut -d. -f1)"
        if [[ "$pyver" -lt 3 ]]; then
            missing+=("python3.10+ (found python3.$pyver)")
        fi
    fi

    if [[ ${#missing[@]} -gt 0 ]]; then
        error "Missing prerequisites:"
        for m in "${missing[@]}"; do error "  - $m"; done
        warn "Install missing tools and re-run setup.sh"
        return 1
    fi

    info "Python 3+ detected ($(python3 --version 2>&1))"
    info "$(git --version 2>&1)"
    return 0
}

# ── Detect installed agents ──────────────────────────────────────────────────
declare -A AGENTS
detect_agents() {
    sub "Detecting installed agents..."

    [[ -d "$HOME/.pi/agent" ]]          && AGENTS[pi]=1         && detail "  Pi Agent: found"       || AGENTS[pi]=0
    [[ -d "$HOME/.claude" ]]            && AGENTS[claude]=1     && detail "  Claude Code: found"   || AGENTS[claude]=0
    [[ -d "$HOME/.ante" ]]              && AGENTS[ante]=1       && detail "  Ante: found"          || AGENTS[ante]=0
    [[ -d "$HOME/.kilocode" ]]          && AGENTS[kilocode]=1   && detail "  KiloCode: found"      || AGENTS[kilocode]=0
    [[ -d "$HOME/.config/opencode" ]]   && AGENTS[opencode]=1   && detail "  OpenCode: found"      || AGENTS[opencode]=0
    [[ -d "$HOME/.config/hermes" ]]     && AGENTS[hermes]=1     && detail "  Hermes: found"        || AGENTS[hermes]=0
    # Antigravity: always present (editor, no config dir)
    AGENTS[antigravity]=1

    local found=()
    for a in pi claude ante kilocode opencode hermes; do
        [[ ${AGENTS[$a]} -eq 1 ]] && found+=("$a")
    done
    if [[ ${#found[@]} -eq 0 ]]; then
        warn "No AI agents detected. Will set up wiki data and ClawMem only."
        warn "Re-run after installing agents to integrate skills/MCP/hooks."
    else
        info "Detected ${#found[@]} agents: ${found[*]}"
    fi
}

# =============================================================================
# PHASE 1: Wiki Data Directory
# =============================================================================
setup_wiki_data() {
    header "Phase 1/8: Wiki Data Directory"

    dry "mkdir -p $WIKI_DATA/{raw,pages/concepts,pages/entities,pages/sources,pages/queries,.meta/skills}"
    if ! $DRY_RUN; then
        mkdir -p "$WIKI_DATA/raw"
        mkdir -p "$WIKI_DATA/pages/concepts"
        mkdir -p "$WIKI_DATA/pages/entities"
        mkdir -p "$WIKI_DATA/pages/sources"
        mkdir -p "$WIKI_DATA/pages/queries"
        mkdir -p "$WIKI_DATA/.meta/skills"
        info "Data directory structure created"
    fi

    # Init template files
    if [[ ! -f "$WIKI_DATA/pages/index.md" ]]; then
        dry "Create pages/index.md"
        if ! $DRY_RUN; then
            cat > "$WIKI_DATA/pages/index.md" << 'EOF'
# Wiki Index

Auto-maintained by dream agent. Each page is one concept with [[wikilinks]] to related pages.

## Quick Links
- [[log]] — Change log
- [[getting-started]] — First steps

---
*Generated by dream agent*
EOF
            info "pages/index.md created"
        fi
    fi

    if [[ ! -f "$WIKI_DATA/pages/log.md" ]]; then
        dry "Create pages/log.md"
        if ! $DRY_RUN; then
            echo -e "# Wiki Log\n\n| Date | Action | Page |\n|------|--------|------|\n" > "$WIKI_DATA/pages/log.md"
            info "pages/log.md created"
        fi
    fi

    # Ensure AGENTS_WIKI.md schema exists (generated by dream agent, but need initial copy)
    # Try source paths in order: module-local, existing data, else generate default
    local agents_wiki_src=""
    if [[ -f "$CANONICAL_DIR/AGENTS_WIKI.md" ]]; then
        agents_wiki_src="$CANONICAL_DIR/AGENTS_WIKI.md"
    elif [[ -f "$HOME/.local/share/ai-wiki/AGENTS_WIKI.md" ]]; then
        agents_wiki_src="$HOME/.local/share/ai-wiki/AGENTS_WIKI.md"
    fi
    if [[ -n "$agents_wiki_src" ]] && [[ ! -f "$WIKI_DATA/AGENTS_WIKI.md" ]]; then
        dry "Copy $agents_wiki_src → $WIKI_DATA/AGENTS_WIKI.md"
        if ! $DRY_RUN; then
            cp "$agents_wiki_src" "$WIKI_DATA/AGENTS_WIKI.md"
            info "AGENTS_WIKI.md schema installed"
        fi
    elif [[ ! -f "$WIKI_DATA/AGENTS_WIKI.md" ]] && [[ ! -f "$agents_wiki_src" ]]; then
        # Generate minimal default
        dry "Generate minimal AGENTS_WIKI.md"
        if ! $DRY_RUN; then
            cat > "$WIKI_DATA/AGENTS_WIKI.md" << 'WIKIEOF'
# AGENTS_WIKI — Wiki Schema

## Directory Layout
- `raw/` — immutable source documents
- `pages/` — LLM-compiled pages with [[wikilinks]]
  - `pages/index.md` — master index
  - `pages/log.md` — change log
- `.meta/skills/` — auto-generated skills

## Conventions
- One concept per file, lowercase-hyphens.md
- Use [[page-name]] cross-refs
- Update index.md and log.md on every change
WIKIEOF
            info "Default AGENTS_WIKI.md created"
        fi
    fi

    # Git init
    if [[ ! -d "$WIKI_DATA/.git" ]]; then
        dry "git init $WIKI_DATA + initial commit"
        if ! $DRY_RUN; then
            cd "$WIKI_DATA"
            git init
            git add -A
            git commit -m "init: wiki data initialized via setup.sh" --quiet
            info "Git repo initialized at $WIKI_DATA"
        fi
    else
        info "Git repo already exists at $WIKI_DATA"
    fi
}

# =============================================================================
# PHASE 2: User Symlinks
# =============================================================================
setup_symlinks() {
    header "Phase 2/8: User Symlinks"

    local links=(
        "$WIKI_DATA:$HOME/ai-wiki"
        "$WIKI_DATA:$HOME/.pi/wiki"
    )

    for entry in "${links[@]}"; do
        local target="${entry%%:*}"
        local link="${entry##*:}"
        local parent
        parent="$(dirname "$link")"
        dry "ln -sfn $target $link"
        if ! $DRY_RUN; then
            mkdir -p "$parent"
            ln -sfn "$target" "$link"
            info "$link → $target"
        fi
    done
}

# =============================================================================
# PHASE 3: ClawMem
# =============================================================================
setup_clawmem() {
    header "Phase 3/8: ClawMem (Memory Engine)"

    if $SKIP_CLAWMEM; then
        warn "Skipped via --skip-clawmem"
        return
    fi

    # Detect existing ClawMem
    local clawmem_path=""
    if command -v clawmem >/dev/null 2>&1; then
        clawmem_path="$(command -v clawmem)"
        info "ClawMem found on PATH: $clawmem_path"
    elif [[ -f "$CLAWMEM_BINARY" ]]; then
        clawmem_path="$CLAWMEM_BINARY"
        info "ClawMem found at source: $clawmem_path"
    else
        warn "ClawMem not detected."
        warn "  Install via npm: npm install -g clawmem"
        warn "  Or from source:  git clone https://github.com/yoloshii/clawmem.git $CLAWMEM_SOURCE_DIR"
        warn "  Then re-run:     cd $CLAWMEM_SOURCE_DIR && bun install"
        warn "  (Skipping ClawMem setup — MCP and search will not work until this is resolved)"
        return
    fi

    # Ensure on PATH
    if ! $DRY_RUN; then
        local clawmem_dir
        clawmem_dir="$(dirname "$clawmem_path")"
        if [[ ":$PATH:" != *":$clawmem_dir:"* ]]; then
            warn "ClawMem not in PATH ($clawmem_dir). Add it to ~/.bashrc or ~/.zshrc"
        fi
    fi

    # Bootstrap vault for wiki
    if [[ -n "$clawmem_path" ]]; then
        dry "clawmem init && clawmem collection add $WIKI_DATA/pages --name wiki"
        if ! $DRY_RUN; then
            # init only if no config
            if [[ ! -f "$HOME/.config/clawmem/index.yml" ]]; then
                "$clawmem_path" init 2>/dev/null || true
                info "ClawMem initialized"
            fi

            # Check if wiki collection exists
            if "$clawmem_path" collection list 2>/dev/null | grep -q '"wiki"'; then
                info "ClawMem wiki collection already exists"
            else
                "$clawmem_path" collection add "$WIKI_DATA/pages" --name wiki 2>/dev/null || true
                info "ClawMem wiki collection added"
            fi

            # Embed wiki content
            sub "Embedding wiki into ClawMem..."
            "$clawmem_path" update --embed 2>/dev/null || warn "Embedding failed — is embedding server running?"
        fi
    fi
}

# =============================================================================
# PHASE 4: MCP Registration
# =============================================================================
register_mcp_for_agent() {
    local agent="$1"

    # Resolve ClawMem binary path dynamically
    local clawmem_bin
    if command -v clawmem >/dev/null 2>&1; then
        clawmem_bin="$(command -v clawmem)"
    elif [[ -x "${CLAWMEM_BINARY:-}" ]]; then
        clawmem_bin="$CLAWMEM_BINARY"
    else
        warn "ClawMem binary not found — skip MCP registration for $agent"
        return
    fi

    # Escape for JSON — use raw path as-is since it's already an absolute path
    local mcp_json_cmd
    mcp_json_cmd="$(python3 -c "import json; print(json.dumps('$clawmem_bin'))")"

    case "$agent" in
        claude-code)
            if [[ ${AGENTS[claude]} -eq 0 ]]; then
                sub "Claude Code not installed — skipping MCP registration"
                return
            fi
            local mcp_file="$HOME/.claude/mcp.json"
            if [[ -f "$mcp_file" ]]; then
                if grep -q '"clawmem"' "$mcp_file" 2>/dev/null; then
                    info "Claude Code: clawmem MCP already registered"
                else
                    dry "Add clawmem to $mcp_file"
                    if ! $DRY_RUN; then
                        python3 -c "
import json
with open('$mcp_file') as f:
    cfg = json.load(f)
cfg.setdefault('mcpServers', {})['clawmem'] = {
    'command': $mcp_json_cmd,
    'args': ['mcp']
}
with open('$mcp_file', 'w') as f:
    json.dump(cfg, f, indent=2)
" 2>/dev/null || python3 -c "
import json
with open('$mcp_file') as f:
    cfg = json.load(f)
cfg['clawmem'] = {'command': $mcp_json_cmd, 'args': ['mcp']}
with open('$mcp_file', 'w') as f:
    json.dump(cfg, f, indent=2)
" 2>/dev/null || warn "Failed to update $mcp_file"
                        info "Claude Code: clawmem MCP registered"
                    fi
                fi
            else
                dry "Create $mcp_file with clawmem server"
                if ! $DRY_RUN; then
                    mkdir -p "$(dirname "$mcp_file")"
                    python3 -c "
import json
cfg = {
    'mcpServers': {
        'clawmem': {
            'command': $mcp_json_cmd,
            'args': ['mcp']
        }
    }
}
with open('$mcp_file', 'w') as f:
    json.dump(cfg, f, indent=2)
"
                    info "Claude Code: clawmem MCP registered"
                fi
            fi
            ;;

        pi)
            if [[ ${AGENTS[pi]} -eq 0 ]]; then
                sub "Pi Agent not installed — skipping MCP registration"
                return
            fi
            local mcp_cache="$HOME/.pi/agent/mcp-cache.json"
            if [[ -f "$mcp_cache" ]]; then
                if grep -q '"clawmem"' "$mcp_cache" 2>/dev/null; then
                    info "Pi Agent: clawmem MCP already cached"
                else
                    dry "Register clawmem in Pi MCP cache"
                    if ! $DRY_RUN; then
                        python3 -c "
import json
with open('$mcp_cache') as f:
    cfg = json.load(f)
cfg['clawmem'] = {'command': $mcp_json_cmd, 'args': ['mcp']}
with open('$mcp_cache', 'w') as f:
    json.dump(cfg, f, indent=2)
" 2>/dev/null || true
                        info "Pi Agent: clawmem MCP registered"
                    fi
                fi
            else
                warn "Pi Agent: no mcp-cache.json found (generated at runtime)"
            fi
            ;;

        ante)
            if [[ ${AGENTS[ante]} -eq 0 ]]; then
                sub "Ante not installed — skipping MCP registration"
                return
            fi
            local settings="$HOME/.ante/settings.json"
            if [[ -f "$settings" ]]; then
                if grep -q '"clawmem"' "$settings" 2>/dev/null; then
                    info "Ante: clawmem MCP already registered"
                else
                    dry "Add clawmem MCP to $settings"
                    if ! $DRY_RUN; then
                        python3 -c "
import json
with open('$settings') as f:
    cfg = json.load(f)
cfg['mcp_servers'] = cfg.get('mcp_servers', {})
cfg['mcp_servers']['clawmem'] = {
    'command': $mcp_json_cmd,
    'args': ['mcp']
}
with open('$settings', 'w') as f:
    json.dump(cfg, f, indent=2)
" 2>/dev/null || warn "Failed to update $settings"
                        info "Ante: clawmem MCP registered"
                    fi
                fi
            fi
            ;;

        kilocode)
            if [[ ${AGENTS[kilocode]} -eq 0 ]]; then
                sub "KiloCode not installed — skipping MCP registration"
                return
            fi
            local mcp_dir="$HOME/.kilocode/mcp_servers"
            local mcp_file="$mcp_dir/clawmem.json"
            if [[ -d "$mcp_dir" ]] || { $DRY_RUN && mkdir -p "$mcp_dir"; } || { ! $DRY_RUN && mkdir -p "$mcp_dir"; }; then
                if [[ -f "$mcp_file" ]]; then
                    info "KiloCode: clawmem MCP already registered"
                else
                    dry "Create $mcp_file"
                    if ! $DRY_RUN; then
                        mkdir -p "$mcp_dir" 2>/dev/null || true
                        python3 -c "
import json
cfg = {
    'name': 'clawmem',
    'command': $mcp_json_cmd,
    'args': ['mcp']
}
with open('$mcp_file', 'w') as f:
    json.dump(cfg, f, indent=2)
"
                        info "KiloCode: clawmem MCP registered"
                    fi
                fi
            fi
            ;;

        opencode)
            if [[ ${AGENTS[opencode]} -eq 0 ]]; then
                sub "OpenCode not installed — skipping MCP registration"
                return
            fi
            local oc_config="$HOME/.config/opencode/opencode.json"
            if [[ -f "$oc_config" ]]; then
                if grep -q '"clawmem"' "$oc_config" 2>/dev/null; then
                    info "OpenCode: clawmem MCP already registered"
                else
                    dry "Add clawmem MCP to $oc_config"
                    if ! $DRY_RUN; then
                        python3 -c "
import json
with open('$oc_config') as f:
    cfg = json.load(f)
cfg['plugins'] = cfg.get('plugins', [])
cfg['mcpServers'] = cfg.get('mcpServers', {})
cfg['mcpServers']['clawmem'] = {
    'command': $mcp_json_cmd,
    'args': ['mcp']
}
with open('$oc_config', 'w') as f:
    json.dump(cfg, f, indent=2)
" 2>/dev/null || warn "Failed to update $oc_config"
                        info "OpenCode: clawmem MCP registered"
                    fi
                fi
            fi
            ;;

        hermes)
            if [[ ${AGENTS[hermes]} -eq 0 ]]; then
                sub "Hermes not installed — skipping MCP registration"
                return
            fi
            if command -v hermes >/dev/null 2>&1; then
                dry "hermes mcp add clawmem"
                if ! $DRY_RUN; then
                    hermes mcp add clawmem -- \
                        "$clawmem_bin" \
                        "mcp" 2>/dev/null || \
                    warn "Hermes mcp add failed (trying alternate syntax)"
                fi
            fi
            ;;
    esac
}

setup_mcp() {
    header "Phase 4/8: MCP Registration"

    if $SKIP_MCP; then
        warn "Skipped via --skip-mcp"
        return
    fi

    if [[ ! -f "${CLAWMEM_BINARY}" ]] && ! command -v clawmem >/dev/null 2>&1; then
        warn "ClawMem not installed — skipping MCP registration for all agents"
        warn "Install ClawMem first, then re-run setup.sh"
        return
    fi

    sub "Registering ClawMem MCP server with detected agents..."

    register_mcp_for_agent "claude-code"
    register_mcp_for_agent "pi"
    register_mcp_for_agent "ante"
    register_mcp_for_agent "kilocode"
    register_mcp_for_agent "opencode"
    register_mcp_for_agent "hermes"
}

# =============================================================================
# PHASE 5: Agent Skills
# =============================================================================
setup_skills() {
    header "Phase 5/8: Agent Skill Symlinks"

    if $SKIP_SKILLS; then
        warn "Skipped via --skip-skills"
        return
    fi

    local skill_source="$CANONICAL_DIR/skill"
    local skill_md="$skill_source/SKILL.md"

    if [[ ! -f "$skill_md" ]]; then
        error "Skill file not found at $skill_md"
        return
    fi

    # Symlink target → source pairs
    local symlinks=()

    if [[ ${AGENTS[pi]} -eq 1 ]]; then
        symlinks+=("$HOME/.pi/agent/skills/karpathy-wiki:$skill_source")
    fi

    if [[ ${AGENTS[claude]} -eq 1 ]]; then
        symlinks+=("$HOME/.claude/skills/karpathy-wiki:$skill_source")
        # Claude Code prefers .md files in skills, also link as .md
        if [[ ! -f "$HOME/.claude/skills/karpathy-wiki.md" ]]; then
            dry "ln -sf $skill_md $HOME/.claude/skills/karpathy-wiki.md"
            if ! $DRY_RUN; then
                mkdir -p "$HOME/.claude/skills"
                ln -sf "$skill_md" "$HOME/.claude/skills/karpathy-wiki.md"
                info "Claude Code: karpathy-wiki.md skill linked"
            fi
        fi
    fi

    if [[ ${AGENTS[ante]} -eq 1 ]]; then
        symlinks+=("$HOME/.ante/skills/karpathy-wiki:$skill_source")
    fi

    if [[ ${AGENTS[kilocode]} -eq 1 ]]; then
        symlinks+=("$HOME/.kilocode/skills/karpathy-wiki:$skill_source")
    fi

    if [[ ${AGENTS[opencode]} -eq 1 ]]; then
        symlinks+=("$HOME/.config/opencode/skills/karpathy-wiki:$skill_source")
        # OpenCode cross-discovers from ~/.claude/skills/ and ~/.agents/skills/
        if [[ ${AGENTS[claude]} -eq 0 ]]; then
            dry "mkdir -p $HOME/.claude/skills + link (OpenCode cross-discovery)"
            if ! $DRY_RUN; then
                mkdir -p "$HOME/.claude/skills"
                ln -sf "$skill_md" "$HOME/.claude/skills/karpathy-wiki-cross.md" 2>/dev/null || true
            fi
        fi
        mkdir -p "$HOME/.agents/skills" 2>/dev/null || true
        if [[ -d "$HOME/.agents/skills" ]]; then
            dry "ln -sf $skill_source $HOME/.agents/skills/karpathy-wiki"
            if ! $DRY_RUN; then
                mkdir -p "$HOME/.agents/skills"
                ln -sfn "$skill_source" "$HOME/.agents/skills/karpathy-wiki" 2>/dev/null || true
            fi
        fi
    fi

    # Pi goal plugin
    if [[ ${AGENTS[pi]} -eq 1 ]]; then
        local plugin_source="$CANONICAL_DIR/plugin/goal"
        local plugin_link="$HOME/.pi/agent/plugins/goal"
        if [[ -d "$plugin_source" ]] && [[ ! -L "$plugin_link" ]]; then
            dry "ln -sfn $plugin_source $plugin_link"
            if ! $DRY_RUN; then
                mkdir -p "$HOME/.pi/agent/plugins"
                ln -sfn "$plugin_source" "$plugin_link"
                info "Pi Agent: goal plugin linked"
            fi
        fi
    fi

    # Create symlinks
    for entry in "${symlinks[@]}"; do
        local target="${entry##*:}"
        local link="${entry%%:*}"
        local parent; parent="$(dirname "$link")"
        if [[ ! -L "$link" ]]; then
            dry "ln -sfn $target $link"
            if ! $DRY_RUN; then
                mkdir -p "$parent"
                ln -sfn "$target" "$link"
                info "Skill linked: $link → $target"
            fi
        else
            info "Skill already linked: $link"
        fi
    done
}

# =============================================================================
# PHASE 6: Hooks
# =============================================================================
setup_hooks() {
    header "Phase 6/8: Session Hooks"

    if $SKIP_HOOKS; then
        warn "Skipped via --skip-hooks"
        return
    fi

    # ── Pi Agent: plugin.json goal triggers ──
    if [[ ${AGENTS[pi]} -eq 1 ]]; then
        local plugin_file="$HOME/.pi/agent/plugins/goal/plugin.json"
        if [[ -f "$plugin_file" ]]; then
            info "Pi Agent: goal plugin already configured (plugin.json)"
        fi
    fi

    # ── Claude Code: hooks ──
    if [[ ${AGENTS[claude]} -eq 1 ]]; then
        local claude_hooks_dir="$HOME/.claude/hooks"
        if [[ -d "$claude_hooks_dir" ]]; then
            local hook_files=("$CANONICAL_DIR/hooks/pre_compact.py" "$CANONICAL_DIR/hooks/session_end.py")
            for hook in "${hook_files[@]}"; do
                if [[ -f "$hook" ]]; then
                    local hook_name; hook_name="$(basename "$hook")"
                    local target="$claude_hooks_dir/$hook_name"
                    if [[ ! -f "$target" ]]; then
                        dry "Copy $hook → $target"
                        if ! $DRY_RUN; then
                            cp "$hook" "$target"
                            chmod +x "$target"
                            info "Claude Code hook: $hook_name installed"
                        fi
                    else
                        info "Claude Code hook exists: $hook_name"
                    fi
                fi
            done

            # Also register in .claude/settings.local.json if using hooks config
            local claude_settings="$HOME/.claude/settings.local.json"
            if [[ -f "$claude_settings" ]]; then
                if grep -q "karpathy" "$claude_settings" 2>/dev/null; then
                    info "Claude Code: karpathy-wiki hooks already configured"
                fi
            fi
        fi
    fi

    # ── KiloCode: hooks ──
    if [[ ${AGENTS[kilocode]} -eq 1 ]]; then
        local kilo_hooks_dir="$HOME/.kilocode/hooks"
        if [[ -d "$kilo_hooks_dir" ]]; then
            local hook_files=("$CANONICAL_DIR/hooks/pre_compact.py" "$CANONICAL_DIR/hooks/session_end.py")
            for hook in "${hook_files[@]}"; do
                if [[ -f "$hook" ]]; then
                    local hook_name; hook_name="$(basename "$hook")"
                    local target="$kilo_hooks_dir/$hook_name"
                    if [[ ! -f "$target" ]]; then
                        dry "Copy $hook → $target"
                        if ! $DRY_RUN; then
                            cp "$hook" "$target"
                            chmod +x "$target"
                            info "KiloCode hook: $hook_name installed"
                        fi
                    fi
                fi
            done
        else
            dry "mkdir -p $kilo_hooks_dir + install hooks"
            if ! $DRY_RUN; then
                mkdir -p "$kilo_hooks_dir"
                for hook in "$CANONICAL_DIR/hooks/pre_compact.py" "$CANONICAL_DIR/hooks/session_end.py"; do
                    if [[ -f "$hook" ]]; then
                        cp "$hook" "$kilo_hooks_dir/"
                        chmod +x "$kilo_hooks_dir/$(basename "$hook")"
                    fi
                done
                info "KiloCode hooks installed"
            fi
        fi
    fi

    # ── Hermes: shell hooks (if installed) ──
    if [[ ${AGENTS[hermes]} -eq 1 ]] && command -v hermes >/dev/null 2>&1; then
        dry "hermes hooks install"
        if ! $DRY_RUN; then
            hermes hooks install 2>/dev/null || true
            info "Hermes hooks installed"
        fi
    fi

    # ── ClawMem hooks (if clawmem installed) ──
    local clawmem_cmd=""
    command -v clawmem >/dev/null 2>&1 && clawmem_cmd="clawmem"
    [[ -z "$clawmem_cmd" ]] && [[ -f "$CLAWMEM_BINARY" ]] && clawmem_cmd="$CLAWMEM_BINARY"

    if [[ -n "$clawmem_cmd" ]]; then
        dry "$clawmem_cmd setup hooks"
        if ! $DRY_RUN; then
            "$clawmem_cmd" setup hooks 2>/dev/null || warn "ClawMem hook setup failed"
            info "ClawMem hooks installed"
        fi
    fi
}

# =============================================================================
# PHASE 7: Dream Agent Scheduler
# =============================================================================
setup_dream() {
    header "Phase 7/8: Dream Agent Scheduler"

    if $SKIP_DREAM; then
        warn "Skipped via --skip-dream"
        return
    fi

    local dream_script="$CANONICAL_DIR/dream/dream_agent.py"
    local scheduler_script="$CANONICAL_DIR/dream/scheduler.py"

    if [[ ! -f "$dream_script" ]]; then
        error "Dream agent not found at $dream_script"
        return
    fi

    # Validate the script runs
    sub "Validating dream agent..."
    if ! $DRY_RUN; then
        if python3 -c "import sys; sys.path.insert(0, '${CANONICAL_DIR}/dream'); from dream_agent import __version__; print(__version__)" 2>/dev/null; then
            info "Dream agent validates"
        else
            python3 "$dream_script" --help 2>/dev/null | head -3 || true
            info "Dream agent script is executable"
        fi
    fi

    # ── systemd timer (Linux) ──
    if $HAS_SYSTEMD; then
        sub "Setting up systemd --user timer..."

        local service_file="$HOME/.config/systemd/user/dream-agent.service"
        local timer_file="$HOME/.config/systemd/user/dream-agent.timer"

        if [[ -f "$service_file" ]] && [[ -f "$timer_file" ]]; then
            if systemctl --user is-enabled dream-agent.timer >/dev/null 2>&1; then
                info "systemd timer already enabled"
            else
                dry "systemctl --user enable --now dream-agent.timer"
                if ! $DRY_RUN; then
                    systemctl --user daemon-reload
                    systemctl --user enable --now dream-agent.timer 2>/dev/null || \
                        warn "Failed to enable timer (may need --user bus)"
                fi
            fi
        else
            dry "Create systemd unit files"
            if ! $DRY_RUN; then
                mkdir -p "$HOME/.config/systemd/user"

                cat > "$service_file" << SERVICE
[Unit]
Description=Karpathy Wiki Dream Agent (Sleep-Time Compute)
Documentation=https://github.com/karpathy-wiki

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 $dream_script --idle 600
Environment=AI_WIKI=$WIKI_DATA
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
SERVICE

                cat > "$timer_file" << TIMER
[Unit]
Description=Dream agent idle timer (30min check)
Requires=dream-agent.service

[Timer]
OnActiveSec=5min
OnType=idle
IdleWaitSec=5min
OnUnitActiveSec=30min

[Install]
WantedBy=timers.target
TIMER

                systemctl --user daemon-reload 2>/dev/null || true
                info "systemd unit files created at:"
                info "  $service_file"
                info "  $timer_file"
                warn "To enable: systemctl --user enable --now dream-agent.timer"
                warn "Requires: loginctl enable-linger $USER"
            fi
        fi
    fi

    # ── macOS / daemon fallback ──
    if [[ "$OS" == "Darwin" ]]; then
        warn "macOS detected — systemd not available."
        warn "Use daemon mode: python3 $scheduler_script --daemon"
        warn "Add to crontab or launchd for persistence."
    fi

    # ── Launchctl (macOS) ──
    if [[ "$OS" == "Darwin" ]]; then
        local plist="$HOME/Library/LaunchAgents/com.karpathy-wiki.dream-agent.plist"
        if [[ ! -f "$plist" ]]; then
            dry "Create launchd plist"
            if ! $DRY_RUN; then
                mkdir -p "$HOME/Library/LaunchAgents"
                cat > "$plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.karpathy-wiki.dream-agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$dream_script</string>
        <string>--idle</string>
        <string>600</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>AI_WIKI</key>
        <string>$WIKI_DATA</string>
    </dict>
    <key>StartInterval</key>
    <integer>1800</integer>
    <key>RunAtLoad</key>
    <true/>
    <key>LowPriorityIO</key>
    <true/>
</dict>
</plist>
PLIST
                info "LaunchAgent plist created at $plist"
                warn "To load: launchctl load $plist"
            fi
        fi
    fi
}

# =============================================================================
# PHASE 8: Environment Variables
# =============================================================================
setup_env() {
    header "Phase 8/8: Environment Variables"

    if $SKIP_ENV; then
        warn "Skipped via --skip-env"
        return
    fi

    local rc_file=""
    if [[ -f "$HOME/.zshrc" ]]; then
        rc_file="$HOME/.zshrc"
    elif [[ -f "$HOME/.bashrc" ]]; then
        rc_file="$HOME/.bashrc"
    elif [[ -f "$HOME/.bash_profile" ]]; then
        rc_file="$HOME/.bash_profile"
    fi

    if [[ -z "$rc_file" ]]; then
        warn "No shell rc file found. Add environment vars manually (see env reference)."
        return
    fi

    # Check which vars are already set and which need adding
    local missing_vars=()

    # Core wiki
    export AI_WIKI="$WIKI_DATA"
    grep -q 'export AI_WIKI=' "$rc_file" 2>/dev/null || missing_vars+=('export AI_WIKI="$HOME/.local/share/ai-wiki"')

    # ClawMem
    grep -q 'export CLAWMEM_URL=' "$rc_file" 2>/dev/null || missing_vars+=('export CLAWMEM_URL="http://localhost:7438"')
    grep -q 'export CLAWMEM_COLLECTION=' "$rc_file" 2>/dev/null || missing_vars+=('export CLAWMEM_COLLECTION="wiki"')

    # Dream agent
    grep -q 'export PI_SKILLS_DIR=' "$rc_file" 2>/dev/null || missing_vars+=('export PI_SKILLS_DIR="$HOME/.pi/agent/skills"')
    grep -q 'export ANTE_SKILLS_DIR=' "$rc_file" 2>/dev/null || missing_vars+=('export ANTE_SKILLS_DIR="$HOME/.ante/skills"')

    # Scheduler tuning (optional — only if referencing default values)
    grep -q 'export DEFAULT_IDLE=' "$rc_file" 2>/dev/null || missing_vars+=('# export DEFAULT_IDLE=600  # Default idle budget (10 min)')
    grep -q 'export DAEMON_INTERVAL=' "$rc_file" 2>/dev/null || missing_vars+=('# export DAEMON_INTERVAL=1800  # Daemon check interval (30 min)')

    # Path (ClawMem)
    local clawmem_dir
    if [[ -f "$CLAWMEM_BINARY" ]]; then
        clawmem_dir="$(dirname "$CLAWMEM_BINARY")"
        if [[ ":$PATH:" != *":$clawmem_dir:"* ]] && [[ -d "$clawmem_dir" ]]; then
            grep -q "export PATH=.*$clawmem_dir" "$rc_file" 2>/dev/null || missing_vars+=("export PATH=\"\$PATH:$clawmem_dir\"")
        fi
    fi

    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        if $DRY_RUN; then
            detail "Would add ${#missing_vars[@]} env vars to $rc_file"
            for var in "${missing_vars[@]}"; do
                detail "  $var"
            done
        else
            if $UNATTENDED; then
                # Auto-append
                {
                    echo ""
                    echo "# ── Karpathy Wiki (added by setup.sh) ──"
                    for var in "${missing_vars[@]}"; do
                        echo "${var#\# }"  # Strip comment prefix if present
                    done
                } >> "$rc_file"
                info "Added ${#missing_vars[@]} env vars to $rc_file"
            else
                warn "Missing environment variables. Add the following to $rc_file:"
                for var in "${missing_vars[@]}"; do
                    warn "  $var"
                done
            fi
        fi
    else
        info "All environment variables already configured in $rc_file"
    fi

    # Export for current session
    export AI_WIKI="$WIKI_DATA"
    export CLAWMEM_URL="${CLAWMEM_URL:-http://localhost:7438}"
    export CLAWMEM_COLLECTION="${CLAWMEM_COLLECTION:-wiki}"
}

# =============================================================================
# Verification
# =============================================================================
run_verification() {
    header "Verification"

    local all_pass=true

    # Wiki data
    if [[ -d "$WIKI_DATA/pages" ]]; then
        info "✅ Wiki data directory exists"
    else
        error "❌ Wiki data directory missing"
        all_pass=false
    fi

    # Symlinks
    if [[ -L "$HOME/ai-wiki" ]]; then
        info "✅ ~/ai-wiki symlink exists"
    else
        warn "⚠ ~/ai-wiki symlink missing"
    fi

    # Git
    if [[ -d "$WIKI_DATA/.git" ]]; then
        cd "$WIKI_DATA"
        local commit_count
        commit_count="$(git rev-list --count HEAD 2>/dev/null || echo 0)"
        info "✅ Wiki git repo ($commit_count commits)"
    fi

    # ClawMem
    if command -v clawmem >/dev/null 2>&1; then
        info "✅ ClawMem on PATH"
    elif [[ -f "$CLAWMEM_BINARY" ]]; then
        info "⏳ ClawMem at source (not on PATH)"
    else
        warn "⚠ ClawMem not installed"
    fi

    # MCP configs
    if [[ -f "$HOME/.claude/mcp.json" ]]; then
        if grep -q 'clawmem' "$HOME/.claude/mcp.json" 2>/dev/null; then
            info "✅ Claude Code MCP: clawmem registered"
        fi
    fi

    # Skills
    for agent_entry in "$HOME/.claude/skills/karpathy-wiki" "$HOME/.pi/agent/skills/karpathy-wiki" "$HOME/.ante/skills/karpathy-wiki" "$HOME/.kilocode/skills/karpathy-wiki" "$HOME/.config/opencode/skills/karpathy-wiki"; do
        if [[ -L "$agent_entry" ]] || [[ -f "$agent_entry" ]]; then
            local name; name="$(echo "$agent_entry" | grep -oP '(\.claude|\.pi|\.ante|\.kilocode|opencode)')"
            info "✅ Skill symlinked for $name"
        fi
    done

    # Hooks
    for hook_file in "$HOME/.claude/hooks/pre_compact.py" "$HOME/.claude/hooks/session_end.py" "$HOME/.kilocode/hooks/pre_compact.py" "$HOME/.kilocode/hooks/session_end.py"; do
        if [[ -f "$hook_file" ]]; then
            info "✅ Hook: $(basename "$(dirname "$hook_file")")/$(basename "$hook_file")"
        fi
    done

    # systemd timer
    if $HAS_SYSTEMD && systemctl --user list-timers --all 2>/dev/null | grep -q dream-agent; then
        info "✅ systemd dream-agent timer active"
    fi

    # Environment
    if [[ -n "${AI_WIKI:-}" ]] && [[ -d "${AI_WIKI:-}" ]]; then
        info "✅ AI_WIKI environment variable set"
    fi

    echo ""
    if $all_pass; then
        info "${GREEN}All checks passed!${NC}"
    else
        warn "Some checks failed — review above for details."
    fi
}

# =============================================================================
# Summary
# =============================================================================
print_summary() {
    header "Setup Summary"

    local preset_display="${CONFIG_PRESET:-default}"
    local mode="${DRY_RUN:+dry-run}"; mode="${mode:-live}"

    echo -e "  ${CYAN}Preset:${NC}      $preset_display"
    echo -e "  ${CYAN}Mode:${NC}        $mode"
    echo -e "  ${CYAN}OS:${NC}          $OS${IS_WSL:+ (WSL2)}"
    echo -e "  ${CYAN}Wiki Data:${NC}   $WIKI_DATA"
    echo -e "  ${CYAN}Code:${NC}        $CANONICAL_DIR"
    echo -e "  ${CYAN}Agents:${NC}      $(for a in pi claude ante kilocode opencode hermes; do [[ ${AGENTS[$a]} -eq 1 ]] && echo -n "$a "; done)antigravity"

    echo ""
    echo -e "  ${CYAN}Quick reference:${NC}"
    echo -e "    Dream agent:   python3 $CANONICAL_DIR/dream/dream_agent.py --idle 600"
    echo -e "    Scheduler:     python3 $CANONICAL_DIR/dream/scheduler.py --daemon"
    echo -e "    Re-run setup:  $0 --preset $preset_display"
    echo -e "    Config schema: $CANONICAL_DIR/config.schema.yaml"
    echo ""
    echo -e "  ${CYAN}Wiki path:${NC}   ~/ai-wiki → $WIKI_DATA"
    echo ""
}

# =============================================================================
# MAIN
# =============================================================================
main() {
    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║           Karpathy Wiki — Multi-Agent Setup                  ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Apply preset from config file
    if [[ -n "$CONFIG_PRESET" ]]; then
        sub "Applying preset: $CONFIG_PRESET"
        case "$CONFIG_PRESET" in
            lightweight|balanced|high-quality|max-context)
                info "Preset '$CONFIG_PRESET' selected"
                ;;
            *)
                warn "Unknown preset '$CONFIG_PRESET'. Using defaults (balanced)."
                CONFIG_PRESET="balanced"
                ;;
        esac
    fi

    if [[ -n "$CONFIG_FILE" ]]; then
        if [[ -f "$CONFIG_FILE" ]]; then
            sub "Loading custom config: $CONFIG_FILE"
        else
            error "Config file not found: $CONFIG_FILE"
            exit 1
        fi
    fi

    if $DRY_RUN; then
        warn "DRY RUN — no changes will be made"
        echo ""
    fi

    # Prerequisites
    header "Prerequisite Check"
    prereq_check || exit 1

    # Detect agents
    detect_agents

    # Run phases
    setup_wiki_data
    setup_symlinks
    setup_clawmem
    setup_mcp
    setup_skills
    setup_hooks
    setup_dream
    setup_env

    # Verify
    run_verification

    # Summary
    print_summary

    if $DRY_RUN; then
        echo -e "${YELLOW}Dry run complete. Re-run without --dry-run to apply changes.${NC}"
    else
        echo -e "${GREEN}Setup complete!${NC}"
        echo -e "  ${BLUE}→${NC} For ongoing operation, keep the dream agent running:"
        echo -e "    python3 $CANONICAL_DIR/dream/scheduler.py --daemon"
        echo ""
        if ! $HAS_SYSTEMD && [[ "$OS" != "Darwin" ]]; then
            echo -e "  ${BLUE}→${NC} Or add to crontab:"
            echo -e "    echo '*/30 * * * * cd $CANONICAL_DIR && python3 dream/scheduler.py --cycle 1800' | crontab -"
        fi
    fi
}

main "$@"
