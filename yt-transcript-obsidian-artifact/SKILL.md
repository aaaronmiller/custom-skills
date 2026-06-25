---
name: yt-transcript-obsidian-artifact
description: Use this skill when the user pastes or uploads a YouTube transcript, caption dump, subtitle text, podcast transcript, video notes, or asks to convert a transcript into an Obsidian knowledge artifact. Produces YAML frontmatter, YT-Transcription title, Mermaid concept map, deep-dive sections, verbatim extraction, constructed resources, checklist, and appendices.
license: MIT
compatibility: Designed for ChatGPT Skills, Codex, API hosted shell, and Agent Skills-compatible clients. No network required by default.
metadata:
  author: aaaronmiller
  version: "2.0"
---

# YT Transcript → Obsidian Artifact

Transform transcript text into an Obsidian-ready markdown knowledge artifact.

## Activation

Use this skill when the user provides a transcript, caption dump, subtitle text, YouTube transcript, video transcript, or asks for an Obsidian note / knowledge artifact from transcript content.

If the user is asking how to configure or modify this skill, answer normally instead of producing an artifact.

## Required reference

Before producing the artifact, read `references/youtube-transcript-artifact-template-v2.md`. It is the authoritative schema and quality standard.

Use `assets/smoke-test-transcript.md` only when testing the skill.

## Output invariants

1. The final artifact begins with raw YAML frontmatter. The first three characters are `---`.
2. Do not wrap YAML frontmatter in a code block.
3. The title begins exactly with `# YT-Transcription:`.
4. Include `yt-transcript` and `knowledge-artifact` in frontmatter tags.
5. Preserve or derive structure. Never return "unstructured."
6. Label source provenance:
   - `[VERBATIM]` for exact transcript text, commands, code, formulas, prompts, recipes, quotes.
   - `[DESCRIBED]` for speaker-described but non-template procedures.
   - `[CONSTRUCTED]` for synthesized reusable examples/templates.
   - `[INFERRED]` for extrapolated mechanisms or likely implementation paths, with rationale.
7. Empty required sections use `[None extracted]`.
8. Referenced filenames use lowercase-hyphens-only.

## Workflow

1. Read the transcript.
2. Detect explicit enumeration. If found, lock it and mark `[ENUMERATION_LOCKED: X items]`.
3. If no enumeration exists, derive thematic clusters and mark `[DERIVED_STRUCTURE: X clusters]`.
4. Mine verbatim material: commands, code, formulas, prompts, recipes, examples, warnings, dates, prices, versions, URLs, tools, people, organizations, and timestamps.
5. Build the artifact using the section order in the reference template.
6. Run the quality gate in the reference template.
7. Output only the finished artifact unless the user asked for setup/debugging help.

## External information policy

Use only the transcript and general domain knowledge by default. Search or browse only when the user explicitly asks for verification, when safety/current-fact validation is needed, or when the transcript's claim is time-sensitive and must be separated from transcript-derived content.

## Quality gate

Before final output, confirm silently:

- YAML starts the response.
- Title prefix is exact.
- Speaker structure is locked or derived.
- Labels are correct.
- Deep Dive sections serve strategic and practical readers.
- Major concepts map to frameworks.
- Problems/opportunities include Prepare / Recognize / Execute.
- Appendices are present.
- Empty required sections say `[None extracted]`.
