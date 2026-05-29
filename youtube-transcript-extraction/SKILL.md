---
name: youtube-transcript-extraction
description: Extract YouTube video transcripts and transform them into high-fidelity, Obsidian-ready knowledge artifacts with structured information groups (recipes, prompts, lists, processes, etc). Use when processing video content, extracting instructional workflows, or building agentic reference materials from video sources. Supports transcript fetching, AI processing with custom template, and automated vault copy.
version: 1.0.0
author: LO (curated by Hermes Agent)
license: MIT
metadata:
  hermes:
    tags: [youtube, transcript, obsidian, knowledge-extraction, artifacts, video-processing, yt-transcript]
    related_skills: [youtube-content, obsidian, ocr-and-documents]
inputs:
  - name: video_url
    description: YouTube video URL for structured knowledge extraction
    pointer_type: parameter
outputs:
  - name: knowledge_artifact
    description: Obsidian-ready structured knowledge artifact
    pointer_type: output_file
---

# YouTube Transcript → Obsidian Knowledge Artifact

Transform YouTube videos into structured, agentic-reference knowledge artifacts stored in Obsidian.

## TL;DR — Quick Usage

```bash
python3 SKILL_DIR/scripts/yt_extract.py <video_url>
```

That's it. It fetches the transcript, sends it to an LLM with the extraction template, and copies the result to your Obsidian vault.

## What This Does

1. **Fetches transcript** — uses `youtube-transcript-api` from the video URL
2. **Sends to LLM** — processes through the extraction template with a strong model
3. **Fixes YAML** — post-processing step to ensure valid frontmatter
4. **Copies to Obsidian** — places the file in `$HOME/documents/chetaz/` on the Windows drive
5. **Injects source URL** — adds the original video URL into YAML frontmatter

## Workflow

```
YouTube URL
    ↓
[Script: yt_extract.py]  — fetches transcript via youtube-transcript-api
    ↓ transcript (.txt)
[LLM: Processing]  — sends transcript + extraction template to LLM API
    ↓ processed (.md)
[Post-process]  — validates YAML frontmatter, fixes title/paths
    ↓
[Copy to Obsidian vault]  — Windows path: /mnt/c/Users/Administrator/Documents/chetaz/
```

## Manual Mode (when YouTube API fails)

If a video has no extractable transcript (copyright restrictions, auto-transcript only):

1. Go to https://youtubetotranscript.com/
2. Paste the URL → click the transcript button → copy to clipboard
3. Run:
```python
from hermes_tools import skill_view
# Load this skill to get the full extraction template
```
4. Paste the transcript + template into your LLM for processing
5. Copy result to Obsidian vault

## Dependencies

```bash
# Install once (uv recommended)
uv pip install --break-system-packages youtube-transcript-api
```

## Configuration

Edit `yt_extract.py` to adjust:
- `VAULT_PATH` — your Obsidian vault location (default: `/mnt/c/Users/Administrator/Documents/chetaz/`)
- `SKILL_DIR` — path to this skill directory
- `MODEL` — which OpenRouter model to use for processing (default: `qwen/qwen3.6-plus:free`)

## Known Limitations

- Videos with no subtitles/captions cannot be transcribed programmatically
- The `youtubetotranscript.com` site has captchas between step 2 and 3
- YouTube API blocks some videos (copyright restrictions)
- Obsidian filename restrictions: no `:` `/` `\` `*` `?` `"` `<` `>` `|` — sanitized automatically

## Future Automation Targets

- **DataKiln DOM macro playback** — replace manual transcript site with programmatic browser automation (pending `/code2/dataKiln` project)
- **Multi-model pipeline** — cheap model for transcript fetch, strong model for extraction, test gate on output
- **Obsidian shim** — automatic YAML injection + source URL capture via Obsidian template/plugin
- **Webhook trigger** — when a YouTube URL is pasted into a chat, auto-trigger the extraction pipeline
## 📎 Resources

📎 `~/code/agents/skills/youtube-transcript-extraction/references/i-o.md`
📎 `~/code/agents/skills/youtube-transcript-extraction/scripts/yt_extract.py`
📎 `~/code/agents/skills/youtube-transcript-extraction/templates/extraction-template.md`
