#!/usr/bin/env python3
"""Validate a YouTube Transcript → Obsidian Artifact output.

The validator catches structural issues an agent can fix before returning final
output. It does not judge factual quality.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = [
    "# YT-Transcription:",
    "## Visual Concept Map",
    "## Executive Summary",
    "## Deep Dive Analysis",
    "## Constructed Resources",
    "## Implementation Checklist",
    "## Appendices",
    "#### 📊 Appendix A: Capability Rubric",
    "#### 📚 Appendix B: Terminology & Definitions",
    "#### 🔗 Appendix C: Entities & References",
    "#### 🧠 Appendix D: Meta-Learning Methodology Telemetry",
    "#### 🤖 Appendix E: Instruction/Prompt Index",
]

DEEP_DIVE_FIELDS = [
    "**Audience Level:**",
    "**Frameworks:**",
    "**Core Concept:**",
    "**Mechanism:**",
    "**Strategic Implication:**",
    "**Practical Application:**",
    "**Contrast:**",
    "**Actionable Applications:**",
    "🛡️ Prepare:",
    "🔍 Recognize:",
    "🚨 Execute:",
    "📐 Framework:",
    "**Example**",
]


def parse_frontmatter(text: str) -> tuple[dict[str, str], str | None]:
    if not text.startswith("---\n"):
        return {}, "Artifact must start with raw YAML frontmatter at character 1."
    end = text.find("\n---", 4)
    if end == -1:
        return {}, "Closing YAML frontmatter delimiter not found."
    raw = text[4:end].strip()
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip() or line.startswith("  ") or line.startswith("- "):
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            data[key.strip()] = val.strip()
    return data, None


def check_order(text: str) -> list[str]:
    errors = []
    last = -1
    for section in REQUIRED_SECTIONS:
        pos = text.find(section)
        if pos == -1:
            errors.append(f"Missing required section: {section}")
        elif pos < last:
            errors.append(f"Section out of order: {section}")
        else:
            last = pos
    return errors


def section_text(text: str, start_heading: str, next_heading_prefix: str = "\n## ") -> str:
    start = text.find(start_heading)
    if start == -1:
        return ""
    next_pos = text.find(next_heading_prefix, start + len(start_heading))
    if next_pos == -1:
        return text[start:]
    return text[start:next_pos]


def check_deep_dives(text: str, strict: bool) -> list[str]:
    errors = []
    deep = section_text(text, "## Deep Dive Analysis")
    sections = re.split(r"\n####\s+", deep)
    dive_sections = [s for s in sections[1:] if s.strip()]
    if not dive_sections:
        errors.append("No deep dive `####` sections found.")
        return errors
    for idx, sec in enumerate(dive_sections, 1):
        title = sec.splitlines()[0][:100] if sec.splitlines() else f"section {idx}"
        missing = [field for field in DEEP_DIVE_FIELDS if field not in sec]
        if missing:
            message = f"Deep dive {idx} missing fields: {', '.join(missing)}"
            if strict or len(missing) > 3:
                errors.append(message)
        if not re.search(r"`\[(Reduces Friction|Deepens Thinking|Improves Context|Accelerates Execution|Enhances Reliability|Improves Transferability|Reduces Cognitive Load|Enables Automation)\]`", sec):
            errors.append(f"Deep dive {idx} lacks a benefit tag in backticks: {title}")
    return errors


def check_labels(text: str) -> list[str]:
    warnings = []
    labels = ["[VERBATIM]", "[DESCRIBED]", "[CONSTRUCTED]", "[INFERRED]"]
    if not any(label in text for label in labels):
        warnings.append("No provenance labels found.")
    return warnings


def check_local_filenames(text: str) -> list[str]:
    warnings = []
    # Check markdown local links excluding anchors, URLs, and Obsidian wikilinks.
    for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
        target = match.group(1).strip()
        if re.match(r"^[a-z]+://", target) or target.startswith("#"):
            continue
        filename = Path(target).name
        if filename and not re.match(r"^[a-z0-9][a-z0-9-]*(?:\.[a-z0-9]+)?$", filename):
            warnings.append(f"Local referenced filename is not lowercase-hyphens-only: {target}")
    return warnings


def validate(text: str, strict: bool = False) -> dict:
    errors = []
    warnings = []

    fm, fm_error = parse_frontmatter(text)
    if fm_error:
        errors.append(fm_error)

    if "tags:" not in text[:1000]:
        errors.append("YAML frontmatter must include tags.")
    if "yt-transcript" not in text[:1200] or "knowledge-artifact" not in text[:1200]:
        errors.append("Frontmatter tags must include yt-transcript and knowledge-artifact.")

    errors.extend(check_order(text))

    if "[ENUMERATION_LOCKED:" not in text and "[DERIVED_STRUCTURE:" not in text:
        errors.append("Executive Summary must include extraction status lock or derived structure marker.")

    if "```mermaid" not in text:
        warnings.append("No Mermaid concept map found. Use a plain outline only when Mermaid is unreliable.")

    errors.extend(check_deep_dives(text, strict=strict))
    warnings.extend(check_labels(text))
    warnings.extend(check_local_filenames(text))

    if "[None extracted]" not in text:
        warnings.append("No `[None extracted]` markers found. This is fine only if every required subsection has content.")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "frontmatter_keys": sorted(fm.keys()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a YT transcript Obsidian artifact.")
    parser.add_argument("artifact", help="Artifact markdown file to validate.")
    parser.add_argument("--strict", action="store_true", help="Treat more missing deep-dive fields as errors.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    args = parser.parse_args()

    try:
        text = Path(args.artifact).read_text(encoding="utf-8", errors="replace")
        result = validate(text, strict=args.strict)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            status = "PASS" if result["ok"] else "FAIL"
            print(status)
            for err in result["errors"]:
                print(f"ERROR: {err}")
            for warning in result["warnings"]:
                print(f"WARNING: {warning}")
        return 0 if result["ok"] else 1
    except Exception as exc:  # pragma: no cover
        print(f"validate-artifact failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
