# Research Notes and Design Rationale

This skill was designed against the current Agent Skills specification and official Anthropic documentation, plus competitive research into YouTube transcript and Obsidian skills.

## Official structure requirements

Key design constraints followed:
- A skill is a directory containing `SKILL.md`.
- The skill may include optional `scripts/`, `references/`, and `assets/` directories.
- `SKILL.md` must contain YAML frontmatter followed by Markdown body content.
- Required frontmatter fields are `name` and `description`.
- The `name` field must match the parent directory and use lowercase letters, numbers, and hyphens.
- The `description` field is the primary trigger surface and must describe what the skill does and when to use it.
- Long context should be split into reference files and loaded through progressive disclosure.
- Scripts should be self-contained, have useful errors, avoid interactive prompts, and support validation or repeatable work.

## Packaging notes

The package is a zip-compatible archive renamed to `.skill`. If a client only accepts `.zip`, rename it back to `.zip`.

The archive should contain the folder as its root:

```text
yt-transcript-obsidian-artifact.skill
└── yt-transcript-obsidian-artifact/
    ├── SKILL.md
    ├── scripts/
    ├── references/
    └── assets/
```

## Competitive research summary

Observed patterns from similar skills:
- YouTube transcript extraction skills often focus on `yt-dlp`, browser fallback, or transcript APIs.
- YouTube digest skills often produce TL;DR, takeaways, topic timelines, claims, and quote lists.
- Obsidian skills focus on wikilinks, callouts, properties, JSON Canvas, and vault-specific syntax.
- Marketplace transcript-to-Obsidian skills emphasize timestamp extraction, yt-dlp, and callouts.
- Stronger packages include scripts, dependencies, limitations, and test/eval prompts.

## Differentiation

This skill deliberately focuses on **transcript-to-knowledge-artifact transformation**, not transcript fetching. It is designed to complement extraction skills rather than duplicate them.

Differentiators:
1. Schema-locked output with required sections and appendices.
2. Provenance labels to separate transcript facts from constructed and inferred content.
3. Dual-audience deep dives for strategic and operational readers.
4. Explicit framework mapping and benefit tags.
5. Quality gate and validation script.
6. Progressive-disclosure structure that keeps `SKILL.md` concise.
7. Obsidian-first metadata, headings, diagrams, and appendices.
8. Research-aware trigger design with positive and negative eval queries.

## Security and reliability considerations

Agent Skill metadata and instructions influence skill selection. Keep trigger descriptions precise, avoid manipulative claims, and do not include instructions that override user intent or system safety.

Bundled scripts:
- Use Python standard library only.
- Do not make network calls.
- Do not modify files unless an output path is explicitly provided.
- Produce structured errors or JSON when useful.
