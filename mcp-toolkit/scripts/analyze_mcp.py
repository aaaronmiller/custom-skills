#!/usr/bin/env python3
"""Summarize MCP tool definitions from a JSON file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def find_tools(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, dict):
        if isinstance(data.get("tools"), list):
            return [tool for tool in data["tools"] if isinstance(tool, dict)]
        if isinstance(data.get("result"), dict) and isinstance(data["result"].get("tools"), list):
            return [tool for tool in data["result"]["tools"] if isinstance(tool, dict)]
    if isinstance(data, list):
        return [tool for tool in data if isinstance(tool, dict)]
    return []


def classify_tool(name: str, description: str) -> str:
    text = f"{name} {description}".lower()
    if any(word in text for word in ("delete", "remove", "destroy", "drop")):
        return "destructive"
    if any(word in text for word in ("create", "update", "write", "set", "patch", "send")):
        return "mutating"
    return "read-only"


def schema_fields(tool: dict[str, Any]) -> list[str]:
    schema = tool.get("inputSchema") or tool.get("input_schema") or {}
    props = schema.get("properties") if isinstance(schema, dict) else None
    if not isinstance(props, dict):
        return []
    required = set(schema.get("required") or [])
    return [f"{name}{'*' if name in required else ''}" for name in props]


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize MCP tools from a JSON definition.")
    parser.add_argument("source", help="Path to an MCP tools JSON file")
    args = parser.parse_args()

    path = Path(args.source)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    try:
        tools = find_tools(load_json(path))
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in {path}: {exc}", file=sys.stderr)
        return 2
    if not tools:
        print("error: no tools found in JSON", file=sys.stderr)
        return 1

    grouped: dict[str, list[dict[str, Any]]] = {"read-only": [], "mutating": [], "destructive": []}
    for tool in tools:
        name = str(tool.get("name", "unnamed"))
        desc = str(tool.get("description", ""))
        grouped[classify_tool(name, desc)].append(tool)

    print(f"tools: {len(tools)}")
    for group, items in grouped.items():
        if not items:
            continue
        print(f"\n## {group}")
        for tool in items:
            name = str(tool.get("name", "unnamed"))
            desc = str(tool.get("description", "")).strip()
            fields = ", ".join(schema_fields(tool)) or "no parameters"
            print(f"- {name}: {desc} [{fields}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
