# Challenge review - {{CHUNK}} ({{ROOT}})
<!-- review-brief v2. Run by a DIFFERENT model than the worker (Claude agents). Read-only except for the one output file. -->

A worker model decided, for every item in this chunk, why it is here and what to do with it. Find the decisions that are wrong, prove it, and correct them. Be a skeptic: a removal survives only if you confirm its evidence yourself. Do not move, rename or delete anything; write only the output file. Stay strictly read-only: use `git --no-optional-locks` for any git command (plain `git status` rewrites index timestamps), and do not open files you only need to hash in an app that might write to them.

Inputs
- Facts for every item: `{{WORKDIR}}/org-items.json` (look items up by id; the chunk's ids are in `{{WORKDIR}}/{{CHUNKFILE}}`). Hints worth reading: `app_owned`, `referenced_by` (a config, startup entry or scheduled task mentions this path), `live_hint`, `duplicate_of`, `version_family`, `installer`, `temp_hint`.
- Worker decisions: `{{WORKDIR}}/decisions-{{CHUNK}}.json`.
- Owner rules: `{{SKILL}}/references/steering.md`; owner profile: `{{SKILL}}/references/user-profile.md`; taxonomy: `{{SKILL}}/references/taxonomy.md`; past mistakes: `{{SKILL}}/references/retrospective.md`.
- Installed programs: `{{INSTALLED_PROGRAMS}}`, `{{INSTALLED_APPX}}`.
- Items in this chunk that have NO decision yet: {{MISSING}}

Check, in this order
1. Every removal. `remove-duplicate`: the original exists and is identical (compare size and hash yourself). `remove-superseded`: the newer version exists here or is installed, and it is the same product line (not another edition, architecture or platform). `remove-temp`: the item has no lasting content (open it). If you cannot confirm, change it to `keep-organize` (or `unsure` if intent is also unclear).
2. Every move of a folder or dot-file. Would it break an app, tool, agent, sync job or shortcut? Dot-folders, `node_modules`, app-owned folders (FL Studio `Image-Line`, VMware `Virtual Machines`, `WindowsPowerShell`/`PowerShell` profiles, Zoom, PowerToys, MAXON/Cinebench, Ableton, Tracktion, Arduino...), anything with `referenced_by`, git repos with recent commits, and folders an agent or tool writes to go to `leave-in-place` with dest `.`.
3. Installers. `Installed` vs `Ready to install` vs `Other systems`: check the installed list and the file's platform and architecture yourself.
4. Intent. Is the stated intent plausible from content and dates? A confident invented intent is worse than `unsure`. For `unsure` items, try once to recover intent: neighbouring downloads by date, and the owner's agent history (`wsl.exe -d Ubuntu -e bash -lc "cass search '<file name>' --robot --limit 5"` if it answers quickly).
5. Placement.
   - The root already names a type: inside Pictures, Music or Videos never nest `Media/...`; albums stay as album folders at the Music root (dest `.`), photos stay in Pictures grouped by topic or project.
   - A folder item goes INTO its category. A dest that repeats the folder's own name or a near-synonym under a category (`Archives & backups/Apple Notes HTML export` for the folder `Notes Export-HTML`) only wraps it in another folder: use the category itself.
   - No single-item subfolders except projects; at most two levels below the top folder; project names `YYYY-MM Topic words` (spaces, no hyphens between words); members of one effort share one project name.
   - An item that is already where its dest would put it gets dest `.` and `leave-in-place`.
6. Missing items: decide each one listed above, with a full record.

Output: write `{{WORKDIR}}/review-{{CHUNK}}.json`:
```json
{"chunk": "{{CHUNK}}", "checked": 0, "corrections": [
  {"id": "O-...", "decision": "keep-organize", "dest": "Installers/Installed", "intent": "(only if changed or missing)",
   "want": "(only if changed or missing)", "confidence": "high", "evidence": "what you verified", "why": "what was wrong (<=20 words)"}],
 "notes": ["patterns the worker got wrong, phrased as a rule for the next worker brief"]}
```
List only items you changed (plus missing items). Omitted fields keep the worker's value. `checked` = how many items you examined closely.
