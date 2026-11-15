# Competitive Research

This file captures implementation ideas from adjacent public skills without copying their content.

## YouTube transcript extraction skills

Common strengths:
- URL validation.
- Multiple YouTube URL formats.
- `yt-dlp` as a primary or fallback extractor.
- Browser/cookie fallback when captions are restricted.
- Conversion from `.vtt` or `.srt` to clean text.
- Error reporting for missing captions, private videos, and age restrictions.

Design implication for this skill:
- Do not duplicate extraction as the core mission.
- If a URL is supplied, first obtain transcript text using available tools or another skill, then apply the artifact workflow.
- Preserve limitations clearly when transcript quality is unknown.

## YouTube digest skills

Common strengths:
- TL;DR.
- Key takeaways.
- Timestamped claims.
- Topic timeline.
- Notable quotes.
- Environment-tier fallback logic.

Design implication for this skill:
- Include digest components, but do not stop at digest depth.
- Preserve procedures, frameworks, resources, and implementation checklists.
- Use appendices for terminology, entities, and prompt indexes.

## Obsidian-focused skills

Common strengths:
- YAML properties.
- Wikilinks.
- Callouts.
- Embeds.
- Vault-aware file naming.
- Markdown validation.

Design implication for this skill:
- Keep all output valid Obsidian Markdown.
- Use raw YAML frontmatter.
- Use callouts sparingly.
- Avoid invented vault links.
- Produce notes suitable for search, linking, and future retrieval.

## Best-in-category target

The category target is not "shortest summary" or "fastest transcript fetch." It is:

> Highest-fidelity transformation of raw spoken transcripts into reusable Obsidian knowledge artifacts.

That means success is measured by:
- Low information loss.
- Clear provenance.
- Reusable procedures.
- Strong structure detection.
- Good handling of exact commands/prompts/examples.
- Obsidian compatibility.
- Validation and repeatability.
