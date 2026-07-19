---
title: Living conversation lifecycle
version: 1.2.0
---

# Living conversation lifecycle

Use this reference when the skill is invoked before or during a long conversation.

## Intended lifecycle

The skill does not assume the conversation is finished. The preferred lifecycle is:

1. human invokes the skill;
2. model and human discuss the topic;
3. model creates or updates the living document as state accumulates;
4. model records findings in Markdown sections;
5. model records questions or options in `modelReplies`;
6. human answers through annotations, section drafts, or proposal decisions;
7. model continues all unblocked work without waiting on unrelated clarifications;
8. worklogs record model progress after each substantial revision.

The document lets the human and model progress at different speeds. The human can annotate precise passages when ready. The model can continue on independent tasks, add additional clarification requests, and preserve what is blocked without losing the rest of the work.

## Model reply queue

Use `modelReplies` for questions the model needs answered or options the model wants the human to choose among.

Each reply should include:

- `id`;
- `prompt`;
- optional `context`;
- `targetIds`;
- `status`: open, answered, blocked, or resolved;
- `options`, including a custom-answer option when useful;
- timestamps.

Use a model reply when the model can keep working elsewhere. Use a blocking final response only when all useful remaining work is blocked.

## Human answers

Humans can respond through:

- annotations on selected text;
- section quick edits;
- proposal decisions;
- exported change-request JSON;
- direct Markdown edits.

Annotations are the best default for lightweight comments, objections, and answers. Section drafts are better when the human is replacing prose. Proposal decisions are best when the model supplied discrete options.

## Progress discipline

The model should keep working when:

- a question blocks one section but not others;
- a later task can proceed with a documented assumption;
- the document can record a provisional path and revisit it;
- evidence gathering, cleanup, validation, or formatting remains useful.

The model should stop when:

- every remaining path depends on a human decision;
- proceeding would overwrite explicit human intent;
- the next action is destructive or externally consequential without authorization;
- required files or evidence are unavailable.

## State locations

- Findings: `public/content/sections/*.md`
- Section order and metadata: `public/content/index.json`
- Human comments: `public/data/annotations.json`
- Model questions and options: `modelReplies` in the manifest
- Candidate changes: `proposals` in the manifest
- Attachments and media: `resources` in the manifest plus files under `resources/`
- Model activity: `worklogs`
- Reader-facing release notes: `releases`
