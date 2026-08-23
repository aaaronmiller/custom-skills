#!/usr/bin/env python3
"""Install the bounded Living Documents contract into harness rule files."""
from __future__ import annotations

import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()
TEMPLATE = (
    Path(__file__).resolve().parents[1]
    / "references"
    / "harness-rules.md"
)
START = "<!-- BEGIN LIVING DOCUMENTS MANAGED CONTRACT -->"
END = "<!-- END LIVING DOCUMENTS MANAGED CONTRACT -->"
LEGACY_HEADING = "## LIVING DOCUMENTS"
DEFAULT_TARGETS = (
    HOME / ".claude" / "CLAUDE.md",
    HOME / ".codex" / "AGENTS.md",
)


def resolved_target(path: Path) -> Path:
    return path.resolve() if path.is_symlink() else path


def merge_rules(existing: str, block: str) -> str:
    start = existing.find(START)
    end = existing.find(END)
    if (start == -1) != (end == -1):
        raise ValueError("found only one Living Documents managed marker")
    if start != -1:
        if existing.find(START, start + len(START)) != -1:
            raise ValueError("found multiple Living Documents managed blocks")
        end += len(END)
        return existing[:start] + block.rstrip() + existing[end:]
    legacy = existing.find(LEGACY_HEADING)
    if legacy != -1:
        next_heading = existing.find("\n## ", legacy + len(LEGACY_HEADING))
        end = len(existing) if next_heading == -1 else next_heading + 1
        suffix = existing[end:]
        separator = "\n\n" if suffix and not block.endswith("\n\n") else ""
        return existing[:legacy] + block.rstrip() + separator + suffix
    separator = "" if not existing or existing.endswith("\n\n") else "\n"
    return existing.rstrip() + separator + "\n" + block.rstrip() + "\n"


def backup(path: Path) -> Path | None:
    if not path.exists():
        return None
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = path.with_name(f"{path.name}.living-documents-rules-{stamp}.bak")
    shutil.copy2(path, target)
    return target


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.living-documents-rules.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument(
        "--target",
        action="append",
        type=Path,
        help="Rule file to update. Repeat for multiple files.",
    )
    args = parser.parse_args()

    block = TEMPLATE.read_text(encoding="utf-8")
    requested = tuple(args.target or DEFAULT_TARGETS)
    targets: list[Path] = []
    seen: set[Path] = set()
    for requested_path in requested:
        target = resolved_target(requested_path.expanduser())
        if target not in seen:
            seen.add(target)
            targets.append(target)

    for target in targets:
        existing = target.read_text(encoding="utf-8") if target.exists() else ""
        merged = merge_rules(existing, block)
        if args.apply and merged != existing:
            backup(target)
            atomic_write(target, merged)
        print(f"{'applied' if args.apply else 'preview'}\t{target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
