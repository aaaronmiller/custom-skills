# Canonicalize destinations and summarize groups
<!-- canonicalize-brief v1. One pass over all chunks after review. -->

Several workers chose destinations independently, so the same project or category can appear under slightly different names, and some folders hold a single file. Produce one consistent folder plan.

Inputs
- All decisions: `{{WORKDIR}}/decisions-*.json`, with reviewer corrections in `{{WORKDIR}}/review-*.json` (a correction overrides the decision for its id).
- Facts: `{{WORKDIR}}/org-items*.json` (for names, dates and sizes).
- Rules: `{{SKILL}}/references/taxonomy.md`.

Do this
1. List every distinct `dest` per root with its member count (a short script is fine for counting; the merging and naming decisions are yours).
2. Merge near-duplicates that mean the same thing (`2026-08 ARDF-model-ranking` and `2026-08 ARDF model ranking dashboards` -> one name). Projects that are clearly the same effort across roots keep the same name in each root.
3. Fold single-item subfolders into their parent category, except projects with real substance (a project of one large folder is fine).
4. Cap depth at two levels below the top-level folder (three for `Projects/<name>/<part>`).
5. Fix names to `YYYY-MM Topic words` for projects; plain spaced words elsewhere; keep the owner's own vocabulary when it carries meaning.
6. Never change a decision, only destinations; leave `.`, `_Unsure` and `_REVIEW-then-delete` as they are.
7. For each final destination, write one or two plain sentences: what is in it and why the owner saved it (from the members' intents). These appear on the approval page as the group description.

Output: write `{{WORKDIR}}/canonical.json`:
```json
{"dest_map": {"<root>|<old dest>": "<new dest>"},
 "summaries": {"<root>|<final dest>": "One or two sentences."},
 "stats": {"dests_before": 0, "dests_after": 0, "items": 0}}
```
`<root>` is the item's `root` field in org-items.json (the folder its dest is relative to), written exactly as it appears there. Map only destinations you changed; every final destination gets a summary, including `_Unsure` (say what kinds of items ended up there) and `_REVIEW-then-delete` (say what is being removed and why it is safe).
