# Retrospective log (meta-analysis between rounds)

Each entry: what was measured, what went wrong, what changed in the method. Newest last.

## v0.1 -> v0.2 (2026-10-14, round 1: Desktop 93 items, Documents 78 items; worker brief v1)
Measured
- Desktop: 78 keep, 5 duplicate, 4 superseded, 5 temp, 1 unsure; confidence 68 high / 24 medium / 1 low; 55 distinct destinations (0.59 per item).
- Documents: 68 keep, 4 duplicate, 6 temp, 0 unsure; 31 high / 47 medium; 52 destinations (0.67 per item).
- Every removal carried hash or diff evidence. Intents read as plausible on spot checks.

Problems
1. Fragmentation: one-file subfolders such as `Documents/Personal & admin/System-audits/2026-03-17`; destinations per item 0.6+ (target <= 0.25).
2. Broke a tool dependency: moved the Desktop `.claude` folder (Claude Code project settings) into `Scripts & configs`.
3. Broke app dependencies: moved `Documents\Image-Line` (FL Studio data) to `~/Music` and `Documents\Virtual Machines` (VMware) to `Disk images`.
4. Inconsistent project naming (`2026-08 ARDF-model-ranking` vs `2026-08 OpenWhispr transcripts`).

Changes
- New decision `leave-in-place` for dot-folders, tool folders, app-owned folders and live working directories; `gather_facts.py` adds an `app_owned` / `tool_folder` hint; the worker brief lists the owner's app-owned folders.
- Taxonomy rules: max depth, no single-item subfolders outside projects, project naming `YYYY-MM Topic words`.
- Later chunks receive the list of project names already in use.
- Review step (Claude) must check every move of a folder for app/tool dependence.
- Canonicalize step folds single-item folders and normalizes names across chunks.

## v0.2 -> v0.3 (2026-10-15, round 2: Downloads 381 items on brief v1; Pictures/Music/Videos 102, home 57, D: 15 on brief v2)
Measured (metrics.py, before review)
- Downloads: 0.17-0.22 destinations per item (good); 23 + 22 removals, every one hash/diff-evidenced; 1.6% / 0% unsure.
- Brief v2 chunks: 0.18-0.23 destinations per item; `leave-in-place` used correctly for scoop, Postman, CrossDevice, vscode-remote-wsl, iTunes, Ableton, Logic, Screenshots, Captures; workers finished in ~2 minutes each.
- Overall 726 items: 626 keep, 81 removals (1.2 GB staged), 14 leave-in-place, 5 unsure (0.7%).

Problems
1. Nesting conflict: the Desktop dump folder was both an item (moved whole) and a root (children sorted) - the plans collide.
2. Wrapper folders: a folder item was given a dest named after itself (`Archives & backups/Apple Notes HTML export` for `Notes Export-HTML`), which is most of the remaining fragmentation in Desktop/Documents (0.57-0.65 per item).
3. Type-named roots: inside Music the worker nested `Media/Audio/<album>`.
4. Junctions (`Documents\My Music` etc.) were treated as folders to move.
5. Registry hives' transaction files in the home folder (`NTUSER.DAT{...}.regtrans-ms`) reached the item list (exact-name skip list missed them).
6. Unsure share is low (0.7%), below the 2% floor: workers may be over-confident on items with thin evidence; the review must test intents, not just removals.
7. Spelling drift across one chunk (`AI generated` / `AI-generated`, `Skill packs` / `Skills packs`).
8. The page grouped by full destination path: 224 cards, too many to skim.

Changes
- gather_facts: nested roots and junctions/symlinks are untouched; skip lists accept glob patterns (`ntuser*`); new `referenced_by` fact from config files (`.wslconfig`, terminal settings, PowerShell profiles, shell rc files, fstab, startup/task/service inventories) and from the registry (sound-scheme files, Run keys) - found `Documents\Codex` (PowerShell profile) and `Music\evil-laugh.wav` (sound event); zip listings as content; sampled hash for files over 256 MB; `live_hint`; `--only` and `--facts-only` for partial refreshes.
- Worker brief v3: rules for wrapper folders, type-named roots, one spelling per folder, `referenced_by` and `live_hint` mean leave-in-place.
- Review brief v2: the same placement checks, missing-item decisions, intent recovery via neighbouring downloads and `cass`.
- Page: one card per top-level folder per location (subfolders nested with their own toggles), tree collapsed, "Show only what needs you"; referenced items that a decision still moves are flagged and start unticked.
- New `metrics.py` (step 3) and `render_briefs.py` (fills briefs from the config, normalizes existing project names so later chunks converge).

### Round 2 review results (Claude review of all 7 chunks, 2026-10-15)
- 395 tool calls across 5 reviewers + 1 canonicalizer. Corrections: Downloads 73 + 38, Desktop 79, Documents 50, media 47, home 10, D: 11.
- Removals: 81 proposed -> 6 overturned (a VSIX from a different publisher; `hosts` identical to the live hosts file; an Intel Advisor project; the bytepad notes folder; a saved YouTube page with real content; `hermes - Copy` holding a report the newer folder overwrote) and ~10 added (missed duplicates and superseded installers, each hash- or version-checked). Final: 85 staged (1.7 GB).
- Leave-in-place grew from 14 to 94. Most came from evidence that only an agent with tools found: app settings files naming a folder (AB Download Manager, Zettlr, X-Mouse), Startup shortcuts and icon paths, the active cursor scheme, the registry sound scheme, agent cron outputs, a kernel build script writing `.wslconfig`.
- All 5 `unsure` items got evidenced intents (agent history via `cass`, file contents, EXIF), so the Unsure pile ended empty; the page's "needs you" view therefore also lists low-confidence moves (15) and guard flags.
- After review: 0.14 destinations per item, 2 single-item folders, 0 moves of referenced or app-owned items except one checked case (`Documents\Obsidian` is not a registered vault).
- Orchestrator rules added after canonicalize (now in the taxonomy): category folders are never created in the home root (they go under `~/Documents`); inside type-named roots (Pictures, Music, Videos) there is no `Projects` or `Media` level.
- Side effects to avoid: `git status` touched `.git` timestamps in two repos (review brief now requires `--no-optional-locks`); a credential-name scan was blocked by the damage-control hook (fine; reviewers rely on the security pattern instead).
- Cost note: the review is the expensive step (~1.6 M subagent tokens for 722 items) but it produced most of the safety value. Next time, give the worker the same tools-based checks (settings files, shortcuts, registry) in the facts so the review has less to find.
