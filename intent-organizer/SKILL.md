---
name: intent-organizer
description: Organize cluttered folders (Downloads, Desktop, Documents, home, drive roots, dump folders) by working out each item's INTENT - why it is there, what the owner was doing with it, what they would want done - then hand the owner a short group-level approval page with full undo. Scripts only gather facts; every keep / move / remove / unsure decision is made by an LLM reasoning over those facts, and a second model challenges the risky ones. Removes only what is superseded, duplicated or temporary; everything else is organized by type, purpose and project (clustered by download dates). Use when the user wants to organize or declutter folders, tame a messy Downloads/Desktop, deal with filesystem bloat or structure, sort installers, find what is safe to remove, or make sense of a dump folder. Generic method; owner-specific knowledge lives in references/user-profile.md.
license: MIT
metadata:
  author: Aaron Miller (with Claude)
  version: "0.2.0"
  builds_on: "file-organizer (scope), intent-archaeology (deterministic facts + model verdicts + retrospective loop), cass-cli (intent recovery from agent sessions)"
---

# Intent Organizer

Most "organize my files" tools sort by extension and delete by age. That is wrong for an owner who keeps things on purpose. This skill treats every item as something someone saved for a reason, reconstructs that reason, and files the item where that reason says it belongs. Only three things leave: older versions of something newer that is here, true duplicates, and temp junk that was never meant to be kept. Anything the model cannot explain goes into a small "Unsure" pile for the owner instead of being guessed.

Read `references/steering.md` first. It is the contract: the owner's rules, in their words. Then read `references/user-profile.md` for who the owner is (projects, devices, habits, protected paths). `references/retrospective.md` lists what went wrong in past runs; do not repeat those mistakes.

## The pipeline (anchored: every script and prompt maps to a step)

Everything is driven by one config file (copy `templates/organize.config.example.json`): work folder, roots (with chunk names, skip patterns, dump folders), protected paths, security pattern, app-owned folder patterns, config files to scan for path references, installed-program sources. All scripts take that config as their first argument (`python -I <script> <config>`).

| Step | Who | Tool | Output |
|---|---|---|---|
| 0. Scope | you | `references/user-profile.md` + the config; ask nothing the profile answers | config file |
| 1. Gather facts | script | `scripts/gather_facts.py <config> [--only "<labels>"] [--facts-only]` | `org-items.json`, `chunk-*.json` (<= 190 items), `installed-*.txt` |
| 2. Reason | LLM workers | `scripts/render_briefs.py <config>` then `scripts/run_worker.sh <brief> 55m high` per chunk | `decisions-<chunk>.json` |
| 3. Meta-analysis | you | `scripts/metrics.py <config>` after the FIRST chunk returns, then each round | brief revised, entry in `references/retrospective.md` |
| 4. Challenge | second model | `render_briefs.py <config> --kind review` + Claude agents (Workflow or Agent) | `review-<chunk>.json` corrections |
| 5. Canonicalize | one LLM pass | `render_briefs.py <config> --kind canonicalize` + one agent | `canonical.json` (dest map + group summaries) |
| 6. Render | script | `scripts/build_page.py <config>` + `templates/organizer.html` | `Organizer.html`, `org-plan.json` |
| 7. Apply / undo | owner runs | `scripts/Apply-Plan.ps1 -Plan org-plan.json -Approvals <export>` (dry run, then `-Execute`); `scripts/Undo-Moves.ps1 -Log run-*.csv` | moved files, run log |
| 8. Retrospective | you | `metrics.py` again + review notes -> `references/retrospective.md`, bump version | better skill next time |

### Step 1 - facts only
`gather_facts.py` records per item: created date (about when it was downloaded), modified date, size, type, folder summaries (children, file types, README excerpt, project markers, newest write), a REDACTED excerpt for text/markdown/HTML/Office/PDF/zip listings, config KEYS only (never values), installer hints (platform, product tokens, version, the installed program it might match, older/same/newer), duplicates (full hash; sampled hash over 256 MB), version families, temp markers, `app_owned` (dot-folders, node_modules, configured app folders), `referenced_by` (which config/startup/task file mentions the path), `live_hint` (project folder written to recently), and any earlier note. Protected paths, security-flagged names, junctions/symlinks, shortcuts, `desktop.ini` and nested roots are listed as untouched and never read. The hints are heuristics and may be wrong; the model decides. Re-run with `--facts-only` to refresh facts after decisions exist without rewriting chunks.

### Step 2 - reasoning workers
Default worker: headless `omp` on `opencode-go/muse-spark-1.3-contributor`, one per chunk, in parallel (see the owner profile for the launch line). `render_briefs.py` fills the brief with the owner profile, the app-owned list, the project names other chunks already use, and the installed-program lists. Each item gets: intent, want, decision, destination, confidence, evidence. Workers may read files further when the excerpt is not enough. A 100-200 item chunk takes 2-15 minutes.

### Step 3 - meta-analysis (after the first chunk, then every round)
`metrics.py` reports per chunk: decision and confidence mix, destinations per item (target <= 0.25), single-item folders, depth violations, project-name style, removals that are low confidence or lack evidence (must be none), moves of app-owned / referenced / live items (must be none), nesting conflicts, and items without a decision. Read a sample of intents too. Fix the BRIEF, not just the output, and log what changed in `references/retrospective.md`.

### Step 4 - challenge
A different model (Claude agents) reviews each chunk adversarially: refute every removal it cannot confirm itself (hash, version, existence of the kept copy), catch moves that would break an app or tool, check installers against the installed list, fix placement (wrapper folders, type-named roots, single-item folders), try once to recover intent for `unsure` items from neighbouring downloads and agent history (`cass`), and decide items that appeared after the worker ran. Corrections go to `review-<chunk>.json`, override the worker, and are marked "reviewed" on the page. Its `notes` feed the retrospective.

### Step 5 - canonicalize
One pass over every destination across all chunks: merge near-duplicate names, fold single-item subfolders, cap depth, normalize project names, and write a 1-2 sentence summary per destination (shown on the page).

### Step 6-7 - the owner's part (keep it small)
The page has one section per location and one card per TOP-LEVEL folder (Installers, Projects, Documents, ...; typically 6-10 per location), each with a toggle; subfolders sit inside the card with their own toggles and a summary, and every item can be opened to see its intent, the owner's likely wish and the evidence. Everything is ON by default except nothing: the owner unticks what they disagree with. Removals are staged to `_REVIEW-then-delete` in the same location, never deleted. `_Unsure` is the only pile that needs personal attention, and "Show only what needs you" filters to it. Export writes `organizer-approvals.json`; the apply script refuses approvals from a different plan id, never overwrites, and logs every move for `Undo-Moves.ps1`. Mechanical guards in `build_page.py`: an item inside a moving folder stays put; name clashes are flagged and skipped.

## Decision rules (summary; full text in `prompts/worker-brief.md`)
- `keep-organize` is the default. Things are here on purpose.
- `remove-superseded` only when a newer version of the same thing is present (or installed and the installer is older).
- `remove-duplicate` only when the same content exists elsewhere (hash or diff evidence).
- `remove-temp` only for things never meant to be kept (zero-byte, partial downloads, lock files, OS metadata forks, regenerable crash reports/logs with no lasting value).
- `leave-in-place` for anything something else depends on by path: dot-folders (`.claude`, `.git`, `.vscode`, `.obsidian`), `node_modules`, app-owned folders created where the app expects them (e.g. `Documents\Image-Line`, `Documents\Virtual Machines`, `Documents\WindowsPowerShell`), live project/working directories, shortcuts and `desktop.ini`.
- `unsure` whenever intent or the owner's wish cannot be worked out. Never guess a removal; low confidence + removal is forbidden.

## Hard safety rules
- Nothing is deleted by this skill. Removals are moves into `_REVIEW-then-delete`; every move is logged and reversible.
- Never read, move or list contents of security-flagged items or protected paths from the profile.
- Never send secrets to a model: excerpts are redacted; configs contribute key names only.
- On Windows PowerShell 5.1, read JSON with `-Encoding UTF8` (non-ASCII file names otherwise break).

## Files
`scripts/gather_facts.py` · `scripts/render_briefs.py` · `scripts/run_worker.sh` · `scripts/metrics.py` · `scripts/build_page.py` · `scripts/Apply-Plan.ps1` · `scripts/Undo-Moves.ps1` · `prompts/worker-brief.md` · `prompts/review-brief.md` · `prompts/canonicalize-brief.md` · `templates/organizer.html` · `templates/organize.config.example.json` · `references/steering.md` · `references/user-profile.md` · `references/taxonomy.md` · `references/retrospective.md`

Windows notes: run Python from Git Bash with `MSYS_NO_PATHCONV=1` when passing `//wsl.localhost/...` or `C:\...` paths; keep `.ps1` files ASCII; PowerShell 5.1 must read JSON with `-Encoding UTF8`.
