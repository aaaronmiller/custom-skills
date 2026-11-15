#!/usr/bin/env python3
"""Basic validation for MCP conversion output directories."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_tools(path: Path) -> list[str]:
    data: Any = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("tools"), list):
        return [str(tool.get("name")) for tool in data["tools"] if isinstance(tool, dict) and tool.get("name")]
    if isinstance(data, dict) and isinstance(data.get("result"), dict) and isinstance(data["result"].get("tools"), list):
        return [str(tool.get("name")) for tool in data["result"]["tools"] if isinstance(tool, dict) and tool.get("name")]
    if isinstance(data, list):
        return [str(tool.get("name")) for tool in data if isinstance(tool, dict) and tool.get("name")]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an MCP conversion output directory.")
    parser.add_argument("output_dir", help="Directory containing generated wrapper files")
    parser.add_argument("--mcp", help="Original MCP tools JSON file")
    args = parser.parse_args()

    out = Path(args.output_dir)
    if not out.is_dir():
        print(f"error: output directory not found: {out}", file=sys.stderr)
        return 2

    failures: list[str] = []
    if not any((out / name).exists() for name in ("README.md", "SCRIPTS_REFERENCE.md", "SKILL.md")):
        failures.append("missing README.md, SCRIPTS_REFERENCE.md, or SKILL.md")

    text_files = [p for p in out.rglob("*") if p.is_file() and p.suffix in {".md", ".py", ".js", ".ts", ".sh"}]
    joined = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in text_files)

    github_short = "ghp" + "_"
    github_pat = "github" + "_pat" + "_"
    openai_prefix = "sk" + "-"
    if openai_prefix in joined or github_short in joined or github_pat in joined:
        failures.append("possible hardcoded secret token found")

    if args.mcp:
        tools = load_tools(Path(args.mcp))
        missing = [tool for tool in tools if tool and tool not in joined]
        if missing:
            failures.append("MCP tools not mentioned in output: " + ", ".join(missing))

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("PASS: conversion output passed basic checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
