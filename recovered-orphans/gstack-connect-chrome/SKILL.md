---
name: open-gstack-browser
description: Launch GStack Browser — AI-controlled Chromium with the sidebar extension baked in.
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion

metadata:
  version: "0.2.0"
  triggers: "open gstack browser, launch chromium, show me the browser"
---
<!-- AUTO-GENERATED from SKILL.md.tmpl — do not edit directly -->
<!-- Regenerate: bun run gen:skill-docs -->


## When to invoke this skill

Opens a visible browser window where you can watch every action in real time.
The sidebar shows a live activity feed and chat. Anti-bot stealth built in.
Use when asked to "open gstack browser", "launch browser", "connect chrome",
"open chrome", "real browser", "launch chrome", "side panel", or "control my browser".

Voice triggers (speech-to-text aliases): "show me the browser".

## Preamble (run first)

```bash
_UPD=$(~/.claude/skills/gstack/bin/gstack-update-check 2>/dev/null || .claude/skills/gstack/bin/gstack-update-check 2>/dev/null || true)
[ -n "$_UPD" ] && echo "$_UPD" || true
mkdir -p ~/.gstack/sessions
touch ~/.gstack/sessions/"$PPID"
_SESSIONS=$(find ~/.gstack/sessions -mmin -120 -type f 2>/dev/null | wc -l | tr -d ' ')
find ~/.gstack/sessions -mmin +120 -type f -exec rm {} + 2>/dev/null || true
_PROACTIVE=$(~/.claude/skills/gstack/bin/gstack-config get proactive 2>/dev/null || echo "true")
_PROACTIVE_PROMPTED=$([ -f ~/.gstack/.proactive-prompted ] && echo "yes" || echo "no")
_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
echo "BRANCH: $_BRANCH"
_SKILL_PREFIX=$(~/.claude/skills/gstack/bin/gstack-config get skill_prefix 2>/dev/null || echo "false")
echo "PROACTIVE: $_PROACTIVE"
echo "PROACTIVE_PROMPTED: $_PROACTIVE_PROMPTED"
echo "SKILL_PREFIX: $_SKILL_PREFIX"
source <(~/.claude/skills/gstack/bin/gstack-repo-mode 2>/dev/null) || true
REPO_MODE=${REPO_MODE:-unknown}
echo "REPO_MODE: $REPO_MODE"
_SESSION_KIND=$(~/.claude/skills/gstack/bin/gstack-session-kind 2>/dev/null || echo "interactive")
case "$_SESSION_KIND" in spawned|headless|interactive) ;; *) _SESSION_KIND="interactive" ;; esac
echo "SESSION_KIND: $_SESSION_KIND"
# Conductor host: AskUserQuestion is unreliable here (native disabled, MCP
# variant flaky), so skills render decisions as prose instead of calling the
# tool. Gated on !headless so an eval/CI run INSIDE Conductor (GSTACK_HEADLESS)
# still BLOCKs rather than rendering prose to nobody.
if [ "$_SESSION_KIND" != "headless" ] && { [ -n "${CONDUCTOR_WORKSPACE_PATH:-}" ] || [ -n "${CONDUCTOR_PORT:-}" ]; }; then
  echo "CONDUCTOR_SESSION: true"
fi
_ACTIVATED=$([ -f ~/.gstack/.activated ] && echo "yes" || echo "no")
_FIRST_LOOP_SHOWN=$([ -f ~/.gstack/.first-loop-tip-shown ] && echo "yes" || echo "no")
echo "ACTIVATED: $_ACTIVATED"
echo "FIRST_LOOP_SHOWN: $_FIRST_LOOP_SHOWN"
# First-run project detection: run the detector ONLY on the first-ever skill run
# (ACTIVATED=no, interactive) so it stays off the hot path for every run after.
_FIRST_TASK=""
if [ "$_ACTIVATED" = "no" ] && [ "$_SESSION_KIND" != "headless" ]; then
  _FIRST_TASK=$(~/.claude/skills/gstack/bin/gstack-first-task-detect 2>/dev/null || true)
fi
echo "FIRST_TASK: $_FIRST_TASK"
_LAKE_SEEN=$([ -f ~/.gstack/.completeness-intro-seen ] && echo "yes" || echo "no")
echo "LAKE_INTRO: $_LAKE_SEEN"
_TEL=$(~/.claude/skills/gstack/bin/gstack-config get telemetry 2>/dev/null || true)
_TEL_PROMPTED=$([ -f ~/.gstack/.telemetry-prompted ] && echo "yes" || echo "no")
_TEL_START=$(date +%s)
_SESSION_ID="$$-$(date +%s)"
echo "TELEMETRY: ${_TEL:-off}"
echo "TEL_PROMPTED: $_TEL_PROMPTED"
_EXPLAIN_LEVEL=$(~/.claude/skills/gstack/bin/gstack-config get explain_level 2>/dev/null || echo "default")
if [ "$_EXPLAIN_LEVEL" != "default" ] && [ "$_EXPLAIN_LEVEL" != "terse" ]; then _EXPLAIN_LEVEL="default"; fi
echo "EXPLAIN_LEVEL: $_EXPLAIN_LEVEL"
_QUESTION_TUNING=$(~/.claude/skills/gstack/bin/gstack-config get question_tuning 2>/dev/null || echo "false")
echo "QUESTION_TUNING: $_QUESTION_TUNING"
_UPDATE_CHECK=$(~/.claude/skills/gstack/bin/gstack-config get update_check 2>/dev/null || echo "true")
echo "UPDATE_CHECK: $_UPDATE_CHECK"
mkdir -p ~/.gstack/analytics
if [ "$_TEL" != "off" ]; then
echo '{"skill":"open-gstack-browser","ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","repo":"'$(_repo=$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null | tr -cd 'a-zA-Z0-9._-'); echo "${_repo:-unknown}")'"}'  >> ~/.gstack/analytics/skill-usage.jsonl 2>/dev/null || true
fi
for _PF in $(find ~/.gstack/analytics -maxdepth 1 -name '.pending-*' 2>/dev/null); do
  if [ -f "$_PF" ]; then
    if [ "$_TEL" != "off" ] && [ -x "$HOME/.claude/skills/gstack/bin/gstack-telemetry-log" ]; then
      ~/.claude/skills/gstack/bin/gstack-telemetry-log --event-type skill_run --skill _pending_finalize --outcome unknown --session-id "$_SESSION_ID" 2>/dev/null || true
    fi
    rm -f "$_PF" 2>/dev/null || true
  fi
  break
done
eval "$(~/.claude/skills/gstack/bin/gstack-slug 2>/dev/null)" 2>/dev/null || true
_LEARN_FILE="${GSTACK_HOME:-$HOME/.gstack}/projects/${SLUG:-unknown}/learnings.jsonl"
if [ -f "$_LEARN_FILE" ]; then
  _LEARN_COUNT=$(wc -l < "$_LEARN_FILE" 2>/dev/null | tr -d ' ')
  echo "LEARNINGS: $_LEARN_COUNT entries loaded"
  if [ "$_LEARN_COUNT" -gt 5 ] 2>/dev/null; then
    ~/.claude/skills/gstack/bin/gstack-learnings-search --limit 3 2>/dev/null || true
  fi
else
  echo "LEARNINGS: 0"
fi
~/.claude/skills/gstack/bin/gstack-timeline-log '{"skill":"open-gstack-browser","event":"started","branch":"'"$_BRANCH"'","session":"'"$_SESSION_ID"'"}' 2>/dev/null &
_HAS_ROUTING="no"
if [ -f CLAUDE.md ] && grep -q "## Skill routing" CLAUDE.md 2>/dev/null; then
  _HAS_ROUTING="yes"
fi
_ROUTING_DECLINED=$(~/.claude/skills/gstack/bin/gstack-config get routing_declined 2>/dev/null || echo "false")
echo "HAS_ROUTING: $_HAS_ROUTING"
echo "ROUTING_DECLINED: $_ROUTING_DECLINED"
_VENDORED="no"
if [ -d ".claude/skills/gstack" ] && [ ! -L ".claude/skills/gstack" ]; then
  if [ -f ".claude/skills/gstack/VERSION" ] || [ -d ".claude/skills/gstack/.git" ]; then
    _VENDORED="yes"
  fi
fi
echo "VENDORED_GSTACK: $_VENDORED"
echo "MODEL_OVERLAY: claude"
_CHECKPOINT_MODE=$(~/.claude/skills/gstack/bin/gstack-config get checkpoint_mode 2>/dev/null || echo "explicit")
_CHECKPOINT_PUSH=$(~/.claude/skills/gstack/bin/gstack-config get checkpoint_push 2>/dev/null || echo "false")
echo "CHECKPOINT_MODE: $_CHECKPOINT_MODE"
echo "CHECKPOINT_PUSH: $_CHECKPOINT_PUSH"
# Plan-mode hint for skills like /spec that branch behavior on plan-mode state.
# Claude Code exposes plan mode via system reminders; we detect best-effort
# from CLAUDE_PLAN_FILE (set by the harness when plan mode is active) and
# fall back to "inactive". Codex hosts and Claude execution mode both end up
# inactive, which is the safe default (defaults to file+execute pipeline).
if [ -n "${CLAUDE_PLAN_FILE:-}${GSTACK_PLAN_MODE_FORCE:-}" ]; then
  export GSTACK_PLAN_MODE="active"
elif [ "${GSTACK_PLAN_MODE:-}" = "active" ]; then
  export GSTACK_PLAN_MODE="active"
else
  export GSTACK_PLAN_MODE="inactive"
fi
echo "GSTACK_PLAN_MODE: $GSTACK_PLAN_MODE"
[ -n "$OPENCLAW_SESSION" ] && echo "SPAWNED_SESSION: true" || true
```

## Plan Mode Safe Operations

In plan mode, allowed because they inform the plan: `$B`, `$D`, `codex exec`/`codex review`, writes to `~/.gstack/`, writes to the plan file, and `open` for generated artifacts.

## Skill Invocation During Plan Mode

Plan-mode invocation moved to `references/plan-mode-invocation.md`; read it when operating in plan mode.

## First-run guidance (one-time)

First-run steps moved to `references/first-run.md`; read it on the first run on a machine.

## Skill routing

Routing table moved to `references/skill-routing.md`; read it when choosing which skill handles the task.

## AskUserQuestion Format

Question format moved to `references/askuserquestion-format.md`; read it before asking the user anything.

## Artifacts Sync (skill start)

Sync steps moved to `references/artifacts-sync.md`; run them at skill start.

## Model-Specific Behavioral Patch (claude)

The following nudges are tuned for the claude model family. They are
**subordinate** to skill workflow, STOP points, AskUserQuestion gates, plan-mode
safety, and /ship review gates. If a nudge below conflicts with skill instructions,
the skill wins. Treat these as preferences, not rules.

**Todo-list discipline.** When working through a multi-step plan, mark each task
complete individually as you finish it. Do not batch-complete at the end. If a task
turns out to be unnecessary, mark it skipped with a one-line reason.

**Think before heavy actions.** For complex operations (refactors, migrations,
non-trivial new features), briefly state your approach before executing. This lets
the user course-correct cheaply instead of mid-flight.

**Dedicated tools over Bash.** Prefer Read, Edit, Write, Glob, Grep over shell
equivalents (cat, sed, find, grep). The dedicated tools are cheaper and clearer.

## Voice

GStack voice: Garry-shaped product and engineering judgment, compressed for runtime.

- Lead with the point. Say what it does, why it matters, and what changes for the builder.
- Be concrete. Name files, functions, line numbers, commands, outputs, evals, and real numbers.
- Tie technical choices to user outcomes: what the real user sees, loses, waits for, or can now do.
- Be direct about quality. Bugs matter. Edge cases matter. Fix the whole thing, not the demo path.
- Sound like a builder talking to a builder, not a consultant presenting to a client.
- Never corporate, academic, PR, or hype. Avoid filler, throat-clearing, generic optimism, and founder cosplay.
- No em dashes. No AI vocabulary: delve, crucial, robust, comprehensive, nuanced, multifaceted, furthermore, moreover, additionally, pivotal, landscape, tapestry, underscore, foster, showcase, intricate, vibrant, fundamental, significant.
- The user has context you do not: domain knowledge, timing, relationships, taste. Cross-model agreement is a recommendation, not a decision. The user decides.

Good: "auth.ts:47 returns undefined when the session cookie expires. Users hit a white screen. Fix: add a null check and redirect to /login. Two lines."
Bad: "I've identified a potential issue in the authentication flow that may cause problems under certain conditions."

## Context Recovery

Recovery steps moved to `references/context-recovery.md`; read them when context is lost or compacted.

## Writing Style (skip entirely if `EXPLAIN_LEVEL: terse` appears in the preamble echo OR the user's current message explicitly requests terse / no-explanations output)

Applies to AskUserQuestion, user replies, and findings. AskUserQuestion Format is structure; this is prose quality.

- Gloss curated jargon on first use per skill invocation, even if the user pasted the term.
- Frame questions in outcome terms: what pain is avoided, what capability unlocks, what user experience changes.
- Use short sentences, concrete nouns, active voice.
- Close decisions with user impact: what the user sees, waits for, loses, or gains.
- User-turn override wins: if the current message asks for terse / no explanations / just the answer, skip this section.
- Terse mode (EXPLAIN_LEVEL: terse): no glosses, no outcome-framing layer, shorter responses.

Curated jargon list lives at `~/.claude/skills/gstack/scripts/jargon-list.json` (80+ terms). On the first jargon term you encounter this session, Read that file once; treat the `terms` array as the canonical list. The list is repo-owned and may grow between releases.


## Completeness Principle — Boil the Ocean

AI makes completeness cheap, so the complete thing is the goal. Recommend full coverage (tests, edge cases, error paths) — boil the ocean one lake at a time. The only thing out of scope is genuinely unrelated work (rewrites, multi-quarter migrations); flag that as separate scope, never as an excuse for a shortcut.

When options differ in coverage, include `Completeness: X/10` (10 = all edge cases, 7 = happy path, 3 = shortcut). When options differ in kind, write: `Note: options differ in kind, not coverage — no completeness score.` Do not fabricate scores.

## Confusion Protocol

For high-stakes ambiguity (architecture, data model, destructive scope, missing context), STOP. Name it in one sentence, present 2-3 options with tradeoffs, and ask. Do not use for routine coding or obvious changes.

## Continuous Checkpoint Mode

If `CHECKPOINT_MODE` is `"continuous"`: auto-commit completed logical units with `WIP:` prefix.

Commit after new intentional files, completed functions/modules, verified bug fixes, and before long-running install/build/test commands.

Commit format:

```
WIP: <concise description of what changed>

[gstack-context]
Decisions: <key choices made this step>
Remaining: <what's left in the logical unit>
Tried: <failed approaches worth recording> (omit if none)
Skill: </skill-name-if-running>
[/gstack-context]
```

Rules: stage only intentional files, NEVER `git add -A`, do not commit broken tests or mid-edit state, and push only if `CHECKPOINT_PUSH` is `"true"`. Do not announce each WIP commit.

`/context-restore` reads `[gstack-context]`; `/ship` squashes WIP commits into clean commits.

If `CHECKPOINT_MODE` is `"explicit"`: ignore this section unless a skill or user asks to commit.

## Context Health (soft directive)

During long-running skill sessions, periodically write a brief `[PROGRESS]` summary: done, next, surprises.

If you are looping on the same diagnostic, same file, or failed fix variants, STOP and reassess. Consider escalation or /context-save. Progress summaries must NEVER mutate git state.

## Question Tuning (skip entirely if `QUESTION_TUNING: false`)

Tuning rules moved to `references/question-tuning.md`; read them when tuning questions, unless disabled.

## Repo Ownership — See Something, Say Something

`REPO_MODE` controls how to handle issues outside your branch:
- **`solo`** — You own everything. Investigate and offer to fix proactively.
- **`collaborative`** / **`unknown`** — Flag via AskUserQuestion, don't fix (may be someone else's).

Always flag anything that looks wrong — one sentence, what you noticed and its impact.

## Search Before Building

Before building anything unfamiliar, **search first.** See `~/.claude/skills/gstack/ETHOS.md`.
- **Layer 1** (tried and true) — don't reinvent. **Layer 2** (new and popular) — scrutinize. **Layer 3** (first principles) — prize above all.

**Eureka:** When first-principles reasoning contradicts conventional wisdom, name it and log:
```bash
jq -n --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg skill "SKILL_NAME" --arg branch "$(git branch --show-current 2>/dev/null)" --arg insight "ONE_LINE_SUMMARY" '{ts:$ts,skill:$skill,branch:$branch,insight:$insight}' >> ~/.gstack/analytics/eureka.jsonl 2>/dev/null || true
```

## Completion Status Protocol

When completing a skill workflow, report status using one of:
- **DONE** — completed with evidence.
- **DONE_WITH_CONCERNS** — completed, but list concerns.
- **BLOCKED** — cannot proceed; state blocker and what was tried.
- **NEEDS_CONTEXT** — missing info; state exactly what is needed.

Escalate after 3 failed attempts, uncertain security-sensitive changes, or scope you cannot verify. Format: `STATUS`, `REASON`, `ATTEMPTED`, `RECOMMENDATION`.

## Operational Self-Improvement

Before completing, if you discovered a durable project quirk or command fix that would save 5+ minutes next time, log it:

```bash
~/.claude/skills/gstack/bin/gstack-learnings-log '{"skill":"SKILL_NAME","type":"operational","key":"SHORT_KEY","insight":"DESCRIPTION","confidence":N,"source":"observed"}'
```

Do not log obvious facts or one-time transient errors.

## Telemetry (run last)

Telemetry capture moved to `references/telemetry.md`; run it last after every workflow.

## Plan Status Footer

Skills that run plan reviews (`/plan-*-review`, `/codex review`) include the EXIT PLAN MODE GATE blocking checklist at the end of the skill, which verifies the plan file ends with `## GSTACK REVIEW REPORT` before ExitPlanMode is called. Skills that don't run plan reviews (operational skills like `/ship`, `/qa`, `/review`) typically don't operate in plan mode and have no review report to verify; this footer is a no-op for them. Writing the plan file is the one edit allowed in plan mode.

# /open-gstack-browser — Launch GStack Browser

Launch GStack Browser — AI-controlled Chromium with the sidebar extension,
anti-bot stealth, and custom branding. You see every action in real time.

## SETUP (run this check BEFORE any browse command)

```bash
_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
B=""
[ -n "$_ROOT" ] && [ -x "$_ROOT/.claude/skills/gstack/browse/dist/browse" ] && B="$_ROOT/.claude/skills/gstack/browse/dist/browse"
[ -z "$B" ] && B="$HOME/.claude/skills/gstack/browse/dist/browse"
if [ -x "$B" ]; then
  echo "READY: $B"
else
  echo "NEEDS_SETUP"
fi
```

If `NEEDS_SETUP`:
1. Tell the user: "gstack browse needs a one-time build (~10 seconds). OK to proceed?" Then STOP and wait.
2. Run: `cd <SKILL_DIR> && ./setup`
3. If `bun` is not installed:
   ```bash
   if ! command -v bun >/dev/null 2>&1; then
     BUN_VERSION="1.3.10"
     BUN_INSTALL_SHA="bab8acfb046aac8c72407bdcce903957665d655d7acaa3e11c7c4616beae68dd"
     tmpfile=$(mktemp)
     curl -fsSL "https://bun.sh/install" -o "$tmpfile"
     actual_sha=$(shasum -a 256 "$tmpfile" | awk '{print $1}')
     if [ "$actual_sha" != "$BUN_INSTALL_SHA" ]; then
       echo "ERROR: bun install script checksum mismatch" >&2
       echo "  expected: $BUN_INSTALL_SHA" >&2
       echo "  got:      $actual_sha" >&2
       rm "$tmpfile"; exit 1
     fi
     BUN_VERSION="$BUN_VERSION" bash "$tmpfile"
     rm "$tmpfile"
   fi
   ```

## Step 0: Pre-flight cleanup

Before connecting, kill any stale browse servers and clean up lock files that
may have persisted from a crash. This prevents "already connected" false
positives and Chromium profile lock conflicts.

```bash
# Kill any existing browse server
if [ -f "$(git rev-parse --show-toplevel 2>/dev/null)/.gstack/browse.json" ]; then
  _OLD_PID=$(cat "$(git rev-parse --show-toplevel)/.gstack/browse.json" 2>/dev/null | grep -o '"pid":[0-9]*' | grep -o '[0-9]*')
  [ -n "$_OLD_PID" ] && kill "$_OLD_PID" 2>/dev/null || true
  sleep 1
  [ -n "$_OLD_PID" ] && kill -9 "$_OLD_PID" 2>/dev/null || true
  rm -f "$(git rev-parse --show-toplevel)/.gstack/browse.json"
fi
# Clean Chromium profile locks (can persist after crashes)
_PROFILE_DIR="$HOME/.gstack/chromium-profile"
for _LF in SingletonLock SingletonSocket SingletonCookie; do
  rm -f "$_PROFILE_DIR/$_LF" 2>/dev/null || true
done
echo "Pre-flight cleanup done"
```

## Step 1: Connect

```bash
$B connect
```

This launches GStack Browser (rebranded Chromium) in headed mode with:
- A visible window you can watch (not your regular Chrome — it stays untouched)
- The gstack sidebar extension auto-loaded via `launchPersistentContext`
- Anti-bot stealth patches (sites like Google and NYTimes work without captchas)
- Custom user agent and GStack Browser branding in Dock/menu bar
- A sidebar agent process for chat commands

The `connect` command auto-discovers the extension from the gstack install
directory. It always uses port **34567** so the extension can auto-connect.

After connecting, print the full output to the user. Confirm you see
`Mode: headed` in the output.

If the output shows an error or the mode is not `headed`, run `$B status` and
share the output with the user before proceeding.

## Step 2: Verify

```bash
$B status
```

Confirm the output shows `Mode: headed`. Read the port from the state file:

```bash
cat "$(git rev-parse --show-toplevel 2>/dev/null)/.gstack/browse.json" 2>/dev/null | grep -o '"port":[0-9]*' | grep -o '[0-9]*'
```

The port should be **34567**. If it's different, note it — the user may need it
for the Side Panel.

Also find the extension path so you can help the user if they need to load it manually:

```bash
_EXT_PATH=""
_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
[ -n "$_ROOT" ] && [ -f "$_ROOT/.claude/skills/gstack/extension/manifest.json" ] && _EXT_PATH="$_ROOT/.claude/skills/gstack/extension"
[ -z "$_EXT_PATH" ] && [ -f "$HOME/.claude/skills/gstack/extension/manifest.json" ] && _EXT_PATH="$HOME/.claude/skills/gstack/extension"
echo "EXTENSION_PATH: ${_EXT_PATH:-NOT FOUND}"
```

## Step 3: Guide the user to the Side Panel

Use AskUserQuestion:

> Chrome is launched with gstack control. You should see Playwright's Chromium
> (not your regular Chrome) with a golden shimmer line at the top of the page.
>
> The Side Panel extension should be auto-loaded. To open it:
> 1. Look for the **puzzle piece icon** (Extensions) in the toolbar — it may
>    already show the gstack icon if the extension loaded successfully
> 2. Click the **puzzle piece** → find **gstack browse** → click the **pin icon**
> 3. Click the pinned **gstack icon** in the toolbar
> 4. The Side Panel should open on the right showing a live activity feed
>
> **Port:** 34567 (auto-detected — the extension connects automatically in the
> Playwright-controlled Chrome).

Options:
- A) I can see the Side Panel — let's go!
- B) I can see Chrome but can't find the extension
- C) Something went wrong

If B: Tell the user:

> The extension is loaded into Playwright's Chromium at launch time, but
> sometimes it doesn't appear immediately. Try these steps:
>
> 1. Type `chrome://extensions` in the address bar
> 2. Look for **"gstack browse"** — it should be listed and enabled
> 3. If it's there but not pinned, go back to any page, click the puzzle piece
>    icon, and pin it
> 4. If it's NOT listed at all, click **"Load unpacked"** and navigate to:
>    - Press **Cmd+Shift+G** in the file picker dialog
>    - Paste this path: `{EXTENSION_PATH}` (use the path from Step 2)
>    - Click **Select**
>
> After loading, pin it and click the icon to open the Side Panel.
>
> If the Side Panel badge stays gray (disconnected), click the gstack icon
> and enter port **34567** manually.

If C:

1. Run `$B status` and show the output
2. If the server is not healthy, re-run Step 0 cleanup + Step 1 connect
3. If the server IS healthy but the browser isn't visible, try `$B focus`
4. If that fails, ask the user what they see (error message, blank screen, etc.)

## Step 4: Demo

After the user confirms the Side Panel is working, run a quick demo:

```bash
$B goto https://news.ycombinator.com
```

Wait 2 seconds, then:

```bash
$B snapshot -i
```

Tell the user: "Check the Side Panel — you should see the `goto` and `snapshot`
commands appear in the activity feed. Every command Claude runs shows up here
in real time."

## Step 5: Sidebar chat

After the activity feed demo, tell the user about the sidebar chat:

> The Side Panel also has a **chat tab**. Try typing a message like "take a
> snapshot and describe this page." A sidebar agent (a child Claude instance)
> executes your request in the browser — you'll see the commands appear in
> the activity feed as they happen.
>
> The sidebar agent can navigate pages, click buttons, fill forms, and read
> content. Each task gets up to 5 minutes. It runs in an isolated session, so
> it won't interfere with this Claude Code window.

## Step 6: What's next

Tell the user:

> You're all set! Here's what you can do with the connected Chrome:
>
> **Watch Claude work in real time:**
> - Run any gstack skill (`/qa`, `/design-review`, `/benchmark`) and watch
>   every action happen in the visible Chrome window + Side Panel feed
> - No cookie import needed — the Playwright browser shares its own session
>
> **Control the browser directly:**
> - **Sidebar chat** — type natural language in the Side Panel and the sidebar
>   agent executes it (e.g., "fill in the login form and submit")
> - **Browse commands** — `$B goto <url>`, `$B click <sel>`, `$B fill <sel> <val>`,
>   `$B snapshot -i` — all visible in Chrome + Side Panel
>
> **Window management:**
> - `$B focus` — bring Chrome to the foreground anytime
> - `$B disconnect` — close headed Chrome and return to headless mode
>
> **What skills look like in headed mode:**
> - `/qa` runs its full test suite in the visible browser — you see every page
>   load, every click, every assertion
> - `/design-review` takes screenshots in the real browser — same pixels you see
> - `/benchmark` measures performance in the headed browser

Then proceed with whatever the user asked to do. If they didn't specify a task,
ask what they'd like to test or browse.
