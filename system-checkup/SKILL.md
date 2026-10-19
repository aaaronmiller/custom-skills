---
name: system-checkup
description: Periodic full checkup of the SPECTRE-16 Windows 11 + WSL2 workstation - Windows Update/servicing health, memory and telemetry, Process Lasso Pro rules, event-log errors and crashes, Bluetooth/input drops, storage and cache reclaim, npm vs pnpm/bun hygiene, outdated software and modernization picks, user-folder organization (living document), and a dark HTML report plus a dry-run removal script. Use when the user asks for a system checkup, health check, "bring the system up to date", monthly maintenance, cleanup/reclaim space, re-audit Process Lasso, or "run the checkup again". Grunt work is delegated to headless omp workers on opencode-go/muse-spark-1.3-contributor.
---

# SPECTRE-16 system checkup

A repeatable version of the 2026-10-13 checkup. Read `references/machine-profile.md` first: it lists the traps that cost hours last time. `references/baseline-2026-10.md` holds the numbers to compare against.

**Machine-specific.** Paths, hardware, user names and known traps are hardwired for SPECTRE-16; adapt `references/machine-profile.md` and the script defaults before using it anywhere else.

**Source of truth:** `~/code/custom-skills/system-checkup` in WSL (repo `aaaronmiller/custom-skills`). Windows Claude Code loads a deployed copy from `C:\Users\Administrator\.claude\skills\system-checkup` (a real copy, so the skill works while WSL is wedged). Edit the repo copy, then run `bash ~/code/custom-skills/system-checkup/scripts/deploy-windows.sh`. Commands below use the Windows copy's paths.

## Ground rules
- **Never delete during the checkup.** Everything is read-only except: SFC's own repairs, re-unticking HID power saving (Elevated-Audit), and files written under `C:\performance-diagnostics\checkup-YYYYMMDD\`. Deletions happen only through `Remove-CheckupItems.ps1`, which the user runs (dry run by default).
- **Never** `wsl --shutdown`, reboot, restart WezTerm, stop agents, or touch `C:\0.defenderexclusions` (ignore it completely). Agents run 24/7 inside WSL.
- Service/registry/Lasso changes are proposals until the user approves them (`references/improvement-pass.md`). Once approved, do not ask again.
- Verify every load-bearing claim a worker makes (build numbers, ini formats, file names) before it reaches the report.
- Protected, always: the Desktop `Bitsum ... [FTUApps]` folder (live Lasso config), `Documents\chetaz` (Obsidian vault), browser profile data other than cache folders, `.claude`, `.config`, `.ssh`, the WSL distro package, `D:\SPECTRE-16-UGLYBETTY.tibx`, the living document.

## Setup
```bash
CK=/c/performance-diagnostics/checkup-$(date +%Y%m%d); SK=/c/Users/Administrator/.claude/skills/system-checkup
mkdir -p $CK/{raw,workers,report,scripts,removal}
cp $SK/scripts/* $CK/scripts/; cp $SK/scripts/Remove-CheckupItems.ps1 $CK/removal/; cp $SK/templates/report-template.html $CK/report/
bash $SK/scripts/render-briefs.sh $SK $CK checkup-$(date +%Y%m%d) $(date +%F)
```
Write files with the Write tool or Bash using **absolute paths** (the PowerShell tool may only write under system32). Run `.ps1` files via `powershell.exe -NoProfile -ExecutionPolicy Bypass -File <abs path>` from Bash.

## Phase 1 - history and state (you, ~10 min)
1. Read the previous checkup's report/baseline and `C:\performance-diagnostics\*.md`; grep older Claude transcripts in `~/.claude/projects/*/*.jsonl` for anything since then.
2. `Perf-Telemetry-v2.ps1 -Status` (sampler alive?) and `-Report -Days 45`.
3. Insider/WU: `HKLM\SOFTWARE\Microsoft\WindowsSelfHost\Applicability`, build/UBR, then WindowsUpdateClient events 19/20/31/41 grouped by title and errorCode (parse event XML `updateTitle`/`errorCode`).

## Phase 2 - collectors (run in parallel, background)
- `collect-system.ps1 -OutDir $CK\raw` (programs, appx, drivers, processes, services, tasks, startup, package managers, winget; about 3 min).
- `collect-events.ps1 -OutFile $CK\report\events.json` (WU failures/week, exhaustion/day, unclean shutdowns, BT drops/day, top errors).
- `python -I scan_storage.py $CK/raw/storage` (AppData, caches, temp with lock state, user-folder inventories, node_modules, large files, hash duplicates; about 30 min because D: is a slow USB card).
- WSL deep du: `wsl.exe -d Ubuntu -e bash -lc 'sudo -n nice -n19 ionice -c3 du -x --block-size=1M --max-depth=4 / | sort -rn | head -400 > /mnt/c/.../raw/wsl-du/du-root-d4.txt'`.
- Telemetry history aggregation for charts: see the inline Python in the 2026-10 transcript, or extend `build_report_data.py`.

## Phase 3 - omp workers (grunt work)
Launch each as its own **background** Bash task (a nohup'd child dies with SIGHUP when wsl.exe exits):
```bash
MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -e bash -l /mnt/c/Users/Administrator/.claude/skills/system-checkup/scripts/run-omp-worker.sh /mnt/c/performance-diagnostics/checkup-YYYYMMDD W1-wsl-audit 45m high
```
| Brief | Job | Needs first |
|---|---|---|
| W1-wsl-audit | WSL health, caches, node_modules, outdated globals/apt | nothing |
| W4-lasso-research | Lasso features + live vs dead ini | nothing |
| W5-insider-upgrade | current Insider builds, ISO route | nothing |
| W3-software-modernize | outdated/EOL/duplicates + Rust/RE-era picks | collect-system done, W1 done |
| W2-folder-organize | living document vN+1 DATA | scan_storage done (needs dupes.csv) |
Smoke-test first with a trivial brief if omp was updated. Failure signatures: exit 127 = `bash -l` missing (PATH); "No API key found for opencode-go" = not a login shell; exit 129 = launched with nohup instead of as a background task. Auto-mode refuses `--auto-approve`; do not add it.

Verify outputs: W5 build numbers against learn.microsoft.com and the UUP dump API (`references/insider-upgrade.md`); W4 ini formats against Bitsum's ini reference; W2 names against the inventories (`380/382 matched` last time).

## Phase 4 - elevated audit (one UAC prompt, 30-40 min)
```bash
powershell.exe -NoProfile -Command "Start-Process powershell -Verb RunAs -Wait -WindowStyle Minimized -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File','C:\performance-diagnostics\checkup-YYYYMMDD\scripts\Elevated-Audit.ps1'"
```
Covers RebootPending, WU policy, WER triage, HID power-saving, SSD health, VSS, BitLocker, Defender, elevated process affinity (Lasso verification), admin cache sizes, battery report, SFC, DISM ScanHealth and AnalyzeComponentStore, CBS errors. The log is UTF-16: read with `iconv -f UTF-16`. Get the SFC unrepairable list with `grep -a "<date>.*\[SR\] Cannot repair member file" C:/Windows/Logs/CBS/CBS.log`.

## Phase 5 - cleanup plan, approval page, removal script
```bash
python -I $CK/scripts/build_removal_manifest.py C:/performance-diagnostics/checkup-YYYYMMDD     # caches, temp, WSL, system, hash dupes
python -I $CK/scripts/build_cleanup_plan.py C:/performance-diagnostics/checkup-YYYYMMDD        # + living-doc organize/stage + Downloads type sort
python -I $CK/scripts/build_approval_page.py C:/performance-diagnostics/checkup-YYYYMMDD       # -> removal/Cleanup-Approvals.html
```
The user decides per item in `Cleanup-Approvals.html` (by folder, approve/reject, exports a JSON per folder or for everything). Then `Remove-CheckupItems.ps1 -Approvals <export>` (dry run) and `-Execute`. Only approved ids run. Check that every cache item states plainly whether it signs anything out (none should). Security-flagged items are filtered out by design. Never rebuild the plan while the user is mid-approval: ids are path hashes and stay stable, but the plan_id changes and old exports are refused.

## Phase 6 - living document
`C:\Users\Administrator\Downloads\downloads-desktop-cleanup.livingdoc`: back up `public/app.js`, `content/index.json` and `data/annotations.json`; swap in W2's DATA (adapt `update_livingdoc_v3.mjs`: version, ids, worklog); refresh `content/sections/*.md` (Read before Write); add `worklogs/YYYY-MM-DD-*.md`; then `node validate.mjs` and `node --check public/app.js`.

## Phase 7 - report
1. `python -I build_report_data.py <CK>` then edit the narrative in `report/report-template.html` (every headline states the finding; update numbers, tables and the plan).
2. `python -I build_report.py <CK> --dism "<ScanHealth summary>"`, then `node --check` on the extracted script.
3. Publish with the Artifact tool (dark theme, Poppins/Lora/IBM Plex Mono, chart series #d4683f and #4f8fd6 as validated; never more than two categorical series). Republishing the same file path keeps the URL.
4. Update `references/baseline-*.md` with the new numbers.

## Phase 8 - what to hand the user
- The report link and the plan in four windows: now (no restart), maintenance window (agents idle), restart, after restart.
- Exactly what was changed (should be almost nothing) and what awaits approval (improvement pass, removal script, ISO staging).
- Anything the auto-mode classifier refused, and why.
