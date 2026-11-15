| Dimension | Flag | Default | Maps to cass |
|-----------|------|---------|--------------|
| Time — relative | `--since 7d` | `30d` | `--days N` or `--since Nd` on `cass search` |
| Time — absolute | `--from 2025-01-01 --to 2025-06-30` | (none) | post-filter on `cass search` timestamps |
| Time — today | `--today` | false | `cass search "" --today --robot-format sessions` |
| Projects | `--projects foo,bar` or `--project-dir ~/code/foo` | all in DB | `cass search "" --workspace /abs/path --robot-format sessions` per project |
| Agents | `--agent claude,cursor` | all | `cass search ... --agent <name> --robot-format sessions` (one invocation per agent, results unioned) |
| Prompt type | `--type correction,scope-cut` | all | post-filter on the distilled `intents.type` column (see `references/intent_taxonomy.md`) |
| Content regex | `--matches "jwt|auth"` | (none) | `cass search "<regex>" --json` (Phase F) or post-filter on extracted prompt text (Phase C) |
| Single session | `--session /path/to/session.jsonl` | (none) | `cass export /path --format json` directly, no enumeration |
| Result cap | `--limit 500` | (none) | `cass search ... --limit N --json` (Phase F) or stop enumeration after N prompts (Phase C) |
| Ordering | `--ordering newest-first` | `newest-first` | cass search results are processed in-line; per-session ordering in extract_prompts_from_session |

**Mix-and-match examples** (all valid):

```bash
# Default: all prompts from the last 30 days across all projects and agents
python scripts/05_extract_prompts.py --db ~/.intent-archaeology/state.db

# All prompts from a single project going back 90 days
python scripts/05_extract_prompts.py \
  --db ~/.intent-archaeology/state.db \
  --projects my-app \
  --since 90d

# Every prompt on two projects since January, Claude Code only
python scripts/05_extract_prompts.py \
  --db ~/.intent-archaeology/state.db \
  --projects my-app,api-server \
  --since 2025-01-01 \
  --agent claude

# Only corrections issued in Cursor in the last week (post-distillation filter)
python scripts/06_distill_intent.py \
  --db ~/.intent-archaeology/state.db \
  --type correction \
  --agent cursor \
  --since 7d

# Every prompt containing "auth" or "jwt" across all agents (Phase F-style)
python scripts/05_extract_prompts.py \
  --db ~/.intent-archaeology/state.db \
  --matches "auth|jwt|token" \
  --since 180d

# One specific session, full export including tool calls
python scripts/05_extract_prompts.py \
  --db ~/.intent-archaeology/state.db \
  --session ~/.claude/projects/abc-123.jsonl \
  --include-tools
```
