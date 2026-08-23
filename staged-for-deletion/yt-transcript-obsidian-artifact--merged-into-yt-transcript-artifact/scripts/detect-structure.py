#!/usr/bin/env python3
"""Detect explicit enumeration or thematic cluster candidates in transcript text.

This is a lightweight helper for agents. It is not authoritative; the model should
use it as telemetry while still reasoning from the transcript.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


ENUM_PATTERNS = [
    ("numbered-item", re.compile(r"(?im)^\s*(?:\d{1,2})[.)]\s+(.{3,120})")),
    ("rule-step-tip", re.compile(r"(?i)\b(rule|step|tip|lesson|principle|way)\s+(?:number\s+)?(\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten)\b")),
    ("ordinal", re.compile(r"(?i)\b(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\b")),
    ("title-claim", re.compile(r"(?i)\b(\d{1,2})\s+(ways|steps|rules|tips|lessons|principles|methods)\b")),
]

TOPIC_MARKERS = re.compile(
    r"(?i)\b(now|next|first|second|third|finally|this brings us to|the next|another|but|however|so|therefore|in summary)\b"
)


def read_text(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8", errors="replace")


def sentence_split(text: str) -> list[str]:
    rough = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text).strip())
    return [s.strip() for s in rough if len(s.strip()) > 20]


def detect(text: str) -> dict:
    matches = []
    for label, pattern in ENUM_PATTERNS:
        for match in pattern.finditer(text):
            matches.append({
                "type": label,
                "match": match.group(0)[:180],
                "start": match.start(),
            })

    # Title claims are strong: "10 ways" means lock to 10 unless contradicted.
    title_counts = []
    for m in ENUM_PATTERNS[-1][1].finditer(text[:2000]):
        title_counts.append(int(m.group(1)))

    # Derive cluster hints by frequent content words and transition markers.
    words = re.findall(r"\b[a-z][a-z0-9-]{3,}\b", text.lower())
    stop = {
        "this", "that", "with", "have", "from", "they", "your", "about", "there",
        "would", "could", "should", "because", "people", "thing", "things", "make",
        "making", "project", "projects", "just", "like", "when", "what", "want",
        "going", "really", "more", "some", "them", "their", "into", "were", "then",
    }
    counts = Counter(w for w in words if w not in stop)
    keywords = [w for w, _ in counts.most_common(20)]

    marker_sentences = []
    for sent in sentence_split(text):
        if TOPIC_MARKERS.search(sent):
            marker_sentences.append(sent[:220])
        if len(marker_sentences) >= 20:
            break

    explicit = bool(matches)
    status = "enumeration-candidates-found" if explicit else "derive-clusters"
    suggested_count = title_counts[0] if title_counts else None
    if suggested_count is None and explicit:
        numeric_hits = []
        for m in matches:
            n = re.search(r"\b(\d{1,2})\b", m["match"])
            if n:
                numeric_hits.append(int(n.group(1)))
        if numeric_hits:
            suggested_count = max(numeric_hits)

    return {
        "status": status,
        "suggested_extraction_status": (
            f"[ENUMERATION_LOCKED: {suggested_count} items]" if suggested_count else
            "[ENUMERATION_LOCKED: X items]" if explicit else
            "[DERIVED_STRUCTURE: X clusters]"
        ),
        "explicit_matches": matches[:50],
        "keyword_hints": keywords,
        "topic_shift_sentence_hints": marker_sentences,
        "notes": [
            "Use this output as telemetry only.",
            "If explicit enumeration is present, preserve the speaker's sequence.",
            "If not, derive clusters from topic shifts and repeated concepts."
        ]
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect transcript structure candidates.")
    parser.add_argument("input", help="Input transcript path, or '-' for stdin.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    try:
        result = detect(read_text(args.input))
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(result["suggested_extraction_status"])
            if result["explicit_matches"]:
                print("\nExplicit matches:")
                for item in result["explicit_matches"][:10]:
                    print(f"- {item['type']}: {item['match']}")
            print("\nKeyword hints:", ", ".join(result["keyword_hints"][:12]))
        return 0
    except Exception as exc:  # pragma: no cover
        print(f"detect-structure failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
