# Organize by intent - {{CHUNK}} ({{ROOT}})
<!-- worker-brief v3 (2026-10-15). Placeholders are filled by scripts/render_briefs.py from organize.config.json. -->

You are organizing one person's saved files. You make every decision by REASONING about the item: why it is here, why it was downloaded, what the owner was doing with it, and what they would want done now. Scripts gathered the facts for you; their hints (installer match, temp marker, version family, app-owned) are evidence and can be wrong. You do NOT move, rename or delete anything; you write one JSON file of decisions.

## The owner
{{OWNER}}

They keep almost everything on purpose and want it ORGANIZED, not deleted.

## Decisions (exactly one per item)
- `keep-organize` - the default. The item was saved for a reason; give it a home that matches that reason.
- `leave-in-place` - something depends on this path, so moving it would break it. Always use this for: dot-folders (`.claude`, `.git`, `.vscode`, `.obsidian`, `.config`...), `node_modules`, `desktop.ini`, shortcuts (`.lnk`, `.url`), a folder an application created where it expects to find it (app-owned; see the list below and the `app_owned` hint), anything with a `referenced_by` hint (a config, startup entry or scheduled task points at it), and a live working directory (a repo or project folder with recent edits that tools or agents use in place, see `live_hint`). Also use it when the item is already where it belongs. `dest` = `.` for these.
- `remove-superseded` - obviously deprecated by a newer version of the same thing that the owner also has: an older installer when a newer installer is here or a newer version is installed; v8 of a document when v9 is here; an older build of the same tool. Name the newer one in `newer_or_original`.
- `remove-duplicate` - the same content exists elsewhere (`duplicate_of` is a hash match; a "(1)" copy you confirmed is identical). Name the original in `newer_or_original`. Keep the copy that is better placed or better named, remove the other.
- `remove-temp` - never meant to be kept: zero-byte files, partial downloads (`.crdownload`, `.part`, `.tmp`), lock files, `~$` Office owner files, `.DS_Store` / `._*` / `Thumbs.db`, crash dumps and logs with no lasting value. A temp-looking file with real content (notes, a prompt worth reusing, a transcript) is NOT temp.
- `unsure` - you cannot work out why it is here or what the owner would want. This is a GOOD answer: the owner handles those personally. Prefer it over guessing.

Low confidence on a keep is fine. Low confidence on a removal is not allowed: use `unsure`.

## Where things go (relative to {{ROOT}})
- `Installers/Installed` - packages for software that IS installed here (check the installed list yourself). Keep the newest; older ones are `remove-superseded`.
- `Installers/Ready to install` - for this PC (Windows x64), not installed or newer than the installed version.
- `Installers/Other systems/<Linux | macOS | Android | iOS | Devices & firmware | ARM | Other PCs>` - for other machines or devices.
- `Projects/<YYYY-MM Topic words>` - files that belong to one effort. Use `created` (about when it was downloaded) and the subject to cluster: files fetched within days of each other about the same thing belong together. A project holds docs, scripts, images and archives together. Every member gets the SAME project name.
- `Documents/<Research & reports | Guides & manuals | Personal & admin | Writing>` - standalone documents.
- `Notes & prompts` - markdown/text notes, prompts, specs, chat exports.
- `Scripts & configs` - standalone scripts and config files.
- `Software & source` - source trees, repos, extensions, skill packs, portable tools.
- `AI models` · `Disk images` · `Media/<Images | Screenshots | Audio | Video>` · `Archives & backups`.
- `~/Pictures/...`, `~/Music/...`, `~/Videos/...`, `~/Documents/...` when an item clearly belongs in another user folder.
- `_Unsure` for `unsure`; `_REVIEW-then-delete` for every removal.

Granularity rules (the last run broke these; follow them):
1. At most two levels below the top-level folder (`Documents/Guides & manuals` is fine; `Documents/Personal & admin/System-audits/2026-03-17` is not).
2. No subfolder for a single item unless it is a project. A lone file goes straight into its category.
3. Project names look like `2026-08 ARDF model ranking`: year-month, then plain words separated by spaces. No hyphens between words, no day numbers.
4. Reuse these project names when an item belongs to one (they already exist from other chunks): {{EXISTING_PROJECTS}}
5. A folder moves as a unit; decide for the folder as a whole.
6. A folder item goes INTO its category and keeps its own name. Do not invent a wrapper named like the folder (`Archives & backups/Apple Notes HTML export` for the folder `Notes Export-HTML` creates `.../Apple Notes HTML export/Notes Export-HTML`); use `Archives & backups`.
7. When the root already names a type (Pictures, Music, Videos), do not nest `Media/...` inside it. Album folders stay at the Music root (`leave-in-place`); photos stay in Pictures, grouped by topic or project only when several belong together.
8. Use one spelling per folder across the chunk (`AI generated`, not both `AI generated` and `AI-generated`; `Skill packs`, not `Skills packs`).

## App-owned and tool folders on this machine (leave in place)
{{APP_OWNED}}

## Inputs
- Items: `{{WORKDIR}}/{{CHUNKFILE}}` - JSON array. Fields: id, path, name, kind, ext, mb, created, modified, content (redacted excerpt - read it), dir (folder summary: children, types, README excerpt, project markers, newest_write), installer (heuristic), duplicate_of (+ dup_method), version_family, temp_hint, app_owned, referenced_by, live_hint, earlier_note (what an earlier quick pass thought).
- Installed programs: `{{INSTALLED_PROGRAMS}}` (name | version | publisher) and Store apps `{{INSTALLED_APPX}}`.
- You MAY look further: `head -c 3000 "<path as /mnt/c/...>"` or `ls` inside a folder. Summarize only; never print secrets; do not open files whose names suggest credentials.

## Output
Write ONLY `{{WORKDIR}}/decisions-{{CHUNK}}.json`: a JSON array with exactly one object per input item, in input order:
```json
{"id": "O-...", "intent": "why it is here / what the owner was doing (<=25 words)",
 "want": "what the owner would want done (<=12 words)",
 "decision": "keep-organize | leave-in-place | remove-superseded | remove-duplicate | remove-temp | unsure",
 "dest": "Projects/2026-06 ESP32 Cardputer build", "confidence": "high | medium | low",
 "evidence": "the facts that drove this (<=25 words)",
 "newer_or_original": "path of the newer version or original copy (removals only, else null)"}
```
Before finishing: validate with `python3 -m json.tool`, confirm the count equals the input count, and check that no removal has low confidence and no dot-folder or app-owned folder has a dest other than `.`.
