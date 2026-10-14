# Worker W2 — Update the "Downloads & Desktop Cleanup" living document to v3 and extend it to every user folder + temp dirs

You classify files for a human decision surface. You do NOT move, rename or delete anything. Use `read`, `bash` (read-only: ls, stat, head, file, python3/jq for parsing), `glob`, `grep`, `find`, and `write` for your two output files only. Today is {{DATE}}.

## Background
In July a "living document" was generated for cleaning up Downloads (~354 items) and Desktop (~130 items) but it was NEVER applied. Its decision data (exact schema you must reuse) is at:
`/mnt/c/performance-diagnostics/{{CHECKUP}}/raw/livingdoc-july-DATA.json`
Schema: `{meta, sectionIntros{sectionName: intro}, groups:[{id, section, loc, title, fn, rec:{label,detail}, alt:{label,detail}, files:[string]}], security:{id, loc, title, fn, target, rec, alt, files:[string]}, folders:[{loc, name}]}`.
Each `files` entry is a human-readable string: the exact file/folder name first, optionally followed by two spaces and a parenthetical note, e.g. `"T3-Code-0.0.13-x64 (1).exe  (134.8 MB, identical to the non-(1) copy)"`. The UI keys per-file decisions on this string, so the name must come first and be exact.

## Current inventories (read these — produced today by a read-only scanner)
Directory: `/mnt/c/performance-diagnostics/{{CHECKUP}}/raw/storage/`
- `inv-Downloads.csv`, `inv-Desktop.csv`, `inv-Documents.csv`, `inv-Pictures.csv`, `inv-Videos.csv`, `inv-Music.csv`, `inv-HOME_ROOT.csv` (items directly in C:\Users\Administrator), `inv-C_ROOT.csv`, `inv-D_ROOT.csv`, `inv-OneDrive.csv`, `inv-Favorites.csv`, `inv-Links.csv`, `inv-Searches.csv` — columns `name,type,ext,mb,files,mtime,newest` (top-level items of each folder).
- `files-Downloads.csv`, `files-Desktop.csv`, `files-Documents.csv` — every file (`rel,mb,mtime`), node_modules/.git excluded. Use to look inside folders.
- `temp-items.csv` — top-level items of %TEMP% and C:\Windows\Temp etc. with `age_days` and `lock` state.
- `dupes.csv` (may or may not exist yet) — duplicate groups `group,keep_suggest,mb,hash,path,mtime` (`hash` = full or sampled blake2b).
- `large-files.csv` — files >= 500 MB.
You may `ls`/`stat` the real folders under `/mnt/c/Users/Administrator/...` read-only to resolve ambiguity, but prefer the CSVs (9p is slow).

## HARD PROTECTION LIST — these must appear only in a group whose rec is "No action / keep in place" (id `protected`), never in a move/delete group
- `Desktop/Bitsum Process Lasso Pro v14.0.0.40 Multilingual Portable [FTUApps]` — holds the LIVE Process Lasso config the running engine reads (registry ConfigFolderEx points here). Moving it breaks Lasso.
- `Documents/chetaz` — the open Obsidian vault.
- `Downloads/downloads-desktop-cleanup.livingdoc` — this document itself.
- every `desktop.ini`; anything named `.claude`, `.config`, `.ssh`, `.gnupg`, `.wslconfig`, `.gitconfig`, `.local`, `.cache`, `AppData`, `NTUSER*` in the home root; the home-root folders `code`, `code2`, `cheta`, `.cuddle*`.
- `C:\performance-diagnostics` and `C:\0.defenderexclusions` / `D:\0.defenderexclusions` (IGNORE the latter two entirely — do not list them at all).
- `D:\SPECTRE-16-UGLYBETTY.tibx` (yesterday's full Acronis backup) and `D:\Recovery`.

## What to produce
1. **Diff vs July**: for Downloads and Desktop, which July file entries no longer exist (resolved), which still exist, and which items are NEW since 2026-07-13 (use mtime/newest). 
2. **A v3 DATA object** using the identical schema, covering ALL of: Downloads, Desktop, Documents, Pictures, Videos, Music, home root, C:\ root (non-system items only), D:\ root, and temp dirs. Rules:
   - Keep the three July sections ("Reclaim space & kill cruft", "Consolidate the heavy stuff", "Organize the survivors, by project") and add a fourth section "Protected — do not touch" (group id `protected`, rec label "Keep in place", alt label "Keep in place").
   - Keep every July group id that still has live files (refresh its `files` to current names and sizes; drop entries that no longer exist from `files` but list them in a new group `resolved-since-july` whose rec is "Already gone — nothing to do"). Never invent files: every name you emit must appear in the inventories.
   - Add new groups as needed, e.g. `exact-dupes` (from dupes.csv: list the `dup` copies with "identical to <kept path>"), `old-versions`, `installers` (installers for apps already installed — check names like *.exe/*.msi/*.msix/*.appx/*.vsix/*.AppImage/*.deb), `disk-images` (*.iso, *.img, *.img.xz, *.wim, *.vhd(x) outside AppData), `ai-models` (*.gguf, *.safetensors, *.onnx, *.bin model weights), `archives-extracted` (zip whose extracted folder sits beside it), `temp-stale` (temp items unlocked and older than 7 days; NEVER include locked items or anything touched in the last 24h; `wsl-crashes` goes to a separate group `crash-evidence` with rec "Keep until WSL crash triage is done"), `screenshots` (Pictures/Screenshots etc. — organize by year-month, do not delete), per-project groups (`proj-*`) for Documents and Desktop work folders.
   - Give each group a precise `fn` (what is in it, total size in GB/MB, why) and realistic `rec`/`alt`. Destination folder names go in `folders` (one entry per location+folder). Prefer project/function folders over extension buckets (that was the July design principle).
   - `security` group: re-detect credential files, key/serial/password text files, credential-harvesting tools, MDM-bypass material, cracked-software keymakers/activators (e.g. `*Keymaker*`, `*Activator*`, `*crack*`, `*keygen*`) — these are a malware risk. Names only; do NOT open or print the contents of any credential-looking file.
3. `meta`: `{documentId:"downloads-desktop-cleanup", version:"3.0.0", formatVersion:"1.2.x", title:"Downloads, Desktop & User Folders Cleanup", generated:"{{DATE}}", author:"Aaron Miller", model:"opencode-go/muse-spark-1.3-contributor (W2) + claude-opus-5-5 review"}`. Update `sectionIntros` text to reflect v3 scope with current totals.

## Output (exactly two files)
- `/mnt/c/performance-diagnostics/{{CHECKUP}}/workers/W2-livingdoc-v3-DATA.json` — the v3 DATA object, valid JSON (validate with `python3 -m json.tool`).
- `/mnt/c/performance-diagnostics/{{CHECKUP}}/workers/W2-folder-organize.md` — sections: `## Summary` (counts + GB per location, top 10 wins), `## Diff vs July` (resolved / still present / new, with counts), `## Per-location findings` (Downloads, Desktop, Documents, Pictures, Videos, Music, Home root, C:\ root, D:\ root, Temp), `## Proposed folder structure` (tree), `## Uncertain items` (anything you could not classify confidently — list them; do not guess), `## Validation` (state you checked every emitted name exists in the inventories, how).
