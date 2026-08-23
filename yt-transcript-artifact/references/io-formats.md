# YouTube Transcript Extraction — Input/Output Formats

## Input

- YouTube video URL (any format: youtube.com/watch, youtu.be, youtube.com/shorts, etc.)
- Alternative: manually pasted transcript (when API extraction fails)

## Output Format

The extraction template produces an Obsidian-ready markdown file with:

- YAML frontmatter: date, source, author, model, tags, source_url
- Visual concept map (Mermaid)
- Executive summary with benefit tags
- Deep-dive analysis per enumerated/thematic section
- Tool & command library
- LLM prompt catalog (verbatim vs constructed)
- Implementation checklist
- Appendices: rubric, terminology, entities, methodology telemetry, prompt index

## Output Location

Copied to Obsidian vault: `$HOME/documents/chetaz/` (configurable in `yt_extract.py`)
