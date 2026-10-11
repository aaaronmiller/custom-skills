# Constitution source (user-canonical)

Location: `/home/cheta/code/quartermaster/.specify/memory/constitution.md`
(v1.0.0, ratified 2026-06-26). This pointer IS the location. Do not duplicate
the file into skills or build roots — duplicates drift and a drifted
constitution enforces the wrong law.

## How to use (Phase 4 step 7)

- Reference by name the principles the new build inherits. Typical carryover:
  preview-before-write with rollback, provenance on every artifact,
  deterministic procedures with advisory model judgment.
- Never transplant another project's Technical Constraints. A stack bound to
  one build (language, storage, CLI surface) is a defect in any other.
- If no applicable constitution exists, do not generate one. Note the absence
  and route creation through the project's governance tooling.
- If the build root lacks a session-scoped instruction file (`AGENTS.md` /
  `CLAUDE.md` / `AGENT.md`), write the standing gates there.

## Enforcement (why restart matters)

- Instruction files load by directory scope at session start. A session rooted
  elsewhere never sees the build root's file — the gates exist on disk and
  bind nothing.
- After writing gates, tell the user to restart rooted in the build folder.
  Until then the gates have no bite. A restart without the file changes
  nothing; the file without a restart changes nothing.
