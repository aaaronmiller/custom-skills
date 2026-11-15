#!/usr/bin/env python3
"""
YouTube Transcript → Obsidian Knowledge Artifact Pipeline

Workflow:
1. Fetch transcript from YouTube URL
2. Format transcript with extraction template
3. Send to LLM API (OpenRouter) for processing
4. Post-process: validate YAML frontmatter, sanitize title
5. Copy result to Obsidian vault

Usage:
    python3 yt_extract.py <youtube_url>
    python3 yt_extract.py <youtube_url> --model anthropic/claude-3.5-sonnet
    python3 yt_extract.py <youtube_url> --dry-run

Dependencies:
    uv pip install --break-system-packages youtube-transcript-api openai
"""

import sys
import os
import re
import json
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone

# ── Configuration ────────────────────────────────────────────────────────────
# Paths
SKILL_DIR = Path(__file__).resolve().parent.parent  # parent of scripts/
TEMPLATE_FILE = SKILL_DIR / "templates" / "extraction-template.md"
VAULT_PATH = Path("/mnt/c/Users/Administrator/Documents/chetaz")
VAULT_PATH_POSIX = Path.home() / "code2" / "video-transcriptions"  # WSL fallback

# LLM settings
DEFAULT_MODEL = "qwen/qwen3-coder-plus:free"
MAX_RETRIES = 2
MAX_TOKENS = 120000  # YouTube transcripts are long, need big context

# API key — prefers OPENROUTER_API_KEY from env, then .env files
def get_api_key():
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        # Try hermes .env
        env_file = Path.home() / ".hermes" / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("OPENROUTER_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    if not key:
        print("ERROR: OPENROUTER_API_KEY not found in environment or ~/.hermes/.env")
        print("Set it with: export OPENROUTER_API_KEY=sk-or-v1-...")
        sys.exit(1)
    return key


def fetch_transcript(video_id: str) -> dict:
    """Fetch transcript using youtube-transcript-api."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        print("Installing youtube-transcript-api...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install",
                        "--break-system-packages", "-q",
                        "youtube-transcript-api"], check=True)
        from youtube_transcript_api import YouTubeTranscriptApi

    api = YouTubeTranscriptApi()
    
    # Try multiple languages for best transcript
    for lang_codes in [["en"], ["en-US"], ["en-GB"], []]:
        try:
            transcripts = api.fetch(video_id, languages=lang_codes if lang_codes else None)
            transcript_entries = list(transcripts[0])
            
            # Build text with timestamps
            segments = []
            full_text = []
            for entry in transcript_entries:
                ts = time.strftime("%M:%S", time.gmtime(entry.get("start", 0)))
                text = entry.get("text", "")
                segments.append(f"[{ts}] {text}")
                full_text.append(text)
            
            return {
                "video_id": video_id,
                "segments": "\n".join(segments),
                "text": " ".join(full_text),
                "length_chars": len(" ".join(full_text)),
                "length_words": len(" ".join(full_text).split()),
                "language": "en",
            }
        except Exception as e:
            if lang_codes == []:
                print(f"Error fetching transcript: {e}")
            continue
    
    print("Could not fetch transcript automatically.")
    print(f"Please extract manually from a transcript service.")
    print("Paste the transcript below and press Ctrl+D when done:")
    transcript_text = sys.stdin.read().strip()
    if not transcript_text:
        print("No transcript provided. Exiting.")
        sys.exit(1)
    return {
        "video_id": video_id,
        "text": transcript_text,
        "segments": "",
        "length_chars": len(transcript_text),
        "length_words": len(transcript_text.split()),
        "language": "manual",
    }


def send_to_llm(transcript_text: str, template_text: str, model: str, dry_run: bool = False) -> str:
    """Send transcript + template to LLM via OpenRouter API."""
    api_key = get_api_key()
    
    system_prompt = """You are an expert knowledge extraction engine. Your job is to transform raw video transcripts into structured, Obsidian-ready knowledge artifacts. Follow the extraction template EXACTLY. Do not skip sections. Do not summarize intro/outro. Extract ALL technical details, tools, commands, and prompts mentioned.

CRITICAL: The VERY FIRST thing in your output MUST be the YAML frontmatter enclosed in --- (not #). Do NOT wrap it in a code block."""

    user_prompt = f"""Here is the extraction template I want you to follow:

{template_text}

---

Here is the YouTube video transcript to process:

{transcript_text}

---

Process this transcript according to the template. Remember:
- YAML frontmatter FIRST, enclosed in ---
- Extract ALL information groups present
- Preserve verbatim commands and prompts
- Generate the implementation checklist
- Include all appendices
"""

    if dry_run:
        print("\n=== DRY RUN ===")
        print(f"Model: {model}")
        print(f"System prompt length: {len(system_prompt)} chars")
        print(f"User prompt length: {len(user_prompt)} chars")
        print(f"Total tokens (est): {(len(system_prompt) + len(user_prompt)) // 4}")
        print("=" * 50)
        return ""

    from openai import OpenAI
    
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    
    print(f"Sending to {model} (est. {(len(system_prompt) + len(user_prompt)) // 4} tokens)...")
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=MAX_TOKENS,
        temperature=0.3,  # Low temperature for extraction accuracy
    )
    
    result = response.choices[0].message.content
    return result


def sanitize_title_for_filename(title: str) -> str:
    """Remove characters not allowed in Obsidian filenames."""
    # Remove: : / \ * ? " < > |
    sanitized = re.sub(r'[:/\\*?"<>|]', '-', title)
    # Collapse multiple hyphens
    sanitized = re.sub(r'-+', '-', sanitized)
    # Remove leading/trailing hyphens
    sanitized = sanitized.strip('-')
    # Truncate to 100 chars
    if len(sanitized) > 100:
        sanitized = sanitized[:100]
    return sanitized


def extract_yaml_frontmatter(content: str) -> tuple:
    """Extract and validate YAML frontmatter from content."""
    # Match content between --- blocks at the start
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        # Try to find YAML that's missing the delimiter
        yaml_match = re.match(r'^(title:.*?tags:.*?)\n', content, re.DOTALL)
        if yaml_match:
            yaml_block = yaml_match.group(1)
            remaining = content[len(yaml_block):].lstrip()
            return yaml_block, remaining
        return None, content
    
    yaml_block = match.group(1)
    remaining = content[match.end():]
    return yaml_block, remaining


def validate_and_fix_yaml(yaml_block: str, source_url: str, model_used: str) -> str:
    """Ensure YAML has required fields and is valid."""
    lines = yaml_block.splitlines()
    
    # Check for title field
    has_title = any(line.startswith("title:") for line in lines)
    has_date = any(line.startswith("date:") for line in lines)
    has_source = any(line.startswith("source:") for line in lines)
    has_tags = any(line.startswith("tags:") for line in lines)
    
    if not has_title:
        lines.append(f"source_url: {source_url}")
    if not has_date:
        lines.append(f"date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}")
    if not has_source:
        lines.append(f"source: {source_url}")
    if not has_tags:
        lines.append("tags: [yt-transcript, knowledge-artifact]")
    
    return "\n".join(lines)


def copy_to_vault(content: str, title: str, output_path: Path = None) -> Path:
    """Copy the processed document to the Obsidian vault."""
    target_dir = output_path or VAULT_PATH
    if not target_dir.exists():
        # Fallback to WSL-friendly path
        target_dir = VAULT_PATH_POSIX
        target_dir.mkdir(parents=True, exist_ok=True)
        print(f"Primary vault not found, using WSL fallback: {target_dir}")
    
    # Sanitize filename
    safe_title = sanitize_title_for_filename(title)
    filename = f"{safe_title}.md"
    
    filepath = target_dir / filename
    filepath.write_text(content, encoding="utf-8")
    print(f"Saved to: {filepath}")
    return filepath


def main():
    parser = argparse.ArgumentParser(description="Extract YouTube transcript → Obsidian artifact")
    parser.add_argument("url", help="YouTube video URL or raw video ID")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL,
                       help=f"LLM model for processing (default: {DEFAULT_MODEL})")
    parser.add_argument("--dry-run", "-d", action="store_true",
                       help="Show what would be done without calling LLM")
    parser.add_argument("--output", "-o", type=str, default=None,
                       help="Output path for vault (default: Obsidian vault path)")
    parser.add_argument("--no-copy", action="store_true",
                       help="Don't copy to vault, just show output")
    parser.add_argument("--transcript-only", action="store_true",
                       help="Only fetch and display transcript, don't process")
    
    args = parser.parse_args()
    
    # Extract video ID from URL
    url = args.url
    video_id = url
    if "youtube.com" in url or "youtu.be" in url:
        # Extract ID from URL
        import re
        match = re.search(r'(?:v=|youtu\.be/|shorts/|embed/)([a-zA-Z0-9_-]{11})', url)
        if match:
            video_id = match.group(1)
    
    print(f"Video ID: {video_id}")
    print(f"Model: {args.model}")
    print()
    
    # Step 1: Fetch transcript
    print("Fetching transcript...")
    transcript = fetch_transcript(video_id)
    print(f"  Got {transcript['length_words']} words, {transcript['length_chars']} chars")
    
    if args.transcript_only:
        print(f"\n{transcript['text']}")
        return
    
    if args.dry_run:
        # Just show transcript stats and exit
        template_text = TEMPLATE_FILE.read_text()
        print(f"  Template length: {len(template_text)} chars")
        return
    
    print()
    
    # Step 2: Load template
    if not TEMPLATE_FILE.exists():
        print(f"ERROR: Template not found at {TEMPLATE_FILE}")
        print("Expected: SKILL_DIR/templates/extraction-template.md")
        sys.exit(1)
    
    template_text = TEMPLATE_FILE.read_text()
    print(f"Template loaded ({len(template_text)} chars)")
    
    # Step 3: Send to LLM
    print(f"\nProcessing with {args.model}...")
    result = send_to_llm(transcript['text'], template_text, args.model)
    
    if not result:
        print("LLM returned empty content. Aborting.")
        sys.exit(1)
    
    print(f"  LLM output: {len(result)} chars")
    
    # Step 4: Post-process YAML
    yaml_block, body = extract_yaml_frontmatter(result)
    if yaml_block:
        # Validate and fix
        fixed_yaml = validate_and_fix_yaml(
            yaml_block,
            source_url=f"https://www.youtube.com/watch?v={video_id}",
            model_used=args.model
        )
        
        # Extract title for filename
        title_match = re.search(r'title:\s*(.+)', result)
        if title_match:
            title = title_match.group(1).strip().strip('"').strip("'")
        else:
            title = f"YT-{video_id}"
    else:
        # No YAML found, wrap content
        fixed_yaml = f"title: YT-{video_id}\ndate: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}\nsource: https://www.youtube.com/watch?v={video_id}\nmodel: {args.model}\ntags: [yt-transcript, needs-review]"
        body = result
        title = f"YT-{video_id}"
    
    # Reconstruct final content
    final_content = f"---\n{fixed_yaml}\n---\n\n{body}"
    
    # Step 5: Copy to vault
    if args.no_copy:
        print(f"\n{'='*60}")
        print("RESULT (not copied to vault):")
        print("=" * 60)
        print(final_content[:3000])
        if len(final_content) > 3000:
            print(f"\n... ({len(final_content) - 3000} more chars)")
    else:
        output_path = Path(args.output) if args.output else None
        filepath = copy_to_vault(final_content, title, output_path)
        print(f"\nDone! Artifact saved to {filepath}")


if __name__ == "__main__":
    main()
