# Change-request contract

A change request is the bridge between human deliberation and file modification. Treat it as a signed instruction envelope even when it is not cryptographically signed.

## Important fields

- `requestId` and `createdAt`: audit identity.
- `document`: target identity, version, files, and preferred edit strategy.
- `instruction`: free-form current execution instruction.
- `decisions`: approved, rejected, and deferred proposal arrays.
- `localEdits`: complete current values for sections edited in the browser.
- `annotations`: comments and decisions attached to document targets.
- `resources`: attachment manifests and paths.
- `visualRefactor`: requested visual communication state.
- `invariants`: constraints that must remain true.
- `requestedResult`: required reporting fields.

## Authority and conflict resolution

The current request and explicit decisions are authoritative. A browser-edited section is authoritative for that section’s current wording unless the same request explicitly asks the agent to rewrite it. An annotation marked `decision` or `objection` carries more weight than a generic comment.

When two approved items conflict, do not choose silently. Reconcile them if possible, otherwise preserve both as explicit alternatives and report the conflict. When an approved item conflicts with a rejected item, the rejected item blocks implementation until the user resolves the contradiction.

## Local edits

`localEdits.sections` contains complete section objects, not patches. Apply them before deeper synthesis so the agent reasons from the user’s latest wording. Preserve the section ID. If a local edit is structurally invalid, repair the minimum necessary fields and report the repair.

Dirty IDs such as `proposal-appendix`, `visual-refactor`, and `worklog-zone` indicate that non-section state changed.

## Annotations

Do not concatenate annotations into the nearest paragraph. Interpret each note according to target and kind:

- `comment`: consideration or suggestion.
- `decision`: explicit direction.
- `objection`: constraint or unresolved concern.
- `evidence`: factual support requiring inspection.
- `reference`: model, file, or example to consult.
- `image-direction`: visual argument or asset guidance.
- `implementation-note`: code or workflow requirement.

If an annotation is superseded by a later annotation, preserve both and record the resolution in the new worklog.

## Resources

Resource records may include original name, stored name, URL, type, size, and SHA-256. Use the stored project path. Do not assume extension equals content type. Never execute attachments by default.

## Invariants

Invariants are testable constraints. Before completion, verify each invariant or state why verification was impossible. Treat “preserve rejected proposals” and “append a worklog” as hard requirements, not preferences.

## Result

When `--output-schema` is active, produce exactly the required structure. Do not wrap the JSON in Markdown. The result describes what actually happened, not what the agent intended to do.
