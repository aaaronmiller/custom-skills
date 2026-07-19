---
title: Change-request contract
version: 2.0.0
---

# Change-request contract

A change request is the bridge between browser-local deliberation and canonical file modification. Treat it as an auditable instruction envelope.

## Required fields

- `requestId`: unique request identity;
- `document.documentId`, `version`, and `formatVersion`;
- `createdAt`;
- `scope`: stable target IDs;
- `drafts`: local section overlays;
- `proposalDecisions`: local approve, defer, or reject choices;
- `annotations`: local comments and evidence pointers;
- `constraints`: invariants and negative constraints;
- `expectedOutputs`: files and reports required from the applying agent or service.

## Authority

Use this precedence:

1. current explicit instruction;
2. explicit proposal decision;
3. direct local draft for its targeted fields;
4. decision or objection annotation;
5. attached evidence;
6. existing document invariant;
7. agent suggestion.

A rejected proposal blocks implementation until explicitly reconsidered. A deferred proposal remains visible but is not permission.

## Draft semantics

A draft contains the complete local values for the fields it changes, normally:

- `sectionId`;
- `title`;
- `dek`;
- `status`;
- `tags`;
- `markdown`;
- `updated` and `updatedAt`.

Apply the draft to the matching stable section. Do not create a new section merely because the title changed.

## Applying a request

1. Verify document ID, base version, and format version.
2. Reject or explicitly reconcile a stale base version.
3. Apply local drafts before deeper synthesis.
4. Apply approved and rejected proposal decisions.
5. Preserve annotations unless the request resolves them.
6. Edit the narrowest files.
7. Append history and worklog entries.
8. Add release notes when behavior or reader-visible content changed materially.
9. Validate and return a structured result.

## Security

Never include credentials, authentication files, unrelated local storage, or executable attachments. Treat attachment type and content as untrusted until inspected.
