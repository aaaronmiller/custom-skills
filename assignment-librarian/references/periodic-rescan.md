---
title: Periodic rescan workflow
version: "1.0"
tags: [assignment-librarian, rescan, index, automation]
---

# Periodic rescan workflow

New ideation folders appear at any time. This loop keeps the index current
without re-authoring staged work. Run it on a schedule, on session start when
the library may have changed, or whenever asked to "rescan" / "update the
index".

## Procedure

1. **Scan.** `python3 scripts/scan.py <root> --out /tmp/readiness.json`
   (read-only; never writes into the library). The report is the triage queue.
2. **Onboard.** Every `readiness: unstaged` folder gets Operation 2
   (`onboarding-playbook.md`). Folders that are holding areas, empty
   containers, or non-specable loose items still get a manifest — with
   `missing-input` issues and the `staging` theme — so the index shows them
   honestly instead of hiding them.
3. **Re-triage.** For folders whose files changed since the last scan
   (hash mismatches, new files, moved paths): re-run the validator, update
   `issues`/`fileNotes`, confirm the status rule still holds. Never rewrite a
   valid manifest's prose to chase a status.
4. **Rebuild the index.** `python3 <root>/.catalog/catalog.py check`, then
   `python3 <root>/.catalog/catalog.py build`. Confirm the new cards, colors,
   dates and pills appear in the regenerated projections.
5. **Report drift only.** Findings go to the agent result (or the scheduled-run
   log), not into library files: new folders found, statuses changed, hashes
   mismatched, packets newly `ready-for-spec-prep`.

## Index legend (what the page shows)

- **Card background** = theme (six colors in `SKILL.md`; `staging` gray means
  not yet classified — onboard it).
- **Pill** = readiness (`unstaged` / `needs-intake` / `ready-for-spec-prep` /
  `has-specs`). A folder without a manifest always renders `unstaged`, with a
  color indicating the missing manifest — it is listed, never hidden.
- **Date line** = `stagedDate`: manifest `stagedAt` when present, otherwise
  the folder's filesystem mtime. Oldest-`unstaged` ordering surfaces stale
  drops for triage.
- **Analytics section** = counts by theme, counts by status, oldest-unstaged
  list, largest-folders list — all derivable from one `scan.py` report.

## Theme keyword fallback (guess only)

Used by `scripts/scan.py` when a folder has no manifest `theme`, and by the
index for `unstaged` cards. Never written into manifests by automation; the
onboarding agent sets the real theme. Match on lowercased folder-name tokens:

- `agentic-systems`: agent, agentic, orchestrator, flywheel, routing, quota,
  prompt, model, stack, unified, driver, hunt, operator, phase, deal, desktop
- `dev-tooling`: repo, cleanup, wsl, atlas, spec-prep, tooling, dev, reclaim, t3,
  code
- `security-research`: adversarial, dossier, greynoise, swarm, web, hack,
  hacking, threat, security, research
- `hardware-platforms`: pi, siri, remote, laptop, hardware, windows, input,
  chrome, tab, extension, switchboard, servicing
- `creative-products`: game, wars, foundry, smile, smiledraft, draft,
  creative, product

Highest keyword-hit count wins; ties break toward `creative-products`, then
`security-research`, `hardware-platforms`, `dev-tooling`, `agentic-systems`.
Zero hits → `staging`. Known limitation: names like `stack-wars` score on both
sides and resolve by the tie-break — the onboarding agent confirms or corrects
it when writing the manifest.
