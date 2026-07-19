# Large revision playbook

Use this reference when applying several approved proposals, integrating a long transcript, revising more than three sections, or changing both content and interface behavior.

## Before editing

1. Read `public/content.json` completely enough to understand section boundaries and recurring terms.
2. Read the latest worklog and all proposal states.
3. Read annotations targeted to affected sections and the whole document.
4. Inventory attached resources by type, target, and stated purpose.
5. Build an impact map: direct sections, dependent sections, interface files, schemas, tests, and documentation.
6. Identify invariants and explicit refusals.
7. Decide whether the revision is conceptual, structural, visual, behavioral, or mixed.

Do not start rewriting while still discovering instructions. Consolidate authority first.

## Revision plan

For each requested change, record:

- source authority;
- target sections and files;
- content to preserve;
- content to add, replace, or deprecate;
- dependencies;
- validation needed;
- worklog language;
- possible follow-on proposals.

When several changes overlap, merge implementation work but keep their identities in the worklog.

## Surgical depth

“Surgical” does not mean shallow. It means change every place required for coherence and no place merely for stylistic tidiness. A new Artifact IR concept may require updates to technical architecture, mechanisms, media adapters, councils, exports, schemas, and skills. Make those linked changes. Do not rewrite the player-fantasy section just because its prose differs.

## User voice

Preserve the author’s unusual comparisons, physical examples, and ambitions. Correct grammar and organization without sterilizing the idea. When a rough statement has several interpretations, retain the strongest plausible reading and place uncertainty in an annotation, proposal, or open question.

Avoid replacing concrete language with consultant language. Prefer “the shutters close while an expensive render runs” to “provide stateful execution feedback.” Both can appear, but the first communicates the experience.

## Worklog construction

The worklog should be useful to a future agent. Include:

- exact version transition;
- proposal IDs and direct instructions applied;
- sections added, removed, split, or merged;
- interface or schema changes;
- resources incorporated;
- research performed;
- validations run with results;
- unresolved warnings;
- suggested next experiments.

Do not write “improved content” or “updated UI.” Name the change.

## New proposal generation

After implementing the current decisions, inspect consequences. New proposals should target newly exposed uncertainties, not recreate the completed work.

Examples:

- after adding autonomous workshops, propose a fixed-budget overnight trust test;
- after defining Artifact IR, propose one complete exported lineage fixture;
- after adding critic personas, propose a human-versus-council comparison;
- after adding manual section creation, propose safe reordering and deprecation semantics.

Default new proposals to defer unless the user explicitly pre-approved them.

## Validation sequence

Run the narrowest checks first so failures are easy to localize:

1. Parse JSON and validate unique stable IDs.
2. Confirm required fields and proposal decisions.
3. Confirm referenced media paths exist.
4. Run syntax checks for changed JavaScript or server files.
5. Run project validators and tests.
6. Build embedded content and standalone HTML.
7. Package skills and inspect archives.
8. Build the project ZIP and test its integrity.
9. When a browser is available, launch the site and inspect desktop and narrow layouts.

If a visual check cannot run, state that honestly in the worklog and final result.

## Destructive changes

Deletion requires explicit authority. Before deleting a section, asset, proposal, resource, schema field, or route:

- search for references;
- identify historical value;
- decide whether deprecation or consolidation is safer;
- record the removal in the worklog;
- validate exports and links.

Never delete attached resources or prior worklogs as cleanup without direct instruction.
