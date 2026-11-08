# Local setup (this machine)

Machine-specific facts for skill-doctor. SKILL.md stays portable; read this file when it exists. Checked 2026-11-08.

## Session sources

| Source | Path | How skill-doctor reads it |
| --- | --- | --- |
| Claude Code | `/home/cheta/.claude/projects` | collector, `claude` |
| Codex | `/home/cheta/.codex/sessions` | collector, `codex` |
| Pi | `/home/cheta/.pi/agent/sessions` | collector, `pi` |
| Hermes | `/home/cheta/.hermes` | collector, `hermes` |
| omp | `/home/cheta/.omp/agent/sessions` | collector, `--harness pi --pi-home /home/cheta/.omp/agent` (extra pass) |
| gemini, opencode, agy, kiro and others | cass index | `casr list` plus `cass export` (extra pass) |
| muse | `/home/cheta/.local/share/muse` | not parsed; report as found but not parsed |

Never run bare `cass index` to refresh sources; use `cass-reindex` only when a named recovery need exists.

## Where a skill really lives

Deployed skill directories (`/home/cheta/.claude/skills`, `/home/cheta/.codex/skills`, `/home/cheta/.omp/agent/skills` and the other skillshare targets) are copies or symlinks. skillshare deploys them from `/home/cheta/.cache/agents/skillshare-source`, which is itself a staging copy. Never draft against a deployed or staged copy.

Resolve the canonical source in this order:

1. `realpath` of the path in `inventory.json`.
2. If it is inside `/home/cheta/.cache/agents/skillshare-source/<name>`, read `entries.<name>.source` in `/home/cheta/.cache/agents/skillshare-source/.metadata.json`.
3. Otherwise check `/home/cheta/code/custom-skills/<name>`, then `/home/cheta/code/agents/skills/<name>`.
4. Otherwise find the upstream in `/home/cheta/code/agents/source-registry.tsv` or `/home/cheta/.quartermaster/sources.yaml` (third-party repositories under `/home/cheta/git`).

Owned skills (`custom-skills`, `agents/skills`): the proposal targets the canonical path. After the user approves an edit, apply it there and redeploy with `skillshare sync`.

Third-party skills (under `/home/cheta/git`): proposal only. An approved adaptation becomes a copy in `/home/cheta/code/custom-skills/<name>` with `source: adapted`, `upstream`, `upstream_commit`, `attribution` and `license` in its frontmatter, the upstream license kept beside it, then `skillshare install` and `skillshare sync`.

## Scoring lanes

Score in the running agent or its in-harness subagents on the same subscription. Do not dispatch transcript batches to `omp -p` OpenCode Go or free lanes, agy, jcode or any other provider: that sends private session content off this machine's approved provider.
