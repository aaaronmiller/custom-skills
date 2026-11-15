#!/usr/bin/env python3
"""Normalize raw YouTube transcript text for downstream artifact extraction.

This utility is optional. It does not summarize, classify, or remove substantive
content. It cleans repeated whitespace, joins caption fragments, and can preserve
timestamp-prefixed lines.

Usage:
  python3 scripts/normalize-transcript.py input.txt --output normalized.txt
  cat input.txt | python3 scripts/normalize-transcript.py - --preserve-lines
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


TIMESTAMP_RE = re.compile(
    r"^\s*(?:\(?\d{1,2}:)?\d{1,2}:\d{2}(?:\.\d{1,3})?\)?\s*[-–—:]?\s*"
)


def read_text(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8", errors="replace")


def normalize(text: str, preserve_lines: bool = False) -> str:
    text = text.replace("\ufeff", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Remove common VTT/SRT technical lines while preserving timestamp text lines.
    lines = []
    previous = None
    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            if preserve_lines:
                lines.append("")
            continue
        if line.upper() in {"WEBVTT", "Kind: captions", "Language: en"}:
            continue
        if re.match(r"^\d+$", line):
            continue
        if "-->" in line:
            # Timestamp ranges in VTT/SRT do not carry content.
            continue
        # Strip HTML-ish caption tags but leave text.
        line = re.sub(r"<[^>]+>", "", line)
        line = re.sub(r"\s+", " ", line).strip()
        # Drop exact duplicate consecutive caption fragments.
        if line and line != previous:
            lines.append(line)
            previous = line

    if preserve_lines:
        output = "\n".join(lines)
        output = re.sub(r"\n{3,}", "\n\n", output)
        return output.strip() + "\n"

    # Paragraphize: keep timestamp-started lines separate, join short fragments.
    paragraphs: list[str] = []
    buffer: list[str] = []

    def flush() -> None:
        nonlocal buffer
        if buffer:
            paragraphs.append(" ".join(buffer).strip())
            buffer = []

    for line in lines:
        if not line:
            flush()
            continue
        if TIMESTAMP_RE.match(line):
            flush()
            paragraphs.append(line)
        else:
            buffer.append(line)
            if len(" ".join(buffer)) > 600 or line.endswith((".", "?", "!", ":")):
                flush()
    flush()

    return "\n\n".join(p for p in paragraphs if p).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize a YouTube transcript text file.")
    parser.add_argument("input", help="Input transcript path, or '-' for stdin.")
    parser.add_argument("--output", "-o", help="Output path. Defaults to stdout.")
    parser.add_argument("--preserve-lines", action="store_true", help="Preserve one caption/text unit per line.")
    args = parser.parse_args()

    try:
        text = read_text(args.input)
        result = normalize(text, preserve_lines=args.preserve_lines)
        if args.output:
            Path(args.output).write_text(result, encoding="utf-8")
        else:
            sys.stdout.write(result)
        return 0
    except Exception as exc:  # pragma: no cover
        print(f"normalize-transcript failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
