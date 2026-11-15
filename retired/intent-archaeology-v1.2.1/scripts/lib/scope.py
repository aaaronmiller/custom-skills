"""ScopeSpec: composable scope for intent-archaeology Phase 5+ runs.

Read references/scope_selectors.md for the full spec. This module is the
canonical implementation: CLI scripts parse args into ScopeSpec, which
compiles to a list of `cass` CLI invocations.

Usage:
    from lib.scope import ScopeSpec, parse_args
    scope = parse_args(["--since", "7d", "--projects", "foo,bar", "--agent", "claude"])
    for cmd in scope.cass_commands():
        print(" ".join(cmd))
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shlex
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

# Known harnesses for documentation. Not a closed vocabulary — cass supports
# many more connectors that we discover dynamically at runtime. When the user
# passes an agent not in this set, we pass it through to cass which validates
# it. This list exists for CLI help text and error messages, not for gatekeeping.
SUPPORTED_AGENTS = {"claude", "codex", "cursor", "gemini", "aider", "chatgpt"}

INTENT_TYPES = {
    "question", "command", "correction", "scope-cut", "scope-add",
    "spec-reference", "bug-report", "constraint", "preference", "noise",
}

DEFAULT_SINCE_DAYS = 30


@dataclass
class ScopeSpec:
    """Composable scope for a Phase 5+ run.

    Every field is optional. Defaults: --since 30d, all projects, all agents.
    See references/scope_selectors.md.
    """
    since: str | None = None              # e.g. "7d"
    since_days: int | None = None         # alternative: integer days
    today: bool = False
    date_from: str | None = None          # ISO date "2025-01-01"
    date_to: str | None = None
    projects: list[str] = field(default_factory=list)   # short names or paths
    project_dirs: list[str] = field(default_factory=list)
    agents: list[str] = field(default_factory=list)     # subset of SUPPORTED_AGENTS
    types: list[str] = field(default_factory=list)      # subset of INTENT_TYPES
    matches: str | None = None            # Python regex
    session: str | None = None            # absolute path to single session
    limit: int | None = None
    ordering: str = "newest-first"        # "newest-first" or "oldest-first"
    include_tools: bool = False

    def __post_init__(self) -> None:
        # Warn on unknown agents (not a hard error — cass validates at runtime)
        if self.agents:
            unknown = set(self.agents) - SUPPORTED_AGENTS
            if unknown:
                import sys as _sys
                print(f"WARN: unknown agent(s) {unknown}. "
                      f"cass may not support them. Known: {sorted(SUPPORTED_AGENTS)}",
                      file=_sys.stderr)
        bad_types = set(self.types) - INTENT_TYPES
        if bad_types:
            raise ValueError(
                f"Unsupported intent type(s): {bad_types}. "
                f"Supported: {sorted(INTENT_TYPES)}"
            )
        if self.ordering not in {"newest-first", "oldest-first"}:
            raise ValueError(f"ordering must be newest-first or oldest-first, got {self.ordering!r}")

    def effective_since_days(self) -> int:
        """Resolve to an integer day count for cass --days / --since."""
        if self.today:
            return 1
        if self.since_days is not None:
            return self.since_days
        if self.since:
            m = re.fullmatch(r"(\d+)d", self.since)
            if not m:
                raise ValueError(f"Invalid --since format: {self.since!r}. Use Nd (e.g. 7d).")
            return int(m.group(1))
        if self.date_from:
            # Compute days from date_from to today
            d = datetime.fromisoformat(self.date_from).replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            return max(1, (now - d).days)
        return DEFAULT_SINCE_DAYS

    def is_default(self) -> bool:
        """True if no scope flags were set (uses default --since 30d)."""
        return not any([
            self.since, self.since_days, self.today, self.date_from, self.date_to,
            self.projects, self.project_dirs, self.agents, self.types,
            self.matches, self.session, self.limit,
        ]) and self.ordering == "newest-first"

    def description(self) -> str:
        """Human-readable scope description for logging and reporting."""
        parts = []
        if self.session:
            parts.append(f"session={self.session}")
            return "Scope: " + ", ".join(parts)
        if self.today:
            parts.append("today")
        elif self.date_from or self.date_to:
            parts.append(f"from={self.date_from or 'beginning'}")
            if self.date_to:
                parts.append(f"to={self.date_to}")
        elif self.since:
            parts.append(f"since={self.since}")
        elif self.since_days is not None:
            parts.append(f"since={self.since_days}d")
        else:
            parts.append(f"since={DEFAULT_SINCE_DAYS}d (default)")
        parts.append("projects=" + (",".join(self.projects) if self.projects else "all"))
        parts.append("agents=" + (",".join(self.agents) if self.agents else "all"))
        if self.types:
            parts.append("types=" + ",".join(self.types))
        if self.matches:
            parts.append(f"matches=/{self.matches}/")
        if self.limit:
            parts.append(f"limit={self.limit}")
        parts.append(f"ordering={self.ordering}")
        if self.include_tools:
            parts.append("include_tools")
        return "Scope: " + ", ".join(parts)

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)

    def hash(self) -> str:
        return hashlib.sha256(self.to_json().encode()).hexdigest()

    # ----- cass command compilation -----

    def cass_timeline_command(self, workspace: str) -> list[str]:
        """Enumerate sessions for a workspace via cass search (not timeline).
        
        cass timeline does not support --workspace, so we use cass search with
        an empty query and workspace filter, then deduplicate by source_path
        in the caller via deduplicate_sessions().
        """
        cmd = ["cass", "search", "", "--workspace", workspace,
               "--fields", "minimal", "--json"]
        days = self.effective_since_days()
        if days:
            cmd.extend(["--days", str(days)])
        if self.agents:
            cmd.extend(["--agent", self.agents[0]])
        if self.limit:
            cmd.extend(["--limit", str(self.limit)])
        return cmd


def deduplicate_sessions(data: dict) -> list[dict]:
    """Deduplicate cass search results by source_path to get unique sessions.
    
    cass search returns individual turns (each with source_path + line_number).
    This function collapses them into unique sessions, keeping the earliest
    line_number as creation proxy and the first agent encountered.
    
    Returns list of dicts with keys: source_path, agent, line_number.
    """
    hits = data.get("hits", [])
    seen: dict[str, dict] = {}
    for h in hits:
        sp = h.get("source_path")
        if not sp:
            continue
        if sp not in seen:
            seen[sp] = {
                "source_path": sp,
                "agent": h.get("agent", "unknown"),
                "line_number": h.get("line_number", 1),
            }
    sessions = list(seen.values())
    sessions.sort(key=lambda s: s.get("line_number", 0), reverse=True)
    return sessions

    def cass_export_command(self, session_path: str) -> list[str]:
        """cass export for one session. Returns argv list."""
        cmd = ["cass", "export", session_path, "--format", "json"]
        return cmd

    def cass_export_with_tools_command(self, session_path: str) -> list[str]:
        """cass export --include-tools for one session. Separate invocation."""
        return ["cass", "export", session_path, "--include-tools"]

    def cass_view_command(self, session_path: str, line: int, context: int = 3) -> list[str]:
        """cass view for one line. Path is positional."""
        return ["cass", "view", session_path, "-n", str(line), "-C", str(context), "--json"]

    def cass_expand_command(self, session_path: str, line: int, context: int = 3) -> list[str]:
        """cass expand. Path positional, --line (not -n)."""
        return ["cass", "expand", session_path, "--line", str(line), "-C", str(context), "--json"]

    def cass_search_command(self, query: str, fields: str = "full") -> list[str]:
        """cass search for Phase F (cited evidence). Not for Phase C enumeration."""
        cmd = ["cass", "search", query, "--fields", fields, "--json"]
        if self.agents:
            # cass takes one --agent per invocation; caller fans out
            if len(self.agents) != 1:
                raise ValueError("cass_search_command supports one agent; fan out in caller")
            cmd.extend(["--agent", self.agents[0]])
        days = self.effective_since_days()
        if days:
            cmd.extend(["--days", str(days)])
        if self.limit:
            cmd.extend(["--limit", str(self.limit)])
        return cmd

    def cass_session_export_commands(self, session_path: str) -> list[list[str]]:
        """All cass commands to fully export one session. May be 1 or 2 invocations."""
        cmds = [self.cass_export_command(session_path)]
        if self.include_tools:
            cmds.append(self.cass_export_with_tools_command(session_path))
        return cmds


def add_scope_args(parser: argparse.ArgumentParser) -> None:
    """Add scope flags to an argparse parser. All optional."""
    g = parser.add_argument_group("scope (composable; default is --since 30d, all projects, all agents)")
    g.add_argument("--since", help="Relative time filter, e.g. '7d', '30d' (default: 30d)")
    g.add_argument("--days", dest="since_days", type=int, help="Alternative to --since: integer days")
    g.add_argument("--today", action="store_true", help="Today only (mutually exclusive with --since/--from/--to)")
    g.add_argument("--from", dest="date_from", help="Absolute start date ISO format (e.g. 2025-01-01)")
    g.add_argument("--to", dest="date_to", help="Absolute end date ISO format")
    g.add_argument("--projects", help="Comma-separated project short names or paths")
    g.add_argument("--project-dir", action="append", dest="project_dirs", default=[], help="Project directory (can be repeated)")
    g.add_argument("--agent", help=f"Comma-separated agent filter: {sorted(SUPPORTED_AGENTS)}")
    g.add_argument("--type", dest="types", help=f"Comma-separated intent type filter (post-distillation): {sorted(INTENT_TYPES)}")
    g.add_argument("--matches", help="Python regex applied to prompt text (case-insensitive)")
    g.add_argument("--session", help="Single session JSONL path (overrides all other scope dimensions)")
    g.add_argument("--limit", type=int, help="Maximum prompts to extract (Phase C) or return (Phase F)")
    g.add_argument("--ordering", choices=["newest-first", "oldest-first"], default="newest-first", help="Sort direction (default: newest-first)")
    g.add_argument("--include-tools", action="store_true", help="Also run cass export --include-tools per session")


def parse_args(args: list[str] | None = None) -> ScopeSpec:
    """Parse scope args from a list. Returns ScopeSpec."""
    parser = argparse.ArgumentParser(add_help=False)
    add_scope_args(parser)
    ns = parser.parse_args(args)

    agents = [a.strip() for a in ns.agent.split(",")] if ns.agent else []
    types = [t.strip() for t in ns.types.split(",")] if ns.types else []
    projects = [p.strip() for p in ns.projects.split(",")] if ns.projects else []

    return ScopeSpec(
        since=ns.since,
        since_days=ns.since_days,
        today=ns.today,
        date_from=ns.date_from,
        date_to=ns.date_to,
        projects=projects,
        project_dirs=ns.project_dirs,
        agents=agents,
        types=types,
        matches=ns.matches,
        session=ns.session,
        limit=ns.limit,
        ordering=ns.ordering,
        include_tools=ns.include_tools,
    )


def run_cass(argv: list[str]) -> dict | list:
    """Run a cass command and parse JSON output. Raises on failure."""
    result = subprocess.run(argv, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)
