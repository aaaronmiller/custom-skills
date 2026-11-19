"""Shared constants and JSONL helpers for version-idea-ledger. Standard library only."""
import json
import os
import re
import sys

sys.dont_write_bytecode = True

CATEGORIES = ("implemented", "to-incorporate", "duplicate", "rejected", "stretch-goal", "unknown")
DISPOSITIONS = ("keep", "archive", "removal-candidate", "pending")
FINAL_DISPOSITIONS = ("keep", "archive", "removal-candidate")
# Fields written by screen_removals.py; inventory.py clears them on every run.
SCREEN_FIELDS = ("survivor", "held", "screened", "screened_sha256", "rule_disposition")


def screen_stamp_ok(row):
    """A removal candidate may reach the judge only with a survivor stamp for its current bytes."""
    return bool(row.get("survivor")) and row.get("screened_sha256") == row.get("sha256")

# Directories never walked. They are recorded as skipped in the run record, not as files.
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache", ".ruff_cache",
             ".mypy_cache", ".tox", ".cache", ".turbo", ".next", "htmlcov", ".omc"}

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{1,63}$")
LOC_LINE_RE = re.compile(r"^L(\d+)(?:-L?(\d+))?$")

LEDGER_ROOT_DEFAULT = os.path.expanduser("~/LIVING_DOCUMENTS/projects")


def ledger_dir(dossier):
    """Where a family's ledgers live, so a rerun finds them: <dossier>/ledgers/."""
    return os.path.join(dossier, "ledgers")


def read_jsonl(path):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{n}: invalid JSON: {exc}")
    return rows


def write_jsonl(path, rows):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    os.replace(tmp, path)


def norm_ws(s):
    return re.sub(r"\s+", " ", s or "").strip()
