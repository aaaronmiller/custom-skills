#!/usr/bin/env python3
"""Five structural checks on a rules file. Each derives from a real defect.

These are mechanical. They do not judge whether a rule is good, only whether it
is written in a form that can be followed. Every check below found something in
the 2026-08-22 audit of a 755-line CLAUDE.md.

  DUPLICATE    The same rule stated twice will drift, and the reader obeys the
               statement it met first. Found: a blocking-decision limit written
               once as a ceiling and once as a quota, quota first. 28% of replies
               ended in an unnecessary decision menu.

  QUOTA        A bare cardinal reads as a target. "One X per reply" is received
               as an instruction to produce one. Only "at most", "up to" or "no
               more than" transmits a maximum, and the zero case must be named.

  UNTRIGGERED  A rule describing the SHAPE of an output, left as a bare
               imperative, acquires the power to CREATE that output. Question
               formatting rules manufacture questions.

  UNOWNED      A decision constrained from several sections gets reassembled
               from fragments, differently each time. This needs no
               contradiction to cause a misread: an external auditor misread
               three of four rules in a file that contained none.

  IMMUNISED    A section instructing the reader to preserve it will outlive the
               policy it depends on. Found: a section carrying a preserve clause
               named a model as the capability floor four days after another
               section demoted that model.

Usage:
    audit_rules_file.py <rules-file.md> [--json]

Exit status is non-zero when any finding exists, so this can gate a commit.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

# Topics whose ownership matters. Each maps to the patterns that constrain it.
DECISIONS = {
    "ask-versus-act": r"\b(ask only|never ask|default to action|before asking|do not ask|confirm first)\b",
    "reply length": r"\b(at most \d+ lines|three-line|status block|proportional to)\b",
    "blocking decisions": r"\bblocking (decision|question)\b",
    "scope of change": r"\b(smallest safe change|do not refactor|broaden scope|narrow, widen)\b",
    "evidence for completion": r"\b(never claim completion|verified|unverified|evidence)\b",
}

QUOTA = re.compile(
    r"(?<!at most )(?<!up to )(?<!no more than )(?<!maximum )"
    r"\b(one|two|three|1|2|3)\s+(blocking|decision|question|line|option|item|reply)",
    re.I,
)
IMMUNISE = re.compile(
    r"preserve if|do not remove this|keep this section|do not delete this section", re.I
)
# A HOW rule: describes the shape of an output. Safe only if a trigger precedes it.
HOW_MARKER = re.compile(
    r"\b(format it|must be (?:formatted|shaped)|use the exact packet|render(?:s|ed)? as|"
    r"every question must|the reply (?:must|should) (?:open|contain|end))\b", re.I
)
TRIGGER = re.compile(r"\b(when|if|whenever|before|after|once)\b", re.I)


def sections(text: str) -> list[tuple[int, str, str]]:
    lines = text.split("\n")
    heads = [(i, l.lstrip("# ").strip()) for i, l in enumerate(lines)
             if re.match(r"^##\s", l)]
    heads.append((len(lines), "(EOF)"))
    out = []
    for k in range(len(heads) - 1):
        start, name = heads[k]
        end = heads[k + 1][0]
        out.append((start + 1, name, "\n".join(lines[start + 1:end])))
    return out


def audit(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.split("\n")
    secs = sections(text)
    findings: dict[str, list] = defaultdict(list)

    # UNOWNED / DUPLICATE — which sections constrain each decision
    for topic, pattern in DECISIONS.items():
        rx = re.compile(pattern, re.I)
        owners = [(ln, name) for ln, name, body in secs if rx.search(body)]
        if len(owners) > 1:
            findings["unowned"].append({
                "decision": topic,
                "sections": [n for _, n in owners],
                "count": len(owners),
            })

    # QUOTA — bare cardinals next to a countable output noun
    for i, line in enumerate(lines, 1):
        if QUOTA.search(line) and not re.search(r"at most|up to|no more than|maximum", line, re.I):
            findings["quota"].append({"line": i, "text": line.strip()[:120]})

    # IMMUNISED — self-preservation language
    for i, line in enumerate(lines, 1):
        if IMMUNISE.search(line):
            findings["immunised"].append({"line": i, "text": line.strip()[:120]})

    # UNTRIGGERED — HOW rules with no condition in the surrounding two lines
    for i, line in enumerate(lines, 1):
        if not HOW_MARKER.search(line):
            continue
        window = " ".join(lines[max(0, i - 3):i + 1])
        if not TRIGGER.search(window):
            findings["untriggered"].append({"line": i, "text": line.strip()[:120]})

    # DUPLICATE — near-identical sentences across different sections
    seen: dict[str, tuple[int, str]] = {}
    for ln, name, body in secs:
        for raw in re.split(r"(?<=[.!?])\s+", body):
            s = re.sub(r"[^a-z0-9 ]", "", raw.lower()).strip()
            s = re.sub(r"\s+", " ", s)
            if len(s.split()) < 6:
                continue
            if s in seen and seen[s][1] != name:
                findings["duplicate"].append({
                    "text": raw.strip()[:110],
                    "sections": [seen[s][1], name],
                })
            else:
                seen[s] = (ln, name)

    return {
        "file": str(path),
        "lines": len(lines),
        "chars": len(text),
        "sections": len(secs),
        "findings": {k: v for k, v in findings.items()},
        "total_findings": sum(len(v) for v in findings.values()),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("rules_file")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    path = Path(args.rules_file).expanduser()
    if not path.is_file():
        print(f"no such file: {path}", file=sys.stderr)
        return 2

    result = audit(path)
    if args.json:
        print(json.dumps(result, indent=2))
        return 1 if result["total_findings"] else 0

    print(f"{result['file']}")
    print(f"{result['lines']} lines, {result['chars']:,} chars, "
          f"{result['sections']} sections\n")

    f = result["findings"]
    labels = {
        "duplicate": "DUPLICATE — same rule in two sections; they will drift",
        "quota": "QUOTA — bare cardinal reads as a target, not a ceiling",
        "untriggered": "UNTRIGGERED — a HOW rule that can create what it formats",
        "unowned": "UNOWNED — one decision constrained from several sections",
        "immunised": "IMMUNISED — a section that resists its own revision",
    }
    for key, label in labels.items():
        items = f.get(key, [])
        print(f"== {label} ({len(items)}) ==")
        if not items:
            print("   none")
        for it in items[:12]:
            if key == "unowned":
                print(f"   {it['decision']}: {it['count']} sections "
                      f"-> {', '.join(it['sections'])}")
            elif key == "duplicate":
                print(f"   {' / '.join(it['sections'])}: {it['text']}")
            else:
                print(f"   line {it['line']}: {it['text']}")
        print()

    print(f"total findings: {result['total_findings']}")
    return 1 if result["total_findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
