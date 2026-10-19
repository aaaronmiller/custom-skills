# Destination taxonomy and naming rules

Destinations are relative to the item's root folder (Downloads, Desktop, Documents, a dump folder...). `~/Pictures/...`, `~/Music/...`, `~/Videos/...`, `~/Documents/...` move an item to another user folder when it obviously belongs there.

| Top level | Holds | Subfolders |
|---|---|---|
| `Installers` | software packages | `Installed` (installed on this PC), `Ready to install` (for this PC, not installed or newer than installed), `Other systems` → `Linux`, `macOS`, `Android`, `iOS`, `Devices & firmware`, `ARM`, `Other PCs` |
| `Projects` | files that belong to one effort | `YYYY-MM Topic` (month the effort started, from download dates) |
| `Documents` | standalone documents | `Research & reports`, `Guides & manuals`, `Personal & admin`, `Writing` |
| `Notes & prompts` | markdown/text notes, prompts, specs, chat exports | optional topic subfolder |
| `Scripts & configs` | standalone scripts and configs | optional tool subfolder |
| `Software & source` | source trees, repos, extensions, skill packs, portable tools | optional |
| `AI models` | weights | — |
| `Disk images` | ISO/IMG/VHD/archives of OS images | — |
| `Media` | `Images`, `Screenshots`, `Audio`, `Video` | — |
| `Archives & backups` | exports, takeouts, backups, migrations | optional |
| `_Unsure` | items whose intent could not be worked out | — |
| `_REVIEW-then-delete` | superseded / duplicate / temp (staged, never deleted) | — |

## Naming and granularity
- At most two levels below the top-level folder; `Projects/<name>` may have one more level when the project genuinely has parts.
- No single-item subfolder unless it is a project. A lone file goes in the parent category.
- Project names: `YYYY-MM Topic words` with plain spaces, Title-ish case, no hyphens between words, no dates beyond the month (e.g. `2026-08 ARDF model ranking`).
- Reuse an existing project name exactly when an item belongs to it.
- Keep owner vocabulary when it carries meaning (e.g. `Mac migration`, `eBay selling`), drop crude words from new folder names only if a neutral word says the same thing.
- The home folder root is not a storage location: never create category folders there; loose home-root items go under `~/Documents/<category>`.
- Inside type-named roots (Pictures, Music, Videos) use topic folders directly - no `Projects`, `Media` or `Archives` level. Album folders stay at the Music root.
- At the Documents root, categories sit directly (`Guides & manuals`, `Research & reports`, `Personal & admin`), never `Documents/Documents/...`.
- A folder item goes INTO a category and keeps its name; never wrap it in a folder named like itself.
