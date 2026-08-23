---
name: yt-transcript-obsidian-artifact
description: |-
  Use this skill when the user pastes, uploads, or provides a YouTube transcript, caption dump, subtitle text, podcast transcript, lecture transcript, video notes, or raw spoken-content text, and asks to convert it into a high-fidelity Obsidian-ready knowledge artifact. Produces YAML frontmatter, YT-Transcription title, Mermaid concept map, deep-dive sections with dual-audience treatment, verbatim extraction with provenance labels, constructed resources, implementation checklist, appendices, and methodology telemetry. Do not use for fetching transcripts from URLs unless explicitly asked; transform provided transcript text by default.
  Triggers: "convert this transcript", "make an Obsidian note", "knowledge artifact", "transcript to notes", "yt transcript", "organize this transcript", "create a study note from this", "extract key points from transcript", "forensic transcript", "youtube to obsidian".
license: MIT
compatibility: |-
  Designed for Agent Skills-compatible clients (Claude Code, Codex, Hermes, Gemini, Qwen, KiloCode, OpenCode).
  Optional Python 3.9+ for bundled validation, structure detection, and transcript normalization scripts.
metadata:
  author: aaaronmiller
  version: "2.1.0"
  category: "knowledge-management"
  output_format: "obsidian-markdown"
tags:
  - references
  - scripts
  - assets
  - templates
---

# YouTube Transcript to Obsidian Artifact

Transform pasted YouTube transcripts, caption dumps, subtitle text, or transcript-like spoken content into a high-fidelity Obsidian-ready knowledge artifact.

The priority is forensic fidelity: preserve structure, exact reusable language, commands, examples, tools, dates, quantities, caveats, and speaker intent. Do not collapse the transcript into a generic summary.

## Required references

Before producing a final artifact, load the authoritative schema and quality standard:

- `references/youtube-transcript-artifact-template-v2.md` - the full output template, extraction protocol, labels, rubrics, and validation rules.

For specialized sub-tasks, load as needed:

- `references/provenance-labels.md` - detailed label rules for VERBATIM, DESCRIBED, CONSTRUCTED, INFERRED
- `references/framework-mapping.md` - framework selection guidance for concept mapping
- `references/obsidian-formatting.md` - Obsidian-specific markdown syntax
- `references/competitive-research.md` - competitive analysis and prior art
- `references/artifact-schema.md` - artifact data model reference

## Activation

Use this skill when:
- The user pastes a YouTube transcript, caption dump, subtitle text, or video transcript-like text.
- The user asks to convert a transcript into an Obsidian note, markdown notes, a knowledge artifact, a structured knowledge note, or a reusable research note.
- The user asks to extract prompts, commands, frameworks, resources, examples, or implementation steps from a transcript.

Do not use this skill for:
- A simple one-paragraph summary unless the user also asks for a structured note.
- Fetching a transcript from a YouTube URL unless the user explicitly asks for retrieval. If retrieval is requested, use available tools or another transcript-extraction skill first, then apply this skill to the transcript.
- Summarizing non-transcript documents unless the user asks to treat them as a transcript.

If transcript text is provided, generate the final artifact immediately. Do not ask setup questions unless no usable transcript text exists.

## Output invariants

1. The final answer must be the artifact itself. No preface, greeting, or explanation before it.
2. The first three characters of the response must be raw YAML frontmatter delimiters: `---`
3. Do not wrap YAML in a code block.
4. After frontmatter, the title must begin exactly with `# YT-Transcription:`
5. Use valid Obsidian markdown.
6. Use Mermaid for the visual concept map unless the transcript makes a plain outline more reliable.
7. If a required section has no applicable content, write `[None extracted]`.
8. Use the section order defined in `references/youtube-transcript-artifact-template-v2.md`.
9. Include `yt-transcript` and `knowledge-artifact` in frontmatter tags.
10. Referenced filenames use lowercase-hyphens-only.

## Extraction workflow

### Phase 1: Forensic Extraction

**1a. Cleanly identify the transcript boundary**

Ignore filler such as sponsor reads, intros, outros, like/subscribe chatter, and supporter name rolls unless they contain hard data, claims, warnings, instructions, examples, tools, URLs, or resources.

If the transcript appears truncated, process what is available and add `[TRUNCATION WARNING]` to Appendix D.

If timestamps exist, preserve them where they help trace examples, claims, procedures, or topic timeline.

Optional helper:
```bash
python3 scripts/normalize-transcript.py input.txt --output normalized.txt
```

**1b. Lock or derive the structure**

Scan for explicit structures:
- "Rule X of Y"
- "Step X"
- "Tip X"
- numbered lists
- "first / second / third"
- title claims like "10 ways", "5 steps", or "7 rules"

If explicit structure exists, preserve it and include `[ENUMERATION_LOCKED: X items]` in the Executive Summary.

If no explicit structure exists, derive coherent thematic clusters from topic shifts, chronology, problem/cause/solution flow, repeated claims, or workflow phases. Include `[DERIVED_STRUCTURE: X clusters]`.

Never call the transcript unstructured.

Optional helper:
```bash
python3 scripts/detect-structure.py normalized.txt --json
```

**1c. Mine high-value exact material**

Extract and preserve:
- Exact commands, prompts, formulas, recipes, code, settings, filenames, version numbers, prices, dates, thresholds, URLs, tool names, people, organizations, and examples.
- Speaker-defined rules, methods, frameworks, caveats, anti-patterns, warnings, and demonstrations.
- Technical details and implementation sequences.

Use provenance labels consistently:
- `[VERBATIM]`: exact language, command, code, formula, prompt, recipe, or quote from the transcript
- `[DESCRIBED]`: a speaker-described instruction or process that is not reusable exactly as spoken
- `[CONSTRUCTED]`: reusable example, template, or explanation synthesized from the speaker's described idea
- `[INFERRED]`: implementation path, mechanism, or likely pattern extrapolated from transcript evidence plus general domain knowledge. Include a short rationale

Never present `[CONSTRUCTED]` or `[INFERRED]` material as transcript fact.

For detailed label rules, load `references/provenance-labels.md`.

### Phase 2: Analytical Synthesis

**2a. Build dual-audience deep dives**

For every numbered item or derived cluster, include both strategic/conceptual and practical/operational treatment:

Per-section structure:
- Section title with one benefit tag
- Audience level: Novice, Competent, Proficient, or Expert
- Framework mapping
- Core Concept (canonical meaning in speaker's terms)
- Mechanism (how it works, causal chain, or process)
- Strategic Implication (broader context, meaning, connections)
- Practical Application (concrete actionable implementation guidance)
- Contrast: anti-pattern vs. best practice
- Actionable Applications: Prepare / Recognize / Execute / Framework
- Example labeled `[VERBATIM]`, `[DESCRIBED]`, `[CONSTRUCTED]`, or `[INFERRED]`

Benefit tags:
`[Reduces Friction]`, `[Deepens Thinking]`, `[Improves Context]`, `[Accelerates Execution]`, `[Enhances Reliability]`, `[Improves Transferability]`, `[Reduces Cognitive Load]`, `[Enables Automation]`

For framework-selection guidance, load `references/framework-mapping.md`.

**2b. Apply concept mapping requirements**

Each major concept must have:
- A named framework mapping (e.g., SDLC, Bloom's Taxonomy, Design Thinking, SWOT, SMART goals, ADDIE, FITT)
- When no named framework fits, use `Concept to Mechanism to Outcome`
- The framework line under each Deep Dive header

**2c. Build inference protocol**

When the transcript describes a process without exact commands/steps:
1. Identify the described capability
2. Determine the likely legitimate implementation path from transcript evidence and general domain knowledge
3. Construct a usable pattern only when safe, non-deceptive, and clearly helpful
4. Label clearly as `[INFERRED]` with a rationale
5. For safety-sensitive, legal, medical, financial, or current-fact-dependent claims, provide conservative explanation and state what needs verification

### Phase 3: Format and Validate

**3a. Format for Obsidian**

Use Obsidian-compatible Markdown:
- YAML properties at the top
- Stable lowercase-hyphenated tags
- Wikilinks only when the note is likely to exist in the vault; otherwise use plain text or markdown links
- Callouts sparingly for warnings, methodology gaps, or key takeaways
- Mermaid diagrams for concept maps (prefer `mindmap` for conceptual, `flowchart` for process, `graph LR` for causal systems)

For Obsidian syntax guidance, load `references/obsidian-formatting.md`.

**3b. Validate before finalizing**

Before answering, silently check:
- YAML starts the response
- `yt-transcript` and `knowledge-artifact` tags are present
- Title prefix is exactly `# YT-Transcription:`
- Speaker structure is locked or derived
- Exact quotes/prompts/commands are labeled `[VERBATIM]`
- Constructed and inferred material is labeled correctly
- Every Deep Dive section has strategic and practical content
- Every major concept has a framework mapping
- Every problem or opportunity has Prepare / Recognize / Execute actions
- Empty required sections say `[None extracted]`
- Referenced filenames are lowercase-hyphens-only
- Mermaid syntax is plausible and avoids characters that commonly break rendering
- No intro/outro fluff is summarized unless it contains unique data, claims, or resources

Optional helper:
```bash
python3 scripts/validate-artifact.py output.md --strict
```

## Gotchas

- Do not add a preface, greeting, or explanation before the YAML frontmatter.
- Do not put the artifact inside a fenced code block.
- Do not over-summarize. This skill is for high-fidelity knowledge extraction, not short digests.
- Do not browse by default. Use only the transcript and general domain knowledge unless the user explicitly asks for verification or the transcript includes safety-critical/current-fact claims.
- Do not let sponsor/outro material dominate the artifact, but extract unique tools, URLs, resources, hard claims, or instructions from those sections.
- Do not omit sections. Use `[None extracted]` where appropriate.
- Do not invent timestamps, URLs, prices, commands, or citations that are not in the transcript.
- Do not label a paraphrase as `[VERBATIM]`; use `[DESCRIBED]` or lower as appropriate.
