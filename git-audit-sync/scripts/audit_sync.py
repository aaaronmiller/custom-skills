#!/usr/bin/env python3
"""
Git Audit & Sync — Scan every git repo in a directory, assess state,
and bring all repos to a clean, synced state.

Usage:
    python3 audit_sync.py <directory>
    python3 audit_sync.py <directory> --dry-run
    python3 audit_sync.py <directory> --audit-only
    python3 audit_sync.py <directory> --exclude repo1,repo2
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# ── Colours / icons ─────────────────────────────────────────────────────────
OK = "✅"
PULLED = "⏩"
PUSHED = "📤"
COMMITTED = "💾"
SYNCED = "🔄"
SKIP = "⏭️"
CONFLICT = "⚠️"
ERROR = "❌"
INFO = "ℹ️"
DRY = "🔍"


# ── Logging ─────────────────────────────────────────────────────────────────

LOG_DIR = Path.home() / "git-audit-logs"


class Report:
    """Collect per-repo results and write a final report."""

    def __init__(self, root: Path, dry_run: bool):
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.path = LOG_DIR / f"git-audit-{ts}.md"
        self.root = root
        self.dry_run = dry_run
        self.lines: list[str] = []
        self.summary: list[str] = []
        self.stats = {"clean": 0, "pulled": 0, "pushed": 0, "committed": 0,
                      "synced": 0, "conflict": 0, "error": 0, "skipped": 0}

    def add(self, repo: str, icon: str, msg: str):
        label = f"{icon} {msg}"
        self.summary.append(f"| {label} |")
        line = f"- {label}"
        self.lines.append(line)
        for key in self.stats:
            if icon in [OK, SKIP, DRY] and key == "clean":
                self.stats[key] += 1; break
            if icon == PULLED and key == "pulled":
                self.stats[key] += 1; break
            if icon == PUSHED and key == "pushed":
                self.stats[key] += 1; break
            if icon == COMMITTED and key == "committed":
                self.stats[key] += 1; break
            if icon == SYNCED and key == "synced":
                self.stats[key] += 1; break
            if icon == CONFLICT and key == "conflict":
                self.stats[key] += 1; break
            if icon == ERROR and key == "error":
                self.stats[key] += 1; break
            if icon == SKIP and key == "skipped":
                self.stats[key] += 1; break

    def write(self):
        total = sum(self.stats.values()) or 1
        ok = self.stats["clean"] + self.stats["pulled"] + self.stats["pushed"] \
             + self.stats["committed"] + self.stats["synced"]
        pct = round(ok / total * 100)
        content = [
            f"# Git Audit — {self.root}",
            f"**Run**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Mode**: {'DRY RUN' if self.dry_run else 'LIVE'}",
            "",
            "## Summary",
            f"| Stat | Count |",
            f"|------|-------|",
            f"| {OK} Clean / up-to-date | {self.stats['clean']} |",
            f"| {PULLED} Pulled | {self.stats['pulled']} |",
            f"| {PUSHED} Pushed | {self.stats['pushed']} |",
            f"| {COMMITTED} Committed + pushed | {self.stats['committed']} |",
            f"| {SYNCED} Synced (commit+push+pull) | {self.stats['synced']} |",
            f"| {CONFLICT} Conflicts | {self.stats['conflict']} |",
            f"| {ERROR} Errors | {self.stats['error']} |",
            f"| {SKIP} Skipped | {self.stats['skipped']} |",
            f"| **Health** | **{pct}%** |",
            "",
            "## Per-repo results",
        ] + self.lines
        self.path.write_text("\n".join(content) + "\n")
        print(f"\n📊 Report: {self.path}")


# ── Helpers ─────────────────────────────────────────────────────────────────

def run(cmd: list[str], cwd: Path, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run a command and return result. Works on all OS paths."""
    return subprocess.run(cmd, capture_output=True, text=True,
                          timeout=timeout, cwd=str(cwd))


def run_git(repo: Path, *args: str, timeout: int = 60) -> str:
    """Run a git command in a repo and return stdout."""
    cmd = ["git"] + list(args)
    r = run(cmd, repo, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout.strip()


def maybe_run_git(repo: Path, *args: str, timeout: int = 60) -> Optional[str]:
    """Run a git command, return stdout or None on failure."""
    cmd = ["git"] + list(args)
    r = run(cmd, repo, timeout=timeout)
    return r.stdout.strip() if r.returncode == 0 else None


def create_backup_tag(repo: Path, report: Report):
    """Create a lightweight backup tag before any write operation."""
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    repo_name = repo.name
    tag = f"git-audit-sync/backup-{ts}-{repo_name}"
    if not report.dry_run:
        r = run(["git", "tag", tag], repo)
        if r.returncode == 0:
            print(f"  📦 Backup tag: {tag}")
    else:
        print(f"  📦 Would create backup tag: {tag}")
    return tag


# ── Repo state inspection ───────────────────────────────────────────────────

class GitRepo:
    """Inspected state of a single git repo."""

    def __init__(self, path: Path):
        self.path = path
        self.name = path.name
        self.branch: str = ""
        self.has_origin: bool = False
        self.has_upstream: bool = False
        self.uncommitted: int = 0
        self.ahead: int = 0
        self.behind: int = 0
        self.has_stashed: bool = False
        self.conflict_files: list[str] = []
        self.error: Optional[str] = None

    def inspect(self):
        """Gather all state info about this repo."""
        # Check for active merge/rebase/cherry-pick/revert first
        # These would cause git operations to fail, so flag early
        GIT_LOCK_FILES = ["MERGE_HEAD", "REBASE_HEAD", "CHERRY_PICK_HEAD",
                          "REVERT_HEAD", "MERGE_MSG", "MERGE_MODE", "sequencer/todo"]
        git_dir = self.path / ".git"
        active_ops = []
        for lf in GIT_LOCK_FILES:
            if (git_dir / lf).exists():
                active_ops.append(lf.replace("_HEAD", "").replace("_MSG", " (merge)")
                                   .replace("_MODE", " (merge)").replace("sequencer/todo", "rebase (interactive)"))
        self.active_git_op = active_ops[0] if active_ops else None

        try:
            self.branch = run_git(self.path, "rev-parse", "--abbrev-ref", "HEAD",
                                  timeout=10)
        except RuntimeError as e:
            self.error = str(e)
            return

        # Remote
        origin_url = maybe_run_git(self.path, "remote", "get-url", "origin",
                                   timeout=10)
        self.has_origin = origin_url is not None

        if not self.has_origin:
            return  # No remote to compare with

        # Fetch
        try:
            run_git(self.path, "fetch", "origin", "--quiet", timeout=30)
        except RuntimeError as e:
            self.error = f"fetch failed: {e}"
            return

        # Upstream tracking
        upstream = maybe_run_git(self.path, "rev-parse", "--abbrev-ref",
                                 "--symbolic-full-name", "@{u}", timeout=10)
        self.has_upstream = upstream is not None

        if not self.has_upstream:
            return

        # Ahead / behind
        try:
            r = run_git(self.path, "rev-list", "--left-right", "--count",
                        f"{upstream}...HEAD", timeout=15)
            parts = r.split()
            self.behind = int(parts[0]) if len(parts) > 0 else 0
            self.ahead = int(parts[1]) if len(parts) > 1 else 0
        except (RuntimeError, ValueError, IndexError):
            pass

        # Uncommitted
        r = maybe_run_git(self.path, "status", "--porcelain", timeout=15)
        if r:
            self.uncommitted = len([l for l in r.split("\n") if l.strip()])

        # Stashed
        r = maybe_run_git(self.path, "stash", "list", timeout=10)
        self.has_stashed = bool(r and r.strip())

    def classify(self) -> str:
        """Return the state classification."""
        if self.active_git_op:
            return "in-progress"
        if self.error:
            return "error"
        if not self.has_origin:
            return "no-remote"
        if not self.has_upstream:
            return "no-upstream"
        if self.behind > 0 and self.ahead > 0 and self.uncommitted > 0:
            return "conflict-risk"
        if self.uncommitted > 0 and self.behind > 0:
            return "diverged"
        if self.uncommitted > 0 and self.ahead > 0:
            return "local-ahead"
        if self.uncommitted > 0:
            return "dirty-even"
        if self.ahead > 0 and self.behind == 0:
            return "pushable"
        if self.behind > 0 and self.ahead == 0:
            return "pullable"
        return "clean"


# ── Actions ─────────────────────────────────────────────────────────────────

def pull_ff(repo: GitRepo, report: Report) -> str:
    """Fast-forward pull. Fails safely if not possible."""
    create_backup_tag(repo.path, report)
    if report.dry_run:
        return f"would pull --ff-only ({repo.behind} commits)"
    r = run(["git", "pull", "--ff-only"], repo.path)
    if r.returncode == 0:
        return f"pulled ({repo.behind} commits, ff-only)"
    # --ff-only failed — likely would create merge commit
    run(["git", "merge", "--abort"], repo.path, timeout=10)
    return f"pull failed (ff-only not possible): {r.stderr.strip()}"


def push(repo: GitRepo, report: Report) -> str:
    """Push local commits to origin."""
    create_backup_tag(repo.path, report)
    if report.dry_run:
        return f"would push ({repo.ahead} commits)"
    r = run(["git", "push"], repo.path)
    return f"pushed ({repo.ahead} commits)" if r.returncode == 0 \
        else f"push failed: {r.stderr.strip()}"


def commit_and_push(repo: GitRepo, report: Report) -> str:
    """Stage all, commit, push."""
    create_backup_tag(repo.path, report)
    if report.dry_run:
        return f"would commit {repo.uncommitted} files and push"
    r = run(["git", "add", "-A"], repo.path, timeout=30)
    if r.returncode != 0:
        return f"git add failed: {r.stderr.strip()}"
    r = run(["git", "commit", "-m", "git-audit-sync: auto-commit",
             "-m", f"Uncommitted changes from audit ({repo.uncommitted} files)"],
            repo.path, timeout=30)
    if r.returncode != 0 and "nothing to commit" not in r.stderr:
        return f"commit failed: {r.stderr.strip()}"
    if repo.has_upstream:
        r = run(["git", "push"], repo.path, timeout=30)
        if r.returncode != 0:
            return f"committed but push failed: {r.stderr.strip()}"
        return f"committed + pushed ({repo.uncommitted} files)"
    return f"committed ({repo.uncommitted} files)"


def commit_push_pull(repo: GitRepo, report: Report) -> str:
    """Commit, push, then pull (safer than pull first)."""
    result = commit_and_push(repo, report)
    # If commit+push failed, don't attempt pull
    if result.startswith("commit failed") or result.startswith("committed but push failed"):
        return result
    # Pull after commit+push ensures we're synced both ways
    r = run(["git", "pull", "--ff-only"], repo.path, timeout=30)
    if r.returncode != 0:
        return f"{result}; pull failed: {r.stderr.strip()}"
    return f"{result}; pulled ({repo.behind} commits)"


def push_upstream(repo: GitRepo, report: Report) -> str:
    """Push branch with upstream tracking (for feature branches)."""
    create_backup_tag(repo.path, report)
    if report.dry_run:
        return f"would push --set-upstream origin {repo.branch}"
    r = run(["git", "push", "--set-upstream", "origin", repo.branch],
            repo.path, timeout=30)
    return f"pushed branch '{repo.branch}' to origin" if r.returncode == 0 \
        else f"push failed: {r.stderr.strip()}"


def assess_conflict(repo: GitRepo, report: Report) -> str:
    """Check if diverged changes are in same files. If not, merge."""
    # Find what changed locally vs what changed upstream
    local_files = set()
    r = maybe_run_git(repo.path, "diff", "HEAD", "--name-only", timeout=15)
    if r:
        local_files = set(r.strip().split("\n"))

    upstream_files = set()
    upstream = maybe_run_git(repo.path, "rev-parse", "--abbrev-ref",
                             "--symbolic-full-name", "@{u}", timeout=10)
    if upstream:
        r = maybe_run_git(repo.path, "diff", f"HEAD..{upstream}", "--name-only",
                          timeout=15)
        if r:
            upstream_files = set(r.strip().split("\n"))

    overlap = local_files & upstream_files

    # Safe types: generated/data files that merge fine
    SAFE_EXTENSIONS = {".json", ".csv", ".db", ".lock", ".pyc", ".log",
                       ".svg", ".png", ".jpg", ".ico"}
    safe_overlap = {f for f in overlap
                    if any(f.endswith(ext) for ext in SAFE_EXTENSIONS)}
    real_overlap = overlap - safe_overlap

    if not real_overlap:
        # Only safe overlaps or no overlap — proceed
        result = commit_push_pull(repo, report)
        return f"auto-merged: {result}"

    return real_overlap


# ── Secret detection ──────────────────────────────────────────────────────────

SECRET_PATTERNS = [".env", ".env.*", "*key*", "*secret*", "*token*",
                   "*credential*", "*password*", "*.pem", "*.key",
                   "*auth*", "*access*", "*api-key*"]


def _warn_secrets(repo: GitRepo, report: Report):
    """Check untracked files for potential secrets before staging all."""
    import fnmatch
    r = maybe_run_git(repo.path, "status", "--porcelain", timeout=10)
    if not r:
        return
    untracked = []
    for line in r.split("\n"):
        line = line.strip()
        if line.startswith("??"):
            fname = line[3:]
            for pat in SECRET_PATTERNS:
                if fnmatch.fnmatch(fname, pat) or fnmatch.fnmatch(fname.split("/")[-1], pat):
                    untracked.append(fname)
                    break
    if untracked:
        files_str = ", ".join(untracked[:5])
        more = f" (+{len(untracked)-5} more)" if len(untracked) > 5 else ""
        print(f"  ⚠️  SECRET RISK: untracked files matching secret patterns")
        print(f"     {files_str}{more}")
        print(f"     Continuing anyway — verify .gitignore is correct")


# ── Main loop ───────────────────────────────────────────────────────────────

def find_git_repos(root: Path) -> list[Path]:
    """Find all git repos under root (directories with .git)."""
    repos = []
    for entry in sorted(root.iterdir()):
        if entry.is_dir() and (entry / ".git").exists():
            repos.append(entry)
    return repos


def process_repo(repo_path: Path, report: Report, excludes: set[str]) -> bool:
    """Process a single repo. Returns True if handled."""
    name = repo_path.name
    if name in excludes:
        report.add(name, SKIP, f"{name} — excluded")
        return True

    r = GitRepo(repo_path)
    r.inspect()

    if r.error:
        report.add(name, ERROR, f"{name} — {r.error}")
        return True

    state = r.classify()
    print(f"\n📁 {name} [{state}] branch={r.branch} origin={r.has_origin} "
          f"upstream={r.has_upstream} uncommitted={r.uncommitted} "
          f"ahead={r.ahead} behind={r.behind}")

    try:
        if state == "in-progress":
            report.add(name, SKIP, f"{name} — active {r.active_git_op} in progress (skipped)")
            return True

        if state == "clean":
            report.add(name, OK, f"{name} — clean, up-to-date")

        elif state == "pullable":
            msg = pull_ff(r, report)
            report.add(name, PULLED, f"{name} — {msg}")

        elif state == "pushable":
            msg = push(r, report)
            report.add(name, PUSHED, f"{name} — {msg}")

        elif state == "dirty-even":
            if r.branch != "main" and r.branch != "master":
                report.add(name, SKIP, f"{name} — {r.uncommitted} uncommitted on "
                          f"'{r.branch}' branch (skipped)")
            else:
                _warn_secrets(r, report)
                msg = commit_and_push(r, report)
                report.add(name, COMMITTED, f"{name} — {msg}")

        elif state == "diverged":
            if r.branch != "main" and r.branch != "master":
                report.add(name, SKIP, f"{name} — {r.uncommitted} uncommitted + "
                          f"{r.behind} behind on '{r.branch}' (skipped)")
            else:
                _warn_secrets(r, report)
                msg = commit_push_pull(r, report)
                report.add(name, SYNCED, f"{name} — {msg}")

        elif state == "conflict-risk":
            overlap = assess_conflict(r, report)
            if isinstance(overlap, set) and overlap:
                files_str = ", ".join(sorted(overlap)[:5])
                report.add(name, CONFLICT, f"{name} — DIVERGED in same files: "
                          f"{files_str}. Backup tag created. Needs review.")
            else:
                _warn_secrets(r, report)
                msg = commit_push_pull(r, report)
                report.add(name, SYNCED, f"{name} — auto-resolved: {msg}")

        elif state == "no-upstream" or state == "no-remote":
            if r.uncommitted > 0:
                if r.branch != "main" and r.branch != "master":
                    report.add(name, SKIP, f"{name} — {r.uncommitted} uncommitted "
                              f"on '{r.branch}' (no upstream, skipped)")
                else:
                    msg = commit_and_push(r, report)
                    report.add(name, COMMITTED, f"{name} — {msg}")
            else:
                report.add(name, OK, f"{name} — clean, no upstream")

        else:
            report.add(name, SKIP, f"{name} — unknown state '{state}'")

    except Exception as e:
        report.add(name, ERROR, f"{name} — exception: {e}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Git Audit & Sync — sync all repos in a directory")
    parser.add_argument("directory", type=Path,
                        help="Root directory to scan for git repos")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be done without making changes")
    parser.add_argument("--audit-only", action="store_true",
                        help="Read-only audit, no changes")
    parser.add_argument("--exclude", type=str, default="",
                        help="Comma-separated list of repo names to skip")
    args = parser.parse_args()

    root = args.directory.resolve()
    if not root.is_dir():
        print(f"❌ Not a directory: {root}")
        sys.exit(1)

    dry_run = args.dry_run or args.audit_only
    excludes = set(x.strip() for x in args.exclude.split(",") if x.strip())
    report = Report(root, dry_run)

    repos = find_git_repos(root)
    if not repos:
        print(f"❌ No git repos found in {root}")
        sys.exit(1)

    print(f"{'🔍' if dry_run else '🚀'} Git Audit & Sync")
    print(f"{'   DRY RUN — no changes will be made' if dry_run else ''}")
    print(f"   Directory: {root}")
    print(f"   Repos found: {len(repos)}")
    if excludes:
        print(f"   Excluding: {', '.join(excludes)}")
    print()

    for repo_path in repos:
        process_repo(repo_path, report, excludes)

    report.write()

    if report.stats["conflict"] > 0:
        print(f"\n{CONFLICT} {report.stats['conflict']} repos need your attention!")
        print(f"   Check {report.path} for details")
    if report.stats["error"] > 0:
        print(f"\n{ERROR} {report.stats['error']} repos had errors")
        print(f"   Check {report.path} for details")

    total = sum(report.stats.values())
    ok = report.stats["clean"] + report.stats["pulled"] + report.stats["pushed"] \
         + report.stats["committed"] + report.stats["synced"]
    print(f"\n📊 {ok}/{total} repos clean ({round(ok/total*100)}%)")


if __name__ == "__main__":
    main()
