#!/usr/bin/env python3
"""Install idempotent Living Documents hooks for Claude Code and Codex."""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HOME = Path.home()
SCRIPT = Path(__file__).with_name("living-documents-continuity-hook.py").resolve()
CLAUDE_SETTINGS = HOME / ".claude" / "settings.json"
CODEX_HOOKS = HOME / ".codex" / "hooks.json"
EVENTS = ("SessionStart", "Stop")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def is_living_documents_handler(handler: dict[str, Any]) -> bool:
    return "living-documents-continuity-hook.py" in str(handler.get("command", ""))


def remove_existing(hooks: dict[str, Any]) -> None:
    for event in list(hooks):
        groups = hooks.get(event)
        if not isinstance(groups, list):
            continue
        kept_groups = []
        for group in groups:
            if not isinstance(group, dict):
                kept_groups.append(group)
                continue
            handlers = group.get("hooks")
            if not isinstance(handlers, list):
                kept_groups.append(group)
                continue
            kept = [
                handler
                for handler in handlers
                if not (
                    isinstance(handler, dict)
                    and is_living_documents_handler(handler)
                )
            ]
            if kept:
                kept_groups.append({**group, "hooks": kept})
        if kept_groups:
            hooks[event] = kept_groups
        else:
            hooks.pop(event, None)


def handler() -> dict[str, Any]:
    return {
        "type": "command",
        "command": f"python3 {SCRIPT} --harness-output",
        "timeout": 5,
        "async": False,
    }


def merged_document(path: Path, kind: str) -> dict[str, Any]:
    document = read_json(path)
    hooks = document.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError(f"expected hooks object: {path}")
    remove_existing(hooks)
    for event in EVENTS:
        hooks.setdefault(event, []).append({"hooks": [handler()]})
    if kind == "codex":
        # Codex does not currently support async command hooks. Omitting the
        # field avoids a configuration warning while preserving Claude support.
        for event in EVENTS:
            hooks[event][-1]["hooks"][0].pop("async", None)
    return document


def backup(path: Path) -> Path | None:
    if not path.exists():
        return None
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = path.with_name(f"{path.name}.living-documents-backup-{stamp}")
    shutil.copy2(path, target)
    return target


def atomic_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.living-documents.tmp")
    temporary.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Back up and replace the live hook configuration.",
    )
    parser.add_argument(
        "--target",
        choices=("all", "claude", "codex"),
        default="all",
    )
    args = parser.parse_args()
    targets = []
    if args.target in {"all", "claude"}:
        targets.append((CLAUDE_SETTINGS, "claude"))
    if args.target in {"all", "codex"}:
        targets.append((CODEX_HOOKS, "codex"))

    results = []
    for path, kind in targets:
        document = merged_document(path, kind)
        if args.apply:
            backup_path = backup(path)
            atomic_write(path, document)
            read_json(path)
            results.append(
                {
                    "target": kind,
                    "path": str(path),
                    "applied": True,
                    "backup": str(backup_path) if backup_path else None,
                }
            )
        else:
            results.append(
                {
                    "target": kind,
                    "path": str(path),
                    "applied": False,
                    "hooks": document.get("hooks", {}),
                }
            )
    print(json.dumps({"results": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
