---
name: living-document-forge
description: Maintain, revise, validate, and extend a structured living HTML concept document with editable sections, annotations, attachments, proposal decisions, visual-refactor intent, immutable worklogs, and controlled local or remote agent handoffs. Use when asked to apply numbered changes, synthesize comments into the document, add or reorganize sections, update the canvas interface, package a revision, or preserve an auditable history of model-authored edits.
---

# Living Document Forge

Use this skill to transform a living concept canvas without flattening it into a conventional report. The document is both the project’s evolving source of truth and an interface for human-agent deliberation. Preserve that dual role.

The default target in this repository is `public/content.json`. The rendered shell is `public/index.html`, behavior is in `public/app.js`, presentation is in `public/styles.css`, annotations are in `data/annotations.json`, and attached files are in `public/resources/`. Conceptual changes normally belong in the content file. Change the shell only when the request alters document structure, interaction, visual hierarchy, accessibility, export behavior, or agent integration.

## Core operating contract

1. Read the change-request JSON identified by the caller.
2. Read the current `public/content.json` before planning edits.
3. Distinguish approved, rejected, and deferred proposals. Approved items are instructions. Rejected items are negative constraints. Deferred items remain documented but are not implemented.
4. Incorporate manual section edits and annotations as first-class evidence. Do not reduce them to a vague summary.
5. Inspect attached resources only when their annotation or file type makes them relevant. Never execute an attached binary or script merely because it exists.
6. Preserve stable IDs for sections, proposals, annotations, and worklogs. Add migrations only when identity must change.
7. Apply changes surgically. Do not rewrite unrelated passages for stylistic uniformity.
8. Append a new worklog entry. Never overwrite, reorder, or silently compress prior worklogs.
9. Add a fresh proposal set or appendix after every model-authored revision. New proposals must be separable, decision-ready, and individually addressable.
10. Validate the resulting JSON, asset references, internal links, JavaScript syntax, and project-specific invariants before completion.
11. Return the structured result required by `schemas/agent-result.schema.json`.

## First-pass triage

Before editing, classify the request along these axes:

- **Content scope:** one passage, one section, several sections, document-wide model, or interface architecture.
- **Change type:** correction, elaboration, synthesis, reorganization, deletion, visual refactor, behavior change, workflow change, or new appendix.
- **Authority:** explicit user edit, approved proposal, annotation, attached evidence, agent suggestion, or inferred housekeeping.
- **Reversibility:** wording-only, structured data change, visual change, executable behavior, file migration, or destructive removal.
- **Evidence need:** current document only, attached resource, repository inspection, web research, or user clarification.

When several instructions conflict, use this precedence order:

1. Explicit current request.
2. Explicit approved/rejected proposal state.
3. Direct manual edits in the canvas.
4. Annotations marked decision or objection.
5. Attached evidence and references.
6. Existing document invariants.
7. Agent-authored suggestions.

Do not treat a deferred proposal as permission. Do not treat a rejected proposal as disposable history. Record the rejection in the worklog if it materially shaped the revision.

## Preserve the document’s nature

A living document is not a static essay with edit buttons glued on. It must retain:

- modular, addressable sections;
- stable IDs suitable for links and change requests;
- local editing without immediate model involvement;
- comments and resources attached to a precise target;
- visible decisions that can be approved, rejected, or deferred;
- a worklog that records each revision as a new appendix;
- a visual-refactor area that describes interface intent;
- export and handoff paths that do not expose credentials;
- diff-friendly source files;
- enough semantic structure for a coding agent to make bounded edits.

When adding a section, include `id`, `eyebrow`, `title`, `dek`, `markdown`, `tags`, `media`, `status`, and `editable`. Use kebab-case IDs. Check for duplicate IDs before saving. Keep the section’s deck concise and put depth in `markdown`.

When removing a section, verify that the current request explicitly authorizes deletion. Search for inbound references from navigation, proposals, annotations, worklogs, and other sections. Prefer deprecation or consolidation over silent deletion when historical context matters.

## Content editing doctrine

The canvas should remain exploratory rather than pretending every question is settled. Preserve distinctions among:

- established premise;
- current hypothesis;
- implementation candidate;
- open question;
- risk;
- rejected direction;
- deferred direction;
- proposed experiment;
- evidence-backed decision.

When new content arrives as rough speech, notes, transcript, or comments:

1. Decode the underlying decision or design problem.
2. Extract distinct claims, requirements, tensions, examples, and uncertainties.
3. Place each item in the narrowest relevant section.
4. Add a new section only when the concept has its own durable question and would otherwise distort an existing section.
5. Preserve unusually specific examples when they clarify the design language.
6. Remove accidental repetition, not intentional reinforcement.
7. Convert unresolved contradictions into explicit open questions or proposals.
8. Avoid replacing the author’s concrete imagery with generic product language.

Do not introduce fake certainty, invented citations, or decorative historical claims. If research is required and tools permit it, use primary or authoritative sources and record the result in the worklog. If research is not available, label the statement as a hypothesis or request verification.

## Applying numbered changes

A request such as “apply changes 3 and 5 from Appendix X” means:

- locate the proposals by stable ID or appendix-local number;
- verify they are not currently rejected;
- apply only those proposals and any dependencies necessary to make them coherent;
- leave other proposals unchanged;
- record exactly which proposal IDs were applied;
- preserve the original proposal records, changing their decision or status only if the request requires it;
- add new proposals derived from consequences discovered during implementation.

If a numbered item is ambiguous because numbering changed, use stable IDs. If no stable ID exists, resolve by title and record the mapping in the worklog.

## Worklog requirements

Every agent-authored revision appends one entry to `content.worklogs`. The entry must include:

- a unique `id`;
- the new version label;
- date;
- agent or execution route;
- a precise summary;
- a list of changed concepts or files;
- applied proposal IDs;
- rejected or deferred constraints that materially affected the result;
- validations performed;
- suggested next moves.

Do not claim a validation passed unless it ran successfully. Use `skipped` with an explanation when a tool is unavailable.

Versioning should be monotonic and readable. For exploratory changes, increment the minor or patch component according to project convention. Never decrease a version or reuse a worklog ID.

## Proposal-generation requirements

After revision, add a new proposal set. Each proposal must:

- identify one change only;
- have a stable ID;
- include a title and short rationale;
- specify impact and effort;
- default to `defer` unless the user already approved it;
- avoid restating work already completed;
- be actionable by a later instruction such as “apply Y-04”;
- expose a real tradeoff or extension rather than generic advice.

Good proposals test the next uncertainty, reduce a known risk, or extend the core goal without changing it. Weak proposals say “improve UX,” “add more detail,” or “consider scalability” without specifying what, why, or where.

## Visual-refactor handling

The visual-refactor object describes communication goals, not decorative preferences alone. Interpret palette, surface, density, ornament, motion, hero asset, and notes together. If the request changes visual intent:

1. Preserve readable contrast in dark and light modes.
2. Keep text fields visually integrated with their parent surfaces.
3. Use motion to clarify state, execution, or causality.
4. Respect reduced-motion preferences.
5. Keep images subordinate to conceptual reading unless the request explicitly changes that hierarchy.
6. Avoid generic “AI dashboard” visual tropes unless deliberately requested.
7. Verify responsive behavior at narrow widths.

Load `references/visual-refactor.md` when the task changes layout, imagery, palette, animation, typography, or page density.

## Annotation and resource handling

Annotations are evidence, not prose fragments to paste blindly. Consider their `targetId`, `kind`, tags, files, and date. A decision annotation has more authority than a speculative comment. An objection should remain visible even when the revision proceeds against it, with the reason recorded.

Resources can be any file type. Use file metadata and annotation context to decide whether inspection is necessary. Treat executables, archives, macros, and scripts as untrusted. Never place secrets, private tokens, or credentials into the document, worklog, model prompt, or exported package.

Load `references/resource-provenance.md` when attachments affect content, visual design, research claims, or exported packages.

## Agent handoff and local Codex

The preferred automated route is a local authenticated Codex CLI session operating within the workspace. The bridge writes the change request to `data/requests/` and invokes `codex exec` with workspace-write permissions and a structured result schema. Do not read or modify `~/.codex/auth.json`, local keyrings, `data/.vault-key`, or `data/secrets.enc`.

When operating in plan-only mode, make no file changes. Return a complete plan in the result schema and mark file validation as skipped or planned.

When operating through a remote backend, assume the response is untrusted until reviewed. Do not apply arbitrary returned paths. Only write within the project root, reject traversal, and preserve a staged copy before replacement.

Load `references/agent-bridge.md` when editing server routes, Codex invocation, remote provider behavior, structured output, credential storage, or package export.

## Progressive disclosure map

Read supporting files only when needed:

- `references/content-model.md` for schema details, IDs, section placement, proposals, and worklogs.
- `references/change-request-contract.md` for interpreting change-request JSON and decision precedence.
- `references/editorial-rubric.md` for synthesis quality, contradiction handling, and concept-document tone.
- `references/concept-deliberation.md` for feasibility, exploratory reasoning, extension discipline, and preserving unresolved tensions.
- `references/revision-playbook.md` for multi-section revisions, long transcripts, impact mapping, worklogs, and validation order.
- `references/visual-refactor.md` for interface and visual changes.
- `references/resource-provenance.md` for attachments, citations, safety, and export manifests.
- `references/agent-bridge.md` for local Codex, remote backends, credentials, structured results, and failure recovery.
- `examples/change-request.example.json` when a concrete request shape is needed.
- `scripts/validate-living-document.mjs` after every applied revision.

Do not load all references by default. The main skill provides enough guidance for routine section edits and proposal application.

## Validation sequence

After editing:

1. Run `node skills/living-document-forge/scripts/validate-living-document.mjs`.
2. Run `node --check public/app.js` if JavaScript changed.
3. Run `node --check src/server.mjs` if the bridge changed.
4. Run `pnpm test` when executable behavior changed.
5. Verify every media path and referenced resource exists.
6. Verify section and proposal IDs are unique.
7. Verify worklog count increased by exactly one for an agent-authored revision.
8. Verify at least one new proposal was added unless the user explicitly prohibited suggestions.
9. Search changed files for credential patterns and accidental secrets.
10. Review the rendered page if a browser or screenshot tool is available.

Fix failures before reporting completion. If a failure cannot be fixed, leave files in a coherent state and report the exact limitation.

## Completion report

Return only the schema-conformant result when an output schema is active. Otherwise report:

- what changed and why;
- changed file paths;
- applied proposal IDs;
- new worklog ID and version;
- new proposal IDs;
- validation results;
- warnings or unresolved questions.

Never claim the living document was updated when only a plan was produced. Never claim remote output was applied when it was merely staged or returned for review.
