"""Shared helpers for the project-archive scripts. Python standard library only.

Every helper here is read-only on the folders it inspects. The only writes are
JSON and Markdown files under a staging directory the caller names, and the
sandbox copies made by the sandbox and recovery tests.
"""
import datetime as _dt
import hashlib
import json
import os
import re
import stat
import subprocess
import sys

sys.dont_write_bytecode = True

# Discovery skip list from the Atlas prompt, Phase 2 step 1
# (project-atlas/sources/atlas-pack/atlas-agent-prompt.md line 184).
SKIP_DIRS = {
    "node_modules", ".venv", "venv", "dist", "build", ".next", "target",
    ".turbo", ".cache", "coverage", "__pycache__", "vendor",
}

# File names whose contents are never shown (Atlas Invariant 5: record presence only).
SENSITIVE_NAME = re.compile(
    r"(^\.env|\.pem$|\.key$|^id_(rsa|ed25519|ecdsa|dsa)|credential|secret|token|\.p12$|\.pfx$|\.kdbx$|\.netrc$|\.pgpass$)",
    re.I,
)
SECRET_RE = re.compile(
    r"(?i:(?:api[_-]?key|secret|token|passw(?:or)?d|pwd|bearer|private[_-]?key|access[_-]?key|auth)\s*[:=]\s*\S+)"
    r"|(?:sk|pk|ghp|gho|ghs|github_pat|xox[abp])[-_][A-Za-z0-9_\-]{8,}"
    r"|AKIA[0-9A-Z]{16}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|(?<![\w/.\-])(?=[A-Za-z0-9+_\-]*\d)(?=[A-Za-z0-9+_\-]*[A-Za-z])[A-Za-z0-9+_\-]{32,}={0,2}"
)

GIT_ENV = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0", LC_ALL="C")


def now_iso():
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def redact(text):
    return SECRET_RE.sub("[redacted]", text)


def is_sensitive_name(path):
    return bool(SENSITIVE_NAME.search(os.path.basename(path)))


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def inside(path, folder):
    """True when path equals folder or lies under it (both made absolute, not resolved)."""
    p = os.path.abspath(path)
    f = os.path.abspath(folder)
    return p == f or p.startswith(f.rstrip(os.sep) + os.sep)


def inside_real(path, folder):
    return inside(os.path.realpath(path), os.path.realpath(folder))


def walk(root, skip_dirs=SKIP_DIRS, exclude=(), skip_git=True):
    """os.walk that never follows links, prunes the skip list and excluded paths.

    Yields (dirpath, dirnames, filenames, symlinks) where symlinks lists names of
    entries in dirpath that are symbolic links (to files or directories).
    """
    exclude = [os.path.abspath(e) for e in exclude]
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        if any(inside(dirpath, e) for e in exclude):
            dirnames[:] = []
            continue
        links = []
        keep = []
        for d in sorted(dirnames):
            full = os.path.join(dirpath, d)
            if os.path.islink(full):
                links.append(d)
                continue
            if d in skip_dirs or (skip_git and d == ".git"):
                continue
            if any(inside(full, e) for e in exclude):
                continue
            keep.append(d)
        dirnames[:] = keep
        files = []
        for f in sorted(filenames):
            full = os.path.join(dirpath, f)
            if os.path.islink(full):
                links.append(f)
            elif not any(inside(full, e) for e in exclude):
                files.append(f)
        yield dirpath, keep, files, sorted(links)


def tree_entries(folder):
    """Every entry under folder, including .git internals, without following links."""
    out = []
    for dirpath, dirnames, filenames in os.walk(folder, followlinks=False):
        dirnames.sort()
        for d in list(dirnames):
            full = os.path.join(dirpath, d)
            if os.path.islink(full):
                out.append((os.path.relpath(full, folder), "l", os.readlink(full), full))
                dirnames.remove(d)
            elif not os.listdir(full):
                out.append((os.path.relpath(full, folder), "d", "", full))
        for f in sorted(filenames):
            full = os.path.join(dirpath, f)
            rel = os.path.relpath(full, folder)
            if os.path.islink(full):
                out.append((rel, "l", os.readlink(full), full))
            else:
                out.append((rel, "f", "", full))
    out.sort(key=lambda e: e[0].split(os.sep))
    return out


def tree_digest(folder):
    """SHA-256 over every path, type, executable bit and content (or link target).

    Modification times are left out so a copy or a move keeps the digest.
    """
    h = hashlib.sha256()
    for rel, kind, target, full in tree_entries(folder):
        if kind == "f":
            mode = os.lstat(full).st_mode
            body = ("x" if mode & stat.S_IXUSR else "-") + sha256_file(full)
        else:
            body = target
        h.update(rel.encode("utf-8", "surrogateescape") + b"\0" + kind.encode() + b"\0" + body.encode("utf-8", "surrogateescape") + b"\0")
    return h.hexdigest()


def file_manifest(folder):
    rows = []
    for rel, kind, target, full in tree_entries(folder):
        st = os.lstat(full)
        row = {
            "path": rel,
            "type": {"f": "file", "l": "symlink", "d": "empty-dir"}[kind],
            "mode": oct(stat.S_IMODE(st.st_mode)),
            "mtime": _dt.datetime.fromtimestamp(st.st_mtime, _dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        if kind == "f":
            row["size"] = st.st_size
            row["sha256"] = sha256_file(full)
            if is_sensitive_name(full):
                row["sensitive_name"] = True
        elif kind == "l":
            row["target"] = target
        rows.append(row)
    return rows


def git(folder, *args, timeout=60):
    try:
        r = subprocess.run(["git", "-C", folder] + list(args), capture_output=True, env=GIT_ENV, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 127, "", str(exc)
    return r.returncode, r.stdout.decode("utf-8", "surrogateescape"), r.stderr.decode("utf-8", "surrogateescape")


def git_facts(folder):
    """Read-only Git facts for a folder. Never commits, stashes, resets or fetches."""
    folder = os.path.abspath(folder)
    facts = {"is_repo_root": False}
    dotgit = os.path.join(folder, ".git")
    rc, top, _ = git(folder, "rev-parse", "--show-toplevel")
    if rc != 0:
        facts["inside_repo"] = None
        return facts
    top = top.strip()
    if os.path.realpath(top) != os.path.realpath(folder):
        facts["inside_repo"] = top
        return facts
    facts["is_repo_root"] = True
    facts["is_linked_worktree"] = os.path.isfile(dotgit)
    if facts["is_linked_worktree"]:
        with open(dotgit, encoding="utf-8", errors="replace") as fh:
            facts["gitdir_pointer"] = fh.read().strip()
    rc, head, _ = git(folder, "rev-parse", "HEAD")
    facts["head"] = head.strip() if rc == 0 else None
    rc, br, _ = git(folder, "symbolic-ref", "--short", "-q", "HEAD")
    facts["branch"] = br.strip() if rc == 0 else None
    rc, roots, _ = git(folder, "rev-list", "--max-parents=0", "HEAD")
    facts["root_commits"] = roots.split() if rc == 0 else []
    rc, rem, _ = git(folder, "remote", "-v")
    facts["remotes"] = sorted({redact(l.split()[1]) for l in rem.splitlines() if len(l.split()) >= 2})
    rc, st, _ = git(folder, "status", "--porcelain=v1", "--untracked-files=all")
    facts["status_porcelain"] = st
    facts["dirty"] = bool(st.strip())
    facts["untracked"] = [l[3:] for l in st.splitlines() if l.startswith("?? ")]
    rc, stash, _ = git(folder, "stash", "list")
    facts["stash_list"] = stash
    facts["stash_count"] = len([l for l in stash.splitlines() if l.strip()])
    # Content of every path git status lists, hashed by us. `git diff HEAD` is not
    # used because it refreshes .git/index, which is a write.
    h = hashlib.sha256()
    for line in st.splitlines():
        path = line[3:].split(" -> ")[-1].strip('"')
        full = os.path.join(folder, path)
        body = sha256_file(full) if os.path.isfile(full) and not os.path.islink(full) else ("missing" if not os.path.lexists(full) else "other")
        h.update(path.encode("utf-8", "surrogateescape") + b"\0" + body.encode() + b"\0")
    facts["changed_content_sha256"] = h.hexdigest()
    rc, wt, _ = git(folder, "worktree", "list", "--porcelain")
    worktrees = []
    for block in wt.strip().split("\n\n"):
        for line in block.splitlines():
            if line.startswith("worktree "):
                worktrees.append(line[len("worktree "):])
    facts["worktrees"] = worktrees
    return facts


GIT_STATE_KEYS = ("head", "branch", "status_porcelain", "stash_list", "changed_content_sha256")


def git_state(facts):
    return {k: facts.get(k) for k in GIT_STATE_KEYS}


def write_json(path, obj):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    data = json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(data)
    return sha256_bytes(data.encode("utf-8"))


def read_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def hold_active(hold_file):
    """A migration hold is active when the file lists `migration` under `hold`.

    Accepts the Atlas controls.yaml form (`hold: [migration]`) or JSON
    ({"hold": ["migration"]}). A missing file means no hold.
    """
    if not hold_file or not os.path.isfile(hold_file):
        return False
    text = open(hold_file, encoding="utf-8", errors="replace").read()
    try:
        data = json.loads(text)
        return "migration" in (data.get("hold") or [])
    except (ValueError, AttributeError):
        pass
    for line in text.splitlines():
        line = line.split("#", 1)[0]
        m = re.match(r"\s*hold\s*:\s*\[(.*)\]", line)
        if m and "migration" in [x.strip().strip("'\"") for x in m.group(1).split(",")]:
            return True
    return False


def load_approval(path, source, dest):
    """An operator approval names the exact source and destination of one move."""
    res = {"present": False, "matches_exact_move": False, "approved_by": None, "approved_at": None}
    if not path or not os.path.isfile(path):
        return res
    try:
        a = read_json(path)
    except ValueError:
        res["error"] = "approval file is not JSON"
        return res
    res["present"] = True
    res["approved_by"] = a.get("approved_by")
    res["approved_at"] = a.get("approved_at")
    res["matches_exact_move"] = bool(
        a.get("approved_by")
        and os.path.abspath(str(a.get("source", ""))) == os.path.abspath(source)
        and os.path.abspath(str(a.get("dest", ""))) == os.path.abspath(dest)
    )
    if a.get("signature"):
        res["signature_present"] = True
    return res


def receipts_path(staging):
    return os.path.join(staging, "receipts.jsonl")


def read_receipts(staging):
    p = receipts_path(staging)
    if not os.path.isfile(p):
        return []
    with open(p, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def append_receipt(staging, step, files=None, extra=None):
    rs = read_receipts(staging)
    rec = {"seq": len(rs) + 1, "step": step, "at": now_iso(), "files": files or {}}
    if extra:
        rec.update(extra)
    with open(receipts_path(staging), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


def die(msg, code=2):
    print(msg, file=sys.stderr)
    sys.exit(code)
