#!/usr/bin/env python3
"""
Git Audit & Sync — Scan every git repo in a directory, assess state,
and bring all repos to a clean, synced state.

Each repo is processed by an independent worker — safe for parallel
execution since every repo has its own .git directory.

Usage:
    python3 audit_sync.py <directory>
    python3 audit_sync.py <directory> --dry-run
    python3 audit_sync.py <directory> --workers 8
    python3 audit_sync.py <directory> --since-days 7
    python3 audit_sync.py <directory> --exclude repo1,repo2
    python3 audit_sync.py <directory> --commit-message "feat: sync"
    python3 audit_sync.py <directory> --update-submodules
    python3 audit_sync.py <directory> --check-only
"""

import argparse
import concurrent.futures
import fnmatch
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


# ── Lockfile (prevents concurrent runs) ─────────────────────────────────────
LOCKFILE = Path(tempfile.gettempdir()) / "git-audit-sync.lock"
_LOCK_FD: Optional[int] = None


def _lockfile_stale() -> bool:
    """Check if lockfile is stale (mtime > 1h or PID no longer alive)."""
    try:
        if LOCKFILE.exists():
            old_pid = int(LOCKFILE.read_text().strip())
            if not Path(f"/proc/{old_pid}").exists():
                return True
    except (ValueError, OSError, IOError):
        pass
    try:
        age = time.time() - LOCKFILE.stat().st_mtime
        if age > 3600:
            return True
    except OSError:
        pass
    return False


def acquire_lock() -> bool:
    """Acquire a system-wide lock so only one instance runs at a time."""
    global _LOCK_FD
    if _lockfile_stale():
        try:
            LOCKFILE.unlink()
        except OSError:
            pass
    try:
        _LOCK_FD = os.open(str(LOCKFILE), os.O_CREAT | os.O_RDWR, 0o644)
        import fcntl
        fcntl.flock(_LOCK_FD, fcntl.LOCK_EX | fcntl.LOCK_NB)
        LOCKFILE.write_text(str(os.getpid()))
        return True
    except (BlockingIOError, OSError, ImportError):
        if _LOCK_FD is not None:
            os.close(_LOCK_FD)
            _LOCK_FD = None
        return False


def release_lock():
    global _LOCK_FD
    if _LOCK_FD is not None:
        try:
            import fcntl
            fcntl.flock(_LOCK_FD, fcntl.LOCK_UN)
        except Exception:
            pass
        os.close(_LOCK_FD)
        _LOCK_FD = None
        try:
            LOCKFILE.unlink(missing_ok=True)
        except Exception:
            pass


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
    """Collect per-repo results and write a final report (thread-safe)."""

    def __init__(self, root: Path, dry_run: bool, output_dir: Optional[Path] = None):
        self._log_dir = output_dir or LOG_DIR
        self._log_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.path = self._log_dir / f"git-audit-{ts}.md"
        self.json_path = self._log_dir / f"git-audit-{ts}.json"
        self.root = root
        self.dry_run = dry_run
        self.lines: list[str] = []
        self.summary: list[str] = []
        self.stats: dict[str, int] = {
            "clean": 0, "pulled": 0, "pushed": 0, "committed": 0,
            "synced": 0, "conflict": 0, "error": 0, "skipped": 0,
        }
        self.details: list[dict[str, Any]] = []

    def add(self, repo: str, icon: str, msg: str, detail: Optional[dict] = None):
        """Add a result (called from workers). Thread-safe via GIL."""
        label = f"{icon} {msg}"
        self.summary.append(f"| {label} |")
        self.lines.append(f"- {label}")
        if detail:
            self.details.append(detail)
        # Thread-safe stat increment — single dict lookup, atomic under GIL
        icon_groups = {
            "clean": [OK, SKIP, DRY],
            "pulled": [PULLED],
            "pushed": [PUSHED],
            "committed": [COMMITTED],
            "synced": [SYNCED],
            "conflict": [CONFLICT],
            "error": [ERROR],
            "skipped": [SKIP],
        }
        for key, icons in icon_groups.items():
            if icon in icons:
                self.stats[key] = self.stats.get(key, 0) + 1
                break

    def sort_by_state(self):
        """Sort results: errors/conflicts first, then by name."""
        def sort_key(line: str) -> tuple:
            for i, ch in enumerate([ERROR, CONFLICT, SYNCED, COMMITTED, PUSHED, PULLED, SKIP, OK]):
                if line.startswith(f"- {ch}"):
                    return (i, line.lower())
            return (99, line.lower())
        self.lines.sort(key=sort_key)

    def write(self):
        self.sort_by_state()
        total = sum(self.stats.values()) or 1
        ok = self.stats["clean"] + self.stats["pulled"] + self.stats["pushed"] \
             + self.stats["committed"] + self.stats["synced"]
        pct = round(ok / total * 100)

        content = [
            f"# Git Audit — {self.root}",
            f"**Run**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Mode**: {'DRY RUN' if self.dry_run else 'LIVE'}",
            f"**Workers**: parallel (multi-repo)",
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

        # JSON output with sanitized values
        json_data = {
            "root": str(self.root),
            "timestamp": datetime.now().isoformat(),
            "mode": "dry-run" if self.dry_run else "live",
            "stats": self.stats,
            "health_pct": pct,
            "repos": self._sanitize(self.details),
        }
        self.json_path.write_text(json.dumps(json_data, indent=2, default=str))

        print(f"\nReport: {self.path}")
        print(f"JSON:   {self.json_path}")

    @staticmethod
    def _sanitize(obj: Any) -> Any:
        """Recursively sanitize values for JSON serialization."""
        if isinstance(obj, dict):
            return {k: Report._sanitize(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [Report._sanitize(v) for v in obj]
        if isinstance(obj, (str, int, float, bool)):
            return obj
        if obj is None:
            return None
        try:
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            return str(obj)


# ── Helpers ─────────────────────────────────────────────────────────────────

def run(cmd: list[str], cwd: Path, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run a command and return result."""
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


def run_with_retry(cmd: list[str], cwd: Path, timeout: int = 60,
                   max_retries: int = 3, backoff: float = 2.0) -> subprocess.CompletedProcess:
    """Run a command with exponential backoff retry.
    Kills timed-out processes before retrying to avoid orphans."""
    last_exc = None
    for attempt in range(max_retries):
        proc = None
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True, cwd=str(cwd))
            stdout, stderr = proc.communicate(timeout=timeout)
            if proc.returncode == 0:
                return subprocess.CompletedProcess(cmd, proc.returncode, stdout, stderr)
            last_exc = RuntimeError(stderr.strip() or f"exit code {proc.returncode}")
            if attempt < max_retries - 1:
                wait = backoff ** attempt
                print(f"  retry {attempt + 1}/{max_retries} after {wait:.0f}s...")
                time.sleep(wait)
        except subprocess.TimeoutExpired:
            if proc:
                proc.kill()
                proc.wait(timeout=5)
            last_exc = TimeoutError(f"timed out after {timeout}s")
            if attempt < max_retries - 1:
                wait = backoff ** attempt
                print(f"  retry {attempt + 1}/{max_retries} after {wait:.0f}s (killed orphan)...")
                time.sleep(wait)
        except OSError as e:
            last_exc = e
            if attempt < max_retries - 1:
                time.sleep(backoff ** attempt)
    raise RuntimeError(str(last_exc))


def create_backup_branch(repo: Path, dry_run: bool) -> str:
    """Create a lightweight git branch (safer than tag — no detached HEAD)."""
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    repo_name = repo.name
    branch = f"git-audit-sync/backup-{ts}-{repo_name}"
    if not dry_run:
        r = run(["git", "branch", branch], repo)
        if r.returncode == 0:
            print(f"  Backup branch: {branch}")
    else:
        print(f"  Would create backup branch: {branch}")
    return branch


# ── Git error classification & safe recovery ────────────────────────────────

def classify_git_error(text: str) -> str:
    """Bucket a git stderr string into an actionable category."""
    t = (text or "").lower()
    if "repository not found" in t or "could not read from remote" in t \
            or ("not found" in t and "repository" in t):
        return "not-found"
    if ("permission to" in t and "denied" in t) or " 403" in t \
            or "403 " in t or "correct access rights" in t:
        return "permission-denied"
    if "non-fast-forward" in t or "fetch first" in t \
            or "tip of your current branch is behind" in t:
        return "non-fast-forward"
    if "unmerged" in t or "unresolved conflict" in t or "needs merge" in t \
            or ("conflict" in t and "merge" in t):
        return "conflict"
    return ""


def abort_in_progress(repo: Path) -> None:
    """Return a repo to a clean state after a failed merge/rebase so it is
    never left mid-operation — the #1 cause of 'broken' repos after a sync."""
    git_dir = repo / ".git"
    if (git_dir / "rebase-merge").exists() or (git_dir / "rebase-apply").exists():
        run(["git", "rebase", "--abort"], repo, timeout=15)
    elif (git_dir / "MERGE_HEAD").exists():
        run(["git", "merge", "--abort"], repo, timeout=15)


def staged_deletions(repo: Path) -> list[str]:
    """List tracked files that the current index would DELETE. A non-empty
    result during an auto-commit is a strong signal of an accidental `rm`
    that must not be silently captured (it later collides with upstream)."""
    r = maybe_run_git(repo, "diff", "--cached", "--diff-filter=D",
                      "--name-only", timeout=15)
    return [l for l in (r.split("\n") if r else []) if l.strip()]


def find_fork_remote(repo: Path, user: str) -> Optional[str]:
    """Return the name of a push remote whose URL belongs to `user` (a fork we
    can push to), preferring a non-origin remote. Used when origin isn't ours."""
    if not user:
        return None
    raw = maybe_run_git(repo, "remote", "-v", timeout=10)
    if not raw:
        return None
    candidates = []
    for line in raw.split("\n"):
        parts = line.split()
        if len(parts) >= 3 and parts[2] == "(push)":
            name, url = parts[0], parts[1]
            if f"/{user}/" in url or f":{user}/" in url:
                candidates.append(name)
    for c in candidates:
        if c != "origin":
            return c
    return candidates[0] if candidates else None


def _push_fallback(repo: "GitRepo", err: str) -> str:
    """Turn a failed `git push` into an actionable message, and when origin
    push is denied, transparently push to the user's fork remote instead."""
    kind = classify_git_error(err)
    if kind == "permission-denied":
        fork = find_fork_remote(repo.path, _GITHUB_USER)
        if fork:
            try:
                run_with_retry(["git", "push", fork, f"HEAD:{repo.branch}"],
                               repo.path, timeout=30)
                return f"pushed to fork '{fork}' (no push access to origin)"
            except RuntimeError as e2:
                return f"push denied on origin; fork '{fork}' push failed: {e2}"
        return ("push denied — origin not owned by you; create a fork "
                "(gh repo fork) and add it as a remote (or pass --github-user)")
    if kind == "not-found":
        return "push failed — remote repository not found (update or remove origin)"
    if kind == "non-fast-forward":
        return "push rejected (behind remote)"
    return f"push failed: {err}"


def _result_icon(msg: str, default: str) -> str:
    """Choose the report icon for an action result string."""
    low = msg.lower()
    if "git add failed" in low or "commit failed" in low:
        return ERROR
    if ("needs review" in low or "needs manual merge" in low or "denied" in low
            or "not found" in low or "conflicted" in low
            or "create a fork" in low):
        return CONFLICT
    return default


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
        self.active_git_op: Optional[str] = None
        self.is_detached: bool = False
        self.conflict_files: list[str] = []
        self.error: Optional[str] = None
        self.last_modified: Optional[datetime] = None
        self.has_skip_marker: bool = False
        self.untracked_files: list[str] = []
        self.commit_msg: str = "git-audit-sync: auto-commit"
        self.remote_missing: bool = False

    def inspect(self, commit_msg: str = "git-audit-sync: auto-commit"):
        """Gather all state info about this repo."""
        self.commit_msg = commit_msg

        # Check for .gitaudit-skip marker
        self.has_skip_marker = (self.path / ".gitaudit-skip").exists()

        # Last modified time
        try:
            mtime = os.path.getmtime(self.path / ".git")
            self.last_modified = datetime.fromtimestamp(mtime)
        except OSError:
            pass

        # Check for active merge/rebase/cherry-pick/revert
        GIT_LOCK_FILES = ["MERGE_HEAD", "REBASE_HEAD", "CHERRY_PICK_HEAD",
                          "REVERT_HEAD", "MERGE_MSG", "MERGE_MODE", "sequencer/todo"]
        git_dir = self.path / ".git"
        active_ops = []
        for lf in GIT_LOCK_FILES:
            fp = git_dir / lf
            if fp.exists():
                name = lf.replace("_HEAD", "").replace("_MSG", " (merge)") \
                          .replace("_MODE", " (merge)") \
                          .replace("sequencer/todo", "rebase (interactive)")
                active_ops.append(name)
        self.active_git_op = active_ops[0] if active_ops else None
        if self.active_git_op:
            return

        # Detect detached HEAD and get branch name
        # Handle empty repos (no commits yet) - "ambiguous argument 'HEAD'" error
        try:
            head = run_git(self.path, "rev-parse", "--symbolic-full-name", "HEAD", timeout=5)
            self.is_detached = not head.startswith("refs/heads/")
            self.branch = run_git(self.path, "rev-parse", "--abbrev-ref", "HEAD", timeout=10)
        except RuntimeError as e:
            err_str = str(e)
            if "ambiguous argument 'HEAD'" in err_str:
                # Empty repo - no commits yet
                self.error = "empty-repo"
                return
            self.error = err_str
            return

        # Remote
        origin_url = maybe_run_git(self.path, "remote", "get-url", "origin",
                                   timeout=10)
        self.has_origin = origin_url is not None
        if not self.has_origin:
            return

        # Fetch with retry (30s timeout, 2 retries)
        try:
            run_with_retry(["git", "fetch", "origin", "--quiet"],
                           self.path, timeout=30, max_retries=2)
        except RuntimeError as e:
            kind = classify_git_error(str(e))
            if kind == "not-found":
                self.remote_missing = True
                self.error = ("remote repository not found — origin deleted or "
                              "renamed; update the remote URL or remove it")
            elif kind == "permission-denied":
                self.error = ("fetch denied — no access to origin (private/renamed "
                              "repo, or token lacks scope)")
            else:
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

        # Uncommitted + untracked
        r = maybe_run_git(self.path, "status", "--porcelain", timeout=15)
        if r:
            lines = [l.strip() for l in r.split("\n") if l.strip()]
            self.uncommitted = len(lines)
            self.untracked_files = [l[3:] for l in lines if l.startswith("??")]

        # Stashed
        r = maybe_run_git(self.path, "stash", "list", timeout=10)
        self.has_stashed = bool(r and r.strip())

    def classify(self) -> str:
        """Return the state classification."""
        if self.has_skip_marker:
            return "skipped"
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
        if self.behind > 0 and self.ahead > 0:
            return "diverged"
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

def pull_ff(repo: GitRepo, dry_run: bool) -> str:
    """Fast-forward pull. Fails safely if not possible."""
    create_backup_branch(repo.path, dry_run)
    if dry_run:
        return f"would pull --ff-only ({repo.behind} commits)"
    try:
        r = run_with_retry(["git", "pull", "--ff-only"], repo.path, timeout=30)
        return f"pulled ({repo.behind} commits, ff-only)"
    except RuntimeError as e:
        run(["git", "merge", "--abort"], repo.path, timeout=10)
        return f"pull failed: {str(e)}"


def push(repo: GitRepo, dry_run: bool) -> str:
    """Push local commits to origin."""
    create_backup_branch(repo.path, dry_run)
    if dry_run:
        return f"would push ({repo.ahead} commits)"
    try:
        r = run_with_retry(["git", "push"], repo.path, timeout=30)
        return f"pushed ({repo.ahead} commits)"
    except RuntimeError as e:
        return _push_fallback(repo, str(e))


def get_dryrun_diff(repo: GitRepo) -> str:
    """Get a summary of files that would be committed (for dry-run display)."""
    r = maybe_run_git(repo.path, "diff", "--stat", timeout=10)
    untracked = maybe_run_git(repo.path, "ls-files", "--others",
                              "--exclude-standard", timeout=10)
    parts = []
    if r:
        parts.append(r.strip())
    if untracked:
        ucount = len([l for l in untracked.split("\n") if l.strip()])
        if ucount > 0:
            parts.append(f"{ucount} untracked file(s)")
    return " | ".join(parts) if parts else ""


def commit_and_push(repo: GitRepo, dry_run: bool) -> str:
    """Stage all, commit, push."""
    dry_diff = get_dryrun_diff(repo) if dry_run else ""
    create_backup_branch(repo.path, dry_run)
    if dry_run:
        detail = f"would commit {repo.uncommitted} files"
        if dry_diff:
            detail += f" ({dry_diff})"
        detail += " and push"
        return detail

    r = run(["git", "add", "-A"], repo.path, timeout=30)
    if r.returncode != 0:
        return f"git add failed: {r.stderr.strip()}"
    # Safety: never auto-commit deletions of tracked files. An accidental `rm`
    # would otherwise be captured and later collide with upstream (a deletion
    # vs. an upstream edit is an unresolvable auto-merge). Flag for review.
    if not _ALLOW_DELETE:
        dels = staged_deletions(repo.path)
        if dels:
            run(["git", "reset", "-q"], repo.path, timeout=15)
            preview = ", ".join(dels[:3]) + ("…" if len(dels) > 3 else "")
            return (f"NEEDS REVIEW: auto-commit would delete {len(dels)} tracked "
                    f"file(s) ({preview}) — skipped (pass --allow-delete to permit)")
    r = run(["git", "commit", "-m", repo.commit_msg,
             "-m", f"Uncommitted changes from audit ({repo.uncommitted} files)"],
            repo.path, timeout=30)
    if r.returncode != 0 and "nothing to commit" not in r.stderr:
        return f"commit failed: {r.stderr.strip()}"
    commit_hash = maybe_run_git(repo.path, "rev-parse", "--short", "HEAD",
                                timeout=5) or "?"
    if repo.has_upstream:
        try:
            run_with_retry(["git", "push"], repo.path, timeout=30)
            return f"committed + pushed ({repo.uncommitted} files) [{commit_hash}]"
        except RuntimeError as e:
            return f"committed [{commit_hash}]; {_push_fallback(repo, str(e))}"
    return f"committed ({repo.uncommitted} files) [{commit_hash}]"


def commit_push_pull(repo: GitRepo, dry_run: bool) -> str:
    """Commit local work, then (if the first push was rejected for being behind)
    integrate upstream via rebase and re-push, completing the sync. Any rebase
    conflict is aborted so the repo is never left mid-operation."""
    result = commit_and_push(repo, dry_run)
    if dry_run:
        return result
    # Hard stops — nothing safely reconcilable downstream.
    if any(s in result for s in ("commit failed", "git add failed",
                                 "NEEDS REVIEW")):
        return result
    # First push already succeeded — done.
    if "+ pushed" in result or result.startswith("committed (") \
            or "pushed (" in result:
        return result
    # Push was rejected (typically behind): rebase onto upstream, then re-push.
    try:
        run_with_retry(["git", "pull", "--rebase"], repo.path, timeout=30)
    except RuntimeError as e:
        abort_in_progress(repo.path)
        return (f"{result.split(';')[0]}; pull --rebase conflicted "
                f"(aborted, repo left clean) — needs manual merge")
    try:
        run_with_retry(["git", "push"], repo.path, timeout=30)
        return f"{result.split(';')[0]}; rebased on upstream + pushed"
    except RuntimeError as e:
        return f"{result.split(';')[0]}; rebased but re-push failed: " \
               f"{_push_fallback(repo, str(e))}"


def push_upstream(repo: GitRepo, dry_run: bool) -> str:
    """Push branch with upstream tracking (for feature branches)."""
    create_backup_branch(repo.path, dry_run)
    if dry_run:
        return f"would push --set-upstream origin {repo.branch}"
    try:
        run_with_retry(["git", "push", "--set-upstream", "origin", repo.branch],
                       repo.path, timeout=30)
        return f"pushed branch '{repo.branch}' to origin"
    except RuntimeError as e:
        return f"push failed: {str(e)}"


def update_submodules(repo: GitRepo, dry_run: bool) -> Optional[str]:
    """Update submodules if they exist."""
    if dry_run:
        return None
    r = maybe_run_git(repo.path, "submodule", "status", timeout=10)
    if not r or not r.strip():
        return None
    r2 = run(["git", "submodule", "update", "--recursive"], repo.path, timeout=60)
    return "submodules updated" if r2.returncode == 0 else "submodule update failed"


def assess_conflict_files(repo: GitRepo) -> set:
    """Return the set of non-trivial files changed in BOTH local and upstream —
    the real (unsafe) overlap that can't be auto-merged."""
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
    SAFE_EXTENSIONS = {".json", ".csv", ".db", ".lock", ".pyc", ".log",
                       ".svg", ".png", ".jpg", ".ico"}
    safe_overlap = {f for f in overlap
                    if any(f.endswith(ext) for ext in SAFE_EXTENSIONS)}
    return overlap - safe_overlap


def assess_conflict(repo: GitRepo, dry_run: bool) -> Any:
    """Check if diverged changes are in same source files; if not, auto-merge."""
    real_overlap = assess_conflict_files(repo)
    if not real_overlap:
        result = commit_push_pull(repo, dry_run)
        return f"auto-merged: {result}"
    return real_overlap


# ── Secret detection ──────────────────────────────────────────────────────────

SECRET_PATTERNS = [
    ".env", ".env.*", "*key*", "*secret*", "*token*",
    "*credential*", "*password*", "*.pem", "*.key",
    "*auth*", "*access*", "*api-key*",
    "*passwd*", "*private*", "*ssh*", "*cert*",
    "*.p12", "*.jks", "*keystore*", "*truststore*",
]


def check_secrets(repo: GitRepo) -> list[str]:
    """Check ALL changed files (untracked + modified) for potential secrets."""
    found: list[str] = []
    r = maybe_run_git(repo.path, "status", "--porcelain", timeout=10)
    if not r:
        return found
    for line in r.split("\n"):
        line = line.strip()
        if not line or len(line) < 4:
            continue
        fname = line[3:]
        basename = os.path.basename(fname)
        for pat in SECRET_PATTERNS:
            if fnmatch.fnmatch(fname, pat) or fnmatch.fnmatch(basename, pat):
                found.append(fname)
                break
    return list(set(found))


# ── Git repo discovery (cross-platform) ────────────────────────────────────

def _find_git_repos_windows(root: Path) -> list[Path]:
    """Find git repos on Windows (fallback when find(1) not available)."""
    repos = []
    SKIP = {"node_modules", ".cache", "venv", ".venv", "__pycache__",
            "target", "build", "dist", ".git"}
    try:
        for p in root.rglob(".git"):
            if p.is_dir() and p.parent.name not in SKIP:
                repos.append(p.parent)
    except PermissionError:
        pass
    return sorted(set(repos))


def find_git_repos(root: Path, maxdepth: int = 3) -> list[Path]:
    """Recursively find all git repos under root (uses find on Linux/macOS, rglob on Windows)."""
    if os.name == "nt":
        return _find_git_repos_windows(root)
    try:
        r = subprocess.run([
            "find", str(root),
            "-name", ".git", "-type", "d",
            "-not", "-path", "*/node_modules/*",
            "-not", "-path", "*/.cache/*",
            "-not", "-path", "*/venv/*",
            "-not", "-path", "*/.venv/*",
            "-not", "-path", "*/__pycache__/*",
            "-not", "-path", "*/target/*",
            "-maxdepth", str(maxdepth),
        ], capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            raise RuntimeError(r.stderr)
        repos = []
        for line in r.stdout.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            repo_dir = Path(line).parent
            repos.append(repo_dir)
        return sorted(set(repos))
    except Exception:
        repos = []
        for entry in sorted(root.iterdir()):
            if entry.is_dir() and (entry / ".git").exists():
                repos.append(entry)
        return repos


# ── Globals shared with worker threads ──────────────────────────────────────
_PROCESS_QUIET = False
_GITHUB_USER = ""        # used to find a fork remote when origin push is denied
_ALLOW_DELETE = False    # permit auto-commit of tracked-file deletions


def detect_github_user() -> str:
    """Best-effort GitHub username for fork-remote fallback: gh CLI, then
    git config. Returns '' if unknown (fork fallback then just reports)."""
    try:
        r = run(["gh", "api", "user", "-q", ".login"], Path.cwd(), timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    try:
        r = run(["git", "config", "--get", "github.user"], Path.cwd(), timeout=5)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return ""


# ── Repo processing (runs in parallel worker) ──────────────────────────────

def process_repo(repo_path: Path, excludes: set[str], dry_run: bool,
                 since: Optional[int], commit_msg: str,
                 do_submodules: bool) -> tuple[str, str, str, Optional[dict]]:
    """Process a single repo. Returns (name, icon, message, detail_dict).
    Designed to be called from parallel workers — no shared state needed."""
    name = repo_path.name

    if name in excludes:
        return (name, SKIP, f"{name} — excluded", None)

    # --since filter: skip repos not modified recently
    if since is not None:
        try:
            mtime = os.path.getmtime(repo_path / ".git")
            age_days = (time.time() - mtime) / 86400
            if age_days > since:
                return (name, SKIP,
                        f"{name} — not modified in {since}+ days (skipped)",
                        {"state": "stale", "age_days": round(age_days, 1)})
        except OSError:
            pass

    r = GitRepo(repo_path)
    r.inspect(commit_msg=commit_msg)

    if r.has_skip_marker:
        return (name, SKIP, f"{name} — .gitaudit-skip marker found (skipped)", None)

    if r.error:
        if r.error == "empty-repo":
            return (name, SKIP, f"{name} — empty repo (no commits yet, skipped)", {"state": "empty", "error": "empty repo"})
        return (name, ERROR, f"{name} — {r.error}",
                {"state": "error", "error": r.error})

    if r.is_detached:
        return (name, SKIP,
                f"{name} — detached HEAD (skip) — git switch <branch>",
                {"state": "detached", "branch": r.branch})

    state = r.classify()
    if not _PROCESS_QUIET:
        print(f"{name} [{state}] br={r.branch} u={r.uncommitted} "
              f"a={r.ahead} b={r.behind}", flush=True)

    detail: dict[str, Any] = {
        "name": name, "state": state, "branch": r.branch,
        "uncommitted": r.uncommitted, "ahead": r.ahead, "behind": r.behind,
    }

    try:
        if state == "in-progress":
            return (name, SKIP, f"{name} — active {r.active_git_op} (skipped)", detail)

        if state == "clean":
            return (name, OK, f"{name} — clean, up-to-date", detail)

        elif state == "pullable":
            msg = pull_ff(r, dry_run)
            detail["action"] = "pull"
            return (name, PULLED, f"{name} — {msg}", detail)

        elif state == "pushable":
            msg = push(r, dry_run)
            detail["action"] = "push"
            return (name, PUSHED, f"{name} — {msg}", detail)

        elif state == "dirty-even":
            if r.branch not in ("main", "master"):
                return (name, SKIP, f"{name} — {r.uncommitted} uncommitted on "
                        f"'{r.branch}' branch (skipped)", detail)
            secrets = check_secrets(r)
            if secrets:
                print(f"  SECRET RISK: {', '.join(secrets[:3])}")
            msg = commit_and_push(r, dry_run)
            detail["action"] = "commit+push"
            detail["secrets"] = secrets[:3] if secrets else []
            return (name, _result_icon(msg, COMMITTED), f"{name} — {msg}", detail)

        elif state == "local-ahead":
            # Uncommitted changes + ahead of upstream
            # Commit the changes then push both new and existing ahead commits
            if r.branch not in ("main", "master"):
                return (name, SKIP, f"{name} — {r.uncommitted} uncommitted + "
                        f"{r.ahead} ahead on '{r.branch}' branch (skipped)", detail)
            secrets = check_secrets(r)
            if secrets:
                print(f"  SECRET RISK: {', '.join(secrets[:3])}")
            # First commit uncommitted changes
            if r.uncommitted > 0:
                if dry_run:
                    return (name, COMMITTED, f"{name} — would commit {r.uncommitted} files and push ({r.ahead} ahead)", detail)
                try:
                    run(["git", "add", "-A"], r.path, timeout=30)
                    run(["git", "commit", "-m", commit_msg], r.path, timeout=30)
                except RuntimeError as e:
                    return (name, ERROR, f"{name} — commit failed: {e}", {"state": "error", "error": str(e)})
            # Then push all ahead commits
            msg = push(r, dry_run)
            detail["action"] = "commit+push (local-ahead)"
            detail["secrets"] = secrets[:3] if secrets else []
            return (name, _result_icon(msg, COMMITTED), f"{name} — {msg}", detail)

        elif state == "diverged":
            if r.branch not in ("main", "master"):
                return (name, SKIP, f"{name} — diverged "
                        f"({r.ahead} ahead, {r.behind} behind, {r.uncommitted} uncommitted) "
                        f"on '{r.branch}' (skipped)", detail)
            secrets = check_secrets(r)
            if secrets:
                print(f"  SECRET RISK: {', '.join(secrets[:3])}")
            if r.uncommitted > 0:
                # Has uncommitted changes: commit, push, then pull
                msg = commit_push_pull(r, dry_run)
                detail["action"] = "commit+push+pull"
            else:
                # No uncommitted changes: just pull then push
                # First pull with rebase, then push
                if dry_run:
                    msg = f"would pull --rebase ({r.behind} commits) and push ({r.ahead} commits)"
                else:
                    try:
                        run_with_retry(["git", "pull", "--rebase"], r.path, timeout=30)
                        pull_msg = f"pulled --rebase ({r.behind} commits)"
                    except RuntimeError as e:
                        abort_in_progress(r.path)
                        detail["conflict_files"] = sorted(
                            assess_conflict_files(r))[:5]
                        return (name, CONFLICT,
                                f"{name} — pull --rebase conflicted "
                                f"(aborted, left clean) — needs manual merge",
                                {**detail, "state": "diverged"})
                    try:
                        run_with_retry(["git", "push"], r.path, timeout=30)
                        push_msg = f"pushed ({r.ahead} commits)"
                    except RuntimeError as e:
                        push_msg = _push_fallback(r, str(e))
                    msg = f"{pull_msg}; {push_msg}"
                detail["action"] = "pull+push"
            detail["secrets"] = secrets[:3] if secrets else []
            if do_submodules:
                sm = update_submodules(r, dry_run)
                if sm:
                    msg += f"; {sm}"
                    detail["submodules"] = sm
            return (name, _result_icon(msg, SYNCED), f"{name} — {msg}", detail)

        elif state == "conflict-risk":
            overlap = assess_conflict(r, dry_run)
            if isinstance(overlap, set) and overlap:
                files_str = ", ".join(sorted(overlap)[:5])
                detail["conflict_files"] = sorted(overlap)[:5]
                return (name, CONFLICT, f"{name} — DIVERGED in same files: "
                        f"{files_str}. Needs review.", detail)
            secrets = check_secrets(r)
            if secrets:
                print(f"  SECRET RISK: {', '.join(secrets[:3])}")
            msg = commit_push_pull(r, dry_run)
            detail["action"] = "auto-resolved"
            detail["secrets"] = secrets[:3] if secrets else []
            return (name, _result_icon(msg, SYNCED),
                    f"{name} — auto-resolved: {msg}", detail)

        elif state in ("no-upstream", "no-remote"):
            if r.uncommitted > 0:
                if r.branch not in ("main", "master"):
                    return (name, SKIP, f"{name} — {r.uncommitted} uncommitted "
                            f"on '{r.branch}' (no upstream, skipped)", detail)
                msg = commit_and_push(r, dry_run)
                detail["action"] = "commit (no upstream)"
                return (name, _result_icon(msg, COMMITTED),
                        f"{name} — {msg}", detail)
            return (name, OK, f"{name} — clean, no upstream", detail)

        else:
            return (name, SKIP, f"{name} — unknown state '{state}'", detail)

    except Exception as e:
        print(f"  {str(e)[:200]}", file=sys.stderr, flush=True)
        return (name, ERROR, f"{name} — {str(e)[:200]}",
                {"state": "error", "error": str(e)[:500]})


# ── Main ─────────────────────────────────────────────────────────────────────

def check_pi_model():
    """Check if Pi is configured with a good model via model-scan."""
    try:
        result = subprocess.run(
            ["python3", str(Path.home() / "code" / "model-scan" / "cli_overall.py"), "overall", "-a", "--free"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            recommended = result.stdout.strip().split("\n")[0]
            # Read current Pi settings
            settings_path = Path.home() / ".config" / "pi" / "settings.json"
            if settings_path.exists():
                settings = json.loads(settings_path.read_text())
                current = settings.get("defaultModel", "unknown")
                if recommended.lower() not in current.lower() and current.lower() not in recommended.lower():
                    return {
                        "current": current,
                        "recommended": recommended,
                        "match": False,
                    }
            return {"recommended": recommended, "match": True}
    except Exception:
        pass
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Git Audit & Sync — sync all repos in a directory in parallel")
    parser.add_argument("directory", type=Path,
                        help="Root directory to scan for git repos")
    parser.add_argument("--fix", action="store_true",
                        help="Auto-fix all issues (commit, push, pull)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be done without making changes")
    parser.add_argument("--audit-only", action="store_true",
                        help=argparse.SUPPRESS)
    parser.add_argument("--exclude", type=str, default="",
                        help="Comma or space-separated list of repo names to skip")
    parser.add_argument("--maxdepth", type=int, default=3,
                        help="Max directory depth for repo discovery (default: 3)")
    parser.add_argument("--since-days", type=int, default=None, dest="since",
                        help="Only process repos modified in the last N days")
    parser.add_argument("--since-date", type=str, default=None,
                        help="Only process repos modified since date (YYYY-MM-DD)")
    parser.add_argument("--since", type=int, default=None, help=argparse.SUPPRESS)
    parser.add_argument("--workers", type=int, default=0,
                        help="Number of parallel workers (default: min(16, cpu_count*2))")
    parser.add_argument("--commit-message", type=str,
                        default="git-audit-sync: auto-commit",
                        help="Custom commit message")
    parser.add_argument("--update-submodules", action="store_true",
                        help="Update git submodules after pull")
    parser.add_argument("--table", action="store_true",
                        help="Compact table output (good for terminal)")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Suppress per-repo output")
    parser.add_argument("--output-dir", type=Path, default=None,
                        help="Report output directory (default: ~/git-audit-logs)")
    parser.add_argument("--check-only", action="store_true",
                        help="Exit non-zero if any repo is dirty/conflicted (for CI)")
    parser.add_argument("--prune-backups", type=int, default=None,
                        help="Remove backup branches older than N days")
    parser.add_argument("--github-user", type=str, default="",
                        help="GitHub username for fork-remote fallback when "
                             "origin push is denied (auto-detected via gh/git if unset)")
    parser.add_argument("--allow-delete", action="store_true",
                        help="Permit auto-commit of tracked-file deletions "
                             "(default: deletions are flagged for review, not committed)")
    args = parser.parse_args()

    # Parse excludes with shlex to handle spaces properly
    excludes = set()
    if args.exclude:
        try:
            for part in shlex.split(args.exclude):
                excludes.add(part.strip())
        except ValueError:
            excludes = set(x.strip() for x in args.exclude.split(",") if x.strip())

    root = args.directory.resolve()
    if not root.is_dir():
        print(f"Not a directory: {root}")
        sys.exit(1)

    # Check Pi model configuration
    pi_check = check_pi_model()
    if pi_check and not pi_check.get("match", True):
        print(f"\n⚠️  Pi model mismatch:")
        print(f"   Current:    {pi_check['current']}")
        print(f"   Recommended: {pi_check['recommended']}")
        print(f"   Run: pi settings defaultModel {pi_check['recommended']}")
        print()

    # PID lockfile
    if not acquire_lock():
        print(f"Another instance is already running (lock: {LOCKFILE})")
        sys.exit(1)

    try:
        repos = find_git_repos(root, args.maxdepth)
        if not repos:
            print(f"No git repos found in {root}")
            return

        dry_run = not args.fix if args.fix else (args.dry_run or args.audit_only)

        # --since-date conversion
        since = args.since
        if args.since_date is not None:
            try:
                ref = datetime.strptime(args.since_date, "%Y-%m-%d")
                since = int((datetime.now() - ref).total_seconds() / 86400)
            except ValueError:
                print(f"  Invalid --since-date format (use YYYY-MM-DD)")
                since = None

        workers = args.workers if args.workers > 0 else min(16, (os.cpu_count() or 4) * 2)

        # --prune-backups: clean old backup branches
        if args.prune_backups is not None and not dry_run:
            pruned = 0
            for rp in repos:
                raw = maybe_run_git(rp, "branch", "--list", "git-audit-sync/*", timeout=15)
                if not raw:
                    continue
                for b in raw.strip().split("\n"):
                    b = b.strip().strip("*").strip()
                    if not b:
                        continue
                    age_cmd = run(["git", "log", "-1", "--format=%ct", b], rp, timeout=10)
                    if age_cmd.returncode == 0 and age_cmd.stdout.strip().isdigit():
                        age_days = (time.time() - int(age_cmd.stdout.strip())) / 86400
                        if age_days > args.prune_backups:
                            run(["git", "branch", "-D", b], rp, timeout=10)
                            pruned += 1
                            if not args.quiet:
                                print(f"  Pruned old backup: {b} ({age_days:.0f}d)")
            if pruned and not args.quiet:
                print(f"  Pruned {pruned} old backup branches")

        # Set worker-visible globals
        global _PROCESS_QUIET, _GITHUB_USER, _ALLOW_DELETE
        _PROCESS_QUIET = args.quiet
        _ALLOW_DELETE = args.allow_delete
        _GITHUB_USER = args.github_user.strip() or detect_github_user()
        if _GITHUB_USER and not args.quiet:
            print(f"  Fork fallback user: {_GITHUB_USER}")

        report = Report(root, dry_run, output_dir=args.output_dir)

        print(f"{'Dry run' if dry_run else 'Live'} — {len(repos)} repos, {workers} workers")
        if excludes:
            print(f"  Excluding: {', '.join(excludes)}")
        if since:
            print(f"  Since: {since} days")
        print()

        # Parallel processing via ThreadPoolExecutor
        results: list[tuple[str, str, str, Optional[dict]]] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(process_repo, rp, excludes, dry_run, since,
                            args.commit_message, args.update_submodules): rp
                for rp in repos
            }
            for future in concurrent.futures.as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    rp = futures[future]
                    results.append((rp.name, ERROR, f"{rp.name} — worker crashed: {e}", None))

        # Merge results (single-threaded)
        for name, icon, msg, detail in results:
            report.add(name, icon, msg, detail)

        # --table: compact terminal table
        if args.table:
            print(f"\n{'Repo':30s} {'State':15s} {'Branch':20s} {'Files':>6s} {'Action':30s}")
            print("-" * 101)
            for name, icon, msg, detail in sorted(results, key=lambda x: x[0]):
                d = detail or {}
                state = d.get("state", "?")[:15]
                branch = d.get("branch", "?")[:20]
                files = str(d.get("uncommitted", 0))
                # Strip repo name prefix from msg
                action = msg.replace(f"{name} — ", "")[:30]
                print(f"{name:30s} {state:15s} {branch:20s} {files:>6s} {action:30s}")
            print()

        # Create REMEDIATION_PLAN.md in repos that need attention during live runs only.
        # Audit-only/dry-run must remain read-only aside from git fetch/report output.
        if not dry_run:
            for name, icon, msg, detail in results:
                if icon in (CONFLICT, ERROR):
                    plan_path = Path(str(args.directory)) / name / "REMEDIATION_PLAN.md"
                    d = detail or {}
                    plan = [
                        f"# REMEDIATION PLAN — {name}",
                        f"**Generated**: {datetime.now().isoformat()}",
                        f"**Status**: {icon} Needs attention",
                        "",
                        "## Issue",
                        f"State: {d.get('state', 'unknown')}",
                        f"Branch: {d.get('branch', '?')}",
                        f"Uncommitted: {d.get('uncommitted', 0)} files",
                        f"Ahead: {d.get('ahead', 0)} | Behind: {d.get('behind', 0)}",
                        "",
                        "## Investigation",
                        d.get("error", "Same files changed in both local and upstream.") if isinstance(d.get("error"), str) else "",
                        "",
                        "## Recommended Actions",
                        "- [ ] Review changes: `git diff HEAD..@{u}`" if d.get("behind", 0) > 0 else "",
                        "- [ ] Commit or stash local changes" if d.get("uncommitted", 0) > 0 else "",
                        "- [ ] Pull upstream: `git pull --rebase`" if d.get("behind", 0) > 0 else "",
                        "- [ ] Push local: `git push`" if d.get("ahead", 0) > 0 else "",
                        "- [ ] Resolve merge conflicts if any",
                        "",
                        "## Auto-sync will skip this repo until resolved.",
                    ]
                    try:
                        plan_path.parent.mkdir(parents=True, exist_ok=True)
                        marker = f"\n---\n*Generated by reposcan at {datetime.now().isoformat()}*\n"
                        # Append if exists, create if not
                        existing = plan_path.read_text() if plan_path.exists() else ""
                        if existing:
                            plan_text = existing + marker + "\n".join(filter(None, plan))
                        else:
                            plan_text = "\n".join(filter(None, plan)) + marker
                        plan_path.write_text(plan_text)
                        if not args.quiet:
                            action = "updated" if existing else "created"
                            print(f"  📋 Remediation plan: {action} {plan_path}")
                    except (OSError, PermissionError) as e:
                        if not args.quiet:
                            print(f"  ⚠️  Could not write remediation plan: {e}")

        # --check-only: exit 1 if any repo is dirty or conflicted
        if args.check_only:
            for name, icon, msg, detail in results:
                if icon in (ERROR, CONFLICT) and detail:
                    s = detail.get("state", "")
                    if s in ("dirty-even", "diverged", "conflict-risk", "error"):
                        print(f"--check-only: {name} in state '{s}'")
                        sys.exit(1)
                elif icon == SKIP and detail:
                    s = detail.get("state", "")
                    if s in ("conflict-risk",):
                        print(f"--check-only: {name} has conflict risk")
                        sys.exit(1)
            print("--check-only: all repos clean")
            sys.exit(0)

        report.write()

        if report.stats["conflict"] > 0:
            print(f"\n{report.stats['conflict']} repos need your attention!")
        if report.stats["error"] > 0:
            print(f"\n{report.stats['error']} repos had errors")

        total = sum(report.stats.values())
        ok = report.stats["clean"] + report.stats["pulled"] + report.stats["pushed"] \
             + report.stats["committed"] + report.stats["synced"]
        pct = round(ok / total * 100) if total else 0
        print(f"\n{ok}/{total} repos clean ({pct}%)")

    finally:
        release_lock()


if __name__ == "__main__":
    main()
