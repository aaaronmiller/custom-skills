# Living Documents format

The canonical format is defined by `/home/cheta/LIVING_DOCUMENTS/system/SPECIFICATION.md`.

Project prose and planning state live in Markdown. YAML frontmatter supplies stable identity and relationships. Generated JSON, renderer caches, browser overlays, and indexes are projections and may be rebuilt.

The stable unit is a project folder, not a month. History records time inside that folder. Older competing source documents remain under the project's archive until adjudicated.

## Interactive question convention

Question semantics remain ordinary canonical Markdown:

```markdown
## Questions for the user

### Question 1: Which direction should govern?

**A. Use the existing owner. Recommended.** Preserves one authority.

**B. Create a new owner.** Adds an explicit boundary.

**Write-in:** Name another direction and its constraints.
```

The exact level-two heading activates a question packet. Each level-three
`Question N:` heading creates one question. Bold lettered paragraphs create
radio choices; `Recommended.` marks the suggested choice; `Write-in:` creates
the custom-answer field. At least two lettered choices are required.

The renderer stores unfinished answers in browser-local state. Submit writes a
mode-0600 loopback receipt under
`~/.local/state/living-documents/question-responses/`, then the continuity
resolver exposes it as `review-pending`. The receipt is input evidence, not
canonical content or execution authority. After applying valid answers to the
dossier, acknowledge it with `ld-ledger ack-question --receipt-id <id>`.
