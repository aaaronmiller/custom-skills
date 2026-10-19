---
name: examine-documents
description: "Reads local files, PDFs or a corpus and writes one cited synthesis. Use when handed material to digest; never searches the web."
license: MIT
metadata:
  author: ice-ninja
  version: "2.0.0"
---

# Examine Documents

Digest material already in hand — a folder of documents, a set of PDFs, a
report to decompose — into one clean synthesis. This skill never searches
the web. When the question needs sources beyond the given material, say so
and offer `deep-research` instead.

## How to run it

1. **Inventory.** List what was handed over (files, formats, rough sizes).
   Say what you will read and what you will skip, before reading it.
2. **Read.** Read the material itself, not summaries of it. For PDFs,
   scans and Office files, extract text with the ocr-and-documents, pdf,
   docx, xlsx or pptx skills first.
3. **Decompose.** Split the material into its distinct claims or topics —
   no more than fit the question. Small folder: hold it in context. Large
   corpus: keep pointer notes (`concept — file:location — one line`), never
   raw pastes, in a scratch file.
4. **Cross-reference.** Where two documents agree or disagree, say so with
   both locations. Contradictions are findings, not noise.
5. **Synthesize.** Write one deliverable: what the material says, where it
   conflicts, what is missing. Cite file and location per claim. Before
   delivery, check each claim has a file and location.

## Depth

Match effort to the material, not a fixed algorithm:

- **Skim** (a few files): read all, answer directly, no scratch files.
- **Standard** (a folder): pointer notes as above, one synthesis pass.
- **Exhaustive** (a corpus): branch per topic, compress each branch to key
  claims plus locations, then synthesize.

No X/Y/Z quotas. The material is bounded; read until it is covered or the
user stops you.

## Delivery and cleanup

The user asked for an answer, not a dozen files. Default to one
deliverable in the working directory:

1. Write the synthesis to the agreed path.
2. If scratch files exist, ask: "Keep the working files, or shall I
   remove them?" If there is no answer, keep the files and name their path.
   If the user confirms — or said "clean up" up front — delete the scratch
   directory and say what was removed.
3. Keep working files only when the user says more analysis follows on the
   same material. Offer removal again at the end of any later run.

Never create session folders, `sources/` dumps, or research plans inside
the skill's own directory. Scratch lives in the run's working directory
and leaves with it.
