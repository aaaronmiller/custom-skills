"""Shared helpers for the intent-archaeology pipeline.

Everything derived is recomputable. Nothing here writes to the human tree.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PIPELINE_VERSION = "0.1.0"

HOME = Path.home()
BASE = Path(os.environ.get("INTENT_ARCH_HOME", HOME / ".intent-archaeology"))
DB_PATH = BASE / "archaeology.db"
DERIVED = BASE / "derived"      # any rebuild may delete this wholesale
HUMAN = BASE / "human"          # no script may ever write here
BATCHES = BASE / "batches"

DEFAULT_ROOTS = [HOME / "code", HOME / "code2"]

MANIFESTS = [
    "package.json", "Cargo.toml", "pyproject.toml", "setup.py", "go.mod",
    "deno.json", "deno.jsonc", "pom.xml", "build.gradle", "Gemfile",
    "composer.json", "mix.exs", "pubspec.yaml", "CMakeLists.txt",
]

SOURCE_EXT = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".rs", ".go", ".rb", ".java", ".kt",
    ".c", ".h", ".cpp", ".hpp", ".cs", ".swift", ".ex", ".exs", ".dart",
    ".svelte", ".vue", ".php", ".scala", ".zig", ".lua", ".sh",
}

SKIP_DIRS = {
    ".git", "node_modules", "target", "dist", "build", "__pycache__",
    ".venv", "venv", ".next", ".nuxt", "vendor", ".cargo", "site-packages",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "coverage", ".turbo",
}

SPEC_PATTERNS = [
    (re.compile(r"(^|/)prd[^/]*\.md$", re.I), "prd"),
    (re.compile(r"(^|/)requirements?[^/]*\.md$", re.I), "requirements"),
    (re.compile(r"(^|/)design[^/]*\.md$", re.I), "design"),
    (re.compile(r"(^|/)plans?[^/]*\.md$", re.I), "plan"),
    (re.compile(r"(^|/)spec[^/]*\.md$", re.I), "spec"),
    (re.compile(r"(^|/)tasks[^/]*\.md$", re.I), "tasks"),
    (re.compile(r"(^|/)constitution\.md$", re.I), "constitution"),
    (re.compile(r"RAISON_DETRE\.md$"), "livingdoc"),
]

# Redaction runs before anything is stored. Order matters: longest first.
SECRET_PATTERNS = [
    ("anthropic_key", re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")),
    ("openai_key", re.compile(r"sk-[A-Za-z0-9]{32,}")),
    ("aws_key", re.compile(r"AKIA[A-Z0-9]{16}")),
    ("google_key", re.compile(r"AIza[A-Za-z0-9_\-]{35}")),
    ("github_pat", re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}")),
    ("slack_token", re.compile(r"xox[baprs]-[A-Za-z0-9\-]{10,}")),
    ("jwt", re.compile(r"eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}")),
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("conn_string", re.compile(r"\b[a-z][a-z0-9+.\-]*://[^\s:@/]+:[^\s:@/]+@[^\s/]+")),
    ("assigned_secret", re.compile(
        r"\b(?:API[_-]?KEY|SECRET|PASSWORD|PASSWD|TOKEN|PRIVATE[_-]?KEY|ACCESS[_-]?KEY)"
        r"\s*[=:]\s*[\"']?[^\s\"'\n]{6,}", re.I)),
]

APPROVAL_TURNS = {
    "y", "yes", "yeah", "yep", "ok", "okay", "k", "go", "go on", "continue",
    "proceed", "do it", "sure", "n", "no", "stop", "next", "sounds good",
    "looks good", "lgtm", "thanks", "ty", "perfect", "great",
}

SLASH_RE = re.compile(r"<command-name>\s*([^<]+?)\s*</command-name>", re.I)
SLASH_ARGS_RE = re.compile(r"<command-args>\s*(.*?)\s*</command-args>", re.I | re.S)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def slug(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", str(text)).strip("-").lower()
    return s[:80] or "unnamed"


def sha(*parts: str, n: int = 12) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(str(p).encode("utf-8", "replace"))
        h.update(b"\x00")
    return h.hexdigest()[:n]


def redact(text: str) -> tuple[str, list[str]]:
    """Redact before storage. Returns (clean_text, pattern_ids_hit)."""
    if not text:
        return text or "", []
    hits: list[str] = []
    for name, pat in SECRET_PATTERNS:
        if pat.search(text):
            hits.append(name)
            text = pat.sub(f"[REDACTED:{name}]", text)
    return text, hits


def connect() -> sqlite3.Connection:
    BASE.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> sqlite3.Connection:
    for d in (BASE, DERIVED, HUMAN, BATCHES):
        d.mkdir(parents=True, exist_ok=True)
    conn = connect()
    schema = (Path(__file__).parent / "schema.sql").read_text()
    conn.executescript(schema)
    conn.execute(
        "INSERT OR REPLACE INTO meta(key,value) VALUES('pipeline_version',?)",
        (PIPELINE_VERSION,),
    )
    conn.commit()
    return conn


def log(conn: sqlite3.Connection, phase: str, status: str, detail: str = "") -> None:
    conn.execute(
        "INSERT INTO run_log(ts,phase,status,detail) VALUES(?,?,?,?)",
        (now(), phase, status, detail),
    )
    conn.commit()


def observe(conn: sqlite3.Connection, kind: str, detail: str,
            event_ids: list[str] | None = None, tranche: int | None = None) -> None:
    """Append-only. Observations never change behaviour mid-run."""
    conn.execute(
        "INSERT INTO observation(ts,kind,detail,event_ids,tranche,pipeline_version)"
        " VALUES(?,?,?,?,?,?)",
        (now(), kind, detail, json.dumps(event_ids or []), tranche, PIPELINE_VERSION),
    )


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 60) -> tuple[int, str, str]:
    try:
        p = subprocess.run(
            cmd, cwd=str(cwd) if cwd else None, capture_output=True,
            text=True, timeout=timeout,
        )
        return p.returncode, p.stdout, p.stderr
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as exc:
        return 1, "", str(exc)


def have(binary: str) -> bool:
    return shutil.which(binary) is not None


def cass_json(args: list[str]) -> object | None:
    """Call cass in robot mode. Never call bare cass; it opens a TUI."""
    if not have("cass"):
        return None
    code, out, _ = run(["cass", *args], timeout=180)
    if code != 0 or not out.strip():
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        rows = []
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("{"):
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return rows or None


def git(path: Path, *args: str) -> str | None:
    code, out, _ = run(["git", "-C", str(path), *args])
    return out.strip() if code == 0 and out.strip() else None


def iter_jsonl(path: Path):
    """Yield (line_number, obj) for a JSONL session file. Tolerates junk lines."""
    try:
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            for i, line in enumerate(fh, start=1):
                line = line.strip()
                if not line or line[0] != "{":
                    continue
                try:
                    yield i, json.loads(line)
                except json.JSONDecodeError:
                    continue
    except OSError:
        return


def extract_text(msg: object) -> str:
    """Pull plain text out of the several content shapes harnesses use."""
    if msg is None:
        return ""
    if isinstance(msg, str):
        return msg
    if isinstance(msg, dict):
        content = msg.get("content", msg.get("text", ""))
        return extract_text(content)
    if isinstance(msg, list):
        parts = []
        for block in msg:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                if block.get("type") in (None, "text") and block.get("text"):
                    parts.append(str(block["text"]))
        return "\n".join(parts)
    return ""


def is_approval(text: str) -> bool:
    t = text.strip().lower().rstrip(".!")
    return len(t) <= 16 and t in APPROVAL_TURNS


def die(msg: str, code: int = 1):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def report(title: str, rows: list[tuple]) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    if not rows:
        print("(none)")
        return
    width = max(len(str(r[0])) for r in rows)
    for r in rows:
        print(f"  {str(r[0]).ljust(width)}  {r[1]}")
