# yt-transcript-obsidian-artifact

A Claude / Agent Skills package for converting pasted YouTube transcripts, subtitle dumps, caption text, lecture transcripts, and podcast transcripts into high-fidelity Obsidian-ready knowledge artifacts.

This skill is optimized for depth, provenance, and reusable knowledge extraction—not generic summaries.

## What it does

- Produces an Obsidian-ready Markdown artifact that begins with YAML frontmatter.
- Preserves speaker structure or derives coherent thematic clusters.
- Labels provenance with `[VERBATIM]`, `[DESCRIBED]`, `[CONSTRUCTED]`, and `[INFERRED]`.
- Extracts prompts, commands, examples, frameworks, tools, URLs, dates, thresholds, and implementation steps.
- Builds dual-audience deep dives for conceptual strategy and practical execution.
- Includes validation scripts and reusable templates.

## Package structure

```text
yt-transcript-obsidian-artifact/
├── SKILL.md
├── README.md
├── LICENSE.txt
├── scripts/
│   ├── detect-structure.py
│   ├── normalize-transcript.py
│   └── validate-artifact.py
├── references/
│   ├── artifact-schema.md
│   ├── competitive-research.md
│   ├── framework-mapping.md
│   ├── obsidian-formatting.md
│   ├── provenance-labels.md
│   └── research-notes.md
└── assets/
    ├── eval-queries.json
    ├── obsidian-artifact-template.md
    ├── sample-transcript.txt
    └── sample-output-skeleton.md
```

## Installation

### Claude.ai

Upload the generated `yt-transcript-obsidian-artifact.skill` file through Claude's Skills upload UI. The file is a zip-compatible archive with a `.skill` extension. If your client accepts only `.zip`, rename the file from `.skill` to `.zip`.

### Claude Code

Unpack the archive and place the folder here:

```bash
~/.claude/skills/yt-transcript-obsidian-artifact/
```

Then start or continue Claude Code and ask with a relevant transcript task, or invoke the skill directly if your client exposes direct invocation.

## Example use

```text
Convert this transcript into a structured Obsidian knowledge note:

[PASTE TRANSCRIPT]
```

## Optional utilities

Validate an artifact:

```bash
python3 scripts/validate-artifact.py output.md --strict
```

Normalize a raw transcript:

```bash
python3 scripts/normalize-transcript.py raw-transcript.txt --output normalized.txt
```

Detect structure candidates:

```bash
python3 scripts/detect-structure.py normalized.txt --json
```

## Design principles

1. Main `SKILL.md` stays concise.
2. Long schema and syntax references live in `references/` and `assets/`.
3. Scripts are optional helpers, not required for normal use.
4. User-provided transcript text is the source of truth.
5. External verification is opt-in unless safety-critical/current facts require it.
6. The artifact is suitable for Obsidian vault storage, AI retrieval, and repeated use.

## License

MIT. See `LICENSE.txt`.
