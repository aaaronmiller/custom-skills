---
title: Monthly cadence
version: "1.0"
tags: [notes-sweeper, cadence, automation]
---

# Monthly cadence

Run the sweep monthly or when tabs pile up (~50+ open). Delta-only after the first run: keep prior snapshot hashes; only new/changed TabState bins and backup files need parsing. Prior run: `~/Documents/notepad-recovery/<timestamp>Z/`.

Compare new extraction against the previous `recovery-catalog/catalog.json` by content hash — exact duplicates share the canonical copy, every occurrence stays in the manifest. Review the previous HUMAN-REVIEW queue first; many items resolve once their project ships.
