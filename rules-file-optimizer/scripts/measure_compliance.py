#!/usr/bin/env python3
"""Measure whether a rules file is actually being followed.

A rules file cannot be judged by reading it. The failure mode this skill exists
to fix is a file that reads well and is not obeyed, so the first step is always
a measurement against a real session transcript.

The unit of measurement is the **terminal reply**: the last assistant text block
before a genuine user turn. Getting this wrong invalidates everything downstream.
Measured on session 9ac1384d, counting every assistant message gave a median of
107 characters, which reads as excellent concision. Counting only terminal
replies gave 2,958. Same data, 27x apart, purely from the definition of the unit
-- most assistant messages are one-line preambles before a tool call, not
replies to anyone.

Usage:
    measure_compliance.py <transcript.jsonl> [...]        human-readable
    measure_compliance.py <transcript.jsonl> --json       machine-readable
    measure_compliance.py <dir>                           every .jsonl beneath it

Transcripts live under ~/.claude/projects/<slugified-cwd>/<session-uuid>.jsonl.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

# A reply that opens with the status block. Tolerates bold markers and leading
# whitespace so a cosmetic change does not read as a compliance failure.
STATUS_BLOCK = re.compile(r'^\s*(?:\*\*)?DONE\s*(?:\*\*)?\s*:', re.I)

# Endings that indicate the reply handed a decision back to the operator. This
# matches on shape, not intent, so the result is an UPPER BOUND on the defect: a
# reply that genuinely needed a decision scores the same as one that manufactured
# a menu. Read a sample before treating the number as the defect rate.
MENU_TAIL = re.compile(
    r'\*\*Question|\*\*Default if|Want me to\b|Say go\b|^\s*-\s*\*\*[A-D]\s*[—-]',
    re.M,
)

# Content the harness injects. These are not the operator speaking, and counting
# them as user turns splits one reply into several.
INJECTED_PREFIXES = ("<", "[Request interrupted", "Caveat:", "<local-command")

LINE_BUDGET_CHARS = 700  # ~10 lines at typical terminal width


def blocks_to_text(content) -> str:
    """Assistant content is either a string or a list of typed blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            b.get("text", "")
            for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        )
    return ""


def load_turns(path: Path) -> list[tuple[str, str]]:
    turns: list[tuple[str, str]] = []
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            message = obj.get("message") or {}
            role = message.get("role")
            if role not in ("user", "assistant"):
                continue
            text = blocks_to_text(message.get("content"))
            if text.strip():
                turns.append((role, text))
    return turns


def terminal_replies(turns: list[tuple[str, str]]) -> list[str]:
    """The last assistant text before each genuine user turn."""
    out: list[str] = []
    for i, (role, text) in enumerate(turns):
        if role != "user":
            continue
        if text.lstrip().startswith(INJECTED_PREFIXES):
            continue
        for j in range(i - 1, -1, -1):
            if turns[j][0] == "assistant":
                out.append(turns[j][1])
                break
            if turns[j][0] == "user":
                break  # consecutive user turns; no reply between them
    return out


def measure(replies: list[str]) -> dict:
    if not replies:
        return {"replies": 0}
    lengths = sorted(len(r) for r in replies)
    n = len(replies)
    with_status = sum(1 for r in replies if STATUS_BLOCK.match(r))
    over_3k = sum(1 for l in lengths if l > 3000)
    over_budget = sum(1 for l in lengths if l > LINE_BUDGET_CHARS)
    menus = sum(1 for r in replies if MENU_TAIL.search(r[-900:]))
    return {
        "replies": n,
        "median_chars": lengths[n // 2],
        "mean_chars": int(statistics.fmean(lengths)),
        "max_chars": lengths[-1],
        "status_block_pct": round(100 * with_status / n),
        "over_3000_pct": round(100 * over_3k / n),
        "over_line_budget_pct": round(100 * over_budget / n),
        "ends_in_menu_pct": round(100 * menus / n),
    }


def collect(paths: list[str]) -> list[Path]:
    out: list[Path] = []
    for raw in paths:
        p = Path(raw).expanduser()
        if p.is_dir():
            out.extend(sorted(p.rglob("*.jsonl")))
        elif p.is_file():
            out.append(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--min-replies", type=int, default=5,
                    help="skip transcripts with fewer terminal replies (default 5)")
    args = ap.parse_args()

    files = collect(args.paths)
    if not files:
        print("no .jsonl transcripts found", file=sys.stderr)
        return 2

    results = []
    for path in files:
        replies = terminal_replies(load_turns(path))
        stats = measure(replies)
        if stats["replies"] < args.min_replies:
            continue
        stats["transcript"] = str(path)
        results.append(stats)

    if not results:
        print(f"no transcript had at least {args.min_replies} terminal replies.\n"
              "A session with too few replies cannot support a compliance claim.",
              file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(results, indent=2))
        return 0

    for r in results:
        print(f"\n{r['transcript']}")
        print(f"  terminal replies      {r['replies']}")
        print(f"  median chars          {r['median_chars']:,}"
              f"   (10-line budget ~{LINE_BUDGET_CHARS})")
        print(f"  mean / max chars      {r['mean_chars']:,} / {r['max_chars']:,}")
        print(f"  opens with status     {r['status_block_pct']}%")
        print(f"  over 3,000 chars      {r['over_3000_pct']}%")
        print(f"  over line budget      {r['over_line_budget_pct']}%")
        print(f"  ends in a menu        {r['ends_in_menu_pct']}%  (upper bound)")

    if len(results) > 1:
        print(f"\n{len(results)} transcripts. No cross-session trend is implied: "
              "sessions differ in task mix, and a rule can look better simply "
              "because the work was shorter.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
