---
title: Onboarding playbook
version: "1.0"
tags: [assignment-librarian, onboarding, intake, manifest]
---

# Onboarding playbook: ideation drop to staged packet

This reference covers Operation 2 of `SKILL.md`: turning a raw folder of
ideation output (usually pasted LLM conversation exports) into a staged packet
spec-prep can consume. Do not modify project sources or extract archives; if the
drop is a lone zip, record it as a source and flag extraction as an explicit
future intake-staging step.

## 1. Survey the drop

List every file (including `sources/`, `archives/`, `reading/` subdirs).
Skim each for: problem statement, proposed solution, personas/users, success
and failure conditions, constraints, scale/quality expectations, implied
entities, integrations, rejected alternatives, provenance (which conversation,
which model, what date). Tag every extracted signal as **intent** (goals,
constraints, users), **spec** (testable requirements), or **implementation**
(stack picks, file layouts) — the author fused them; separation starts here.

## 2. Draft project-intake.json

Normative shape: `<root>/.catalog/project-intake.schema.json`. Required keys:

| Key | Rule |
|---|---|
| `schemaVersion` | `1` |
| `projectId` | kebab-case, usually the folder name normalized |
| `title` | one line, human-readable |
| `summary` | one paragraph: what it is, what state it is in, what blocks it |
| `lifecycle` | `staged` for every newly onboarded packet |
| `assignment` | `unassigned`, `assigned`, or `tooling` (skill/format/tooling packets are `tooling`) |
| `kind` | `project`, `maintenance`, or `tooling` |
| `nextOperation` | free text, e.g. `specification-preparation` or `intake-review` |
| `readOrder` | >= 1 relative path, each must resolve to a real file; start with `start-here.md` |
| `sources` | array of `{path, format, role, sha256}`; roles: `ideation-source`, `reference`, `archive`, `reading-copy` |
| `issues` | array of `{severity, detail}`; severity in `info`, `conversion`, `missing-input` |
| `relatedProjects` | array of projectId strings (empty array, never null) |
| `externalResources` | array of `{path, role, handling}` (empty array if none) |

Optional keys worth setting: `brief` (bounded project brief, 1–3 paragraphs —
its absence plus a `missing-input` issue is what holds a packet at
`needs-intake`), `details`, `ldRelation` (`direct`/`indirect`/`none`),
`fileNotes` (one line per important file), `theme` (one of the six SKILL.md
slugs; omit when unsure — the index falls back to keyword guessing and gray).

Compute every source hash yourself, never copy one:

```bash
sha256sum "<folder>"/*
python3 <root>/.catalog/intake-validator.py "<folder>"
```

The validator is the acceptance gate: it rejects bad `schemaVersion`,
non-kebab `projectId`, empty title/summary/nextOperation, bad lifecycle or
assignment, non-array collections, duplicate or missing source paths, path
traversal (`..`, absolute paths, symlinks), sha256 mismatches, empty
`readOrder`, dead read-order paths, and malformed issues/externalResources.
Fix the manifest, not the validator.

## 3. Record gaps honestly

Typical `issues` entries:

- `missing-input`: "No bounded product brief — reference research only."
- `missing-input`: "Held-out evaluation payload referenced but absent."
- `conversion`: "Skill pack, not product requirements; preparation consumes it as tooling input."
- `conversion`: "Archive `x.zip` unextracted; extraction is an explicit future staging step."
- `info`: "Assigned status preserved from source; not a readiness claim."

A packet with any `missing-input` issue triages as `needs-intake`. That is a
correct terminal state for research-only or empty drops (e.g. an empty
container awaiting its brief), not a failure to fix by inventing scope.

## 4. Write start-here.md

```markdown
---
title: "<Title> intake"
type: intake-handoff
version: "1.0.0"
---

# <Title>

State: staged intake. Assignment: <assignment>. spec-prep operation: <nextOperation>.

Read `project-intake.json`, then the following source files in order:

1. `<first source>`
...

## Format and readiness findings

- <one line per finding>

## Future handoff

Use the installed spec-prep skill and its lifecycle terminology. ...
```

Leave `workbench.json` alone unless the packet needs non-default pointers —
spec-prep auto mode generates it during preparation.

## 5. Common failures

- sha256 copied from an older manifest instead of recomputed after edits.
- `readOrder` naming a file that lives in `sources/` without the prefix.
- Absolute paths or `..` in source paths (rejected; keep everything relative).
- One manifest covering two projects: split the folder, one manifest each.
- Declaring `ready-for-spec-prep` in prose while `issues` still carry
  `missing-input` — the triage rule reads the manifest, not the prose.
