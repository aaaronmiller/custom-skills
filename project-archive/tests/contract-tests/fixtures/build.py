"""Contract-test fixtures, independent of the skills' own fixtures.

build(top) creates, all under top:
  .project-archive-sandbox         marker that allows sandbox-mode moves under top
  code/site-old/                   plain folder to move (DA-032), with three consumers:
  code/bin/site-old                  a symlink to it
  code/etc/site.yaml                 a config naming its path
  code/jobs/nightly.cron             a cron-style line naming its path
  code/jobs/other.cron             a near miss (site-old-v2) that is not a consumer
  code/notes-repo/                 Git repo (DA-033): one uncommitted edit, one
                                   untracked file, one stash entry, spec.md
  code/current/spec.md             successor spec for notes-repo
  archive/                         archive root
  living/history.md                Living Documents page
  discovery.json, hold.yaml, approval-site-old.json, approval-notes-repo.json
The DA-034 folders are static Markdown in fixtures/lineage/ (attempt-1, attempt-2, current).
"""
import json
import os
import subprocess
import time

GIT_ENV = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT="0",
               GIT_AUTHOR_DATE="2026-10-20T09:00:00Z", GIT_COMMITTER_DATE="2026-10-20T09:00:00Z")
GITC = ["-c", "user.name=contract fixture", "-c", "user.email=contract-fixture@localhost",
        "-c", "commit.gpgsign=false", "-c", "init.defaultBranch=main"]

SPEC = """# notes-repo spec (contract fixture)

## Requirements

- **NR-001**: THE notes store SHALL keep every note as a plain Markdown file.
"""


def w(p, text):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)


def git(cwd, *a):
    subprocess.run(["git"] + GITC + list(a), cwd=cwd, env=GIT_ENV, check=True, capture_output=True)


def build(top):
    top = os.path.abspath(top)
    os.makedirs(top)
    w(os.path.join(top, ".project-archive-sandbox"), "contract-test sandbox\n")
    code = os.path.join(top, "code")
    site = os.path.join(code, "site-old")
    w(os.path.join(site, "index.html"), "<p>old site</p>\n")
    w(os.path.join(site, "assets", "style.css"), "p { color: black; }\n")
    os.makedirs(os.path.join(code, "bin"))
    os.symlink(site, os.path.join(code, "bin", "site-old"))
    w(os.path.join(code, "etc", "site.yaml"), "root: %s\nport: 8080\n" % site)
    w(os.path.join(code, "jobs", "nightly.cron"), "0 3 * * * rsync -a %s/ /srv/backup/\n" % site)
    w(os.path.join(code, "jobs", "other.cron"), "0 4 * * * ls %s-v2\n" % site)
    repo = os.path.join(code, "notes-repo")
    w(os.path.join(repo, "spec.md"), SPEC)
    w(os.path.join(repo, "a.md"), "note a\n")
    git(repo, "init", "-q")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "contract fixture")
    w(os.path.join(repo, "a.md"), "note a\nstash me\n")
    git(repo, "stash", "push", "-q", "-m", "contract stash")
    w(os.path.join(repo, "a.md"), "note a\nuncommitted\n")
    w(os.path.join(repo, "b-untracked.md"), "untracked note\n")
    w(os.path.join(code, "current", "spec.md"), SPEC.replace("notes-repo spec", "current spec"))
    os.makedirs(os.path.join(top, "archive"))
    w(os.path.join(top, "living", "history.md"), "# notes: history\n")
    w(os.path.join(top, "discovery.json"), json.dumps({"roots": [top], "exclude": [os.path.join(top, "archive")]}))
    w(os.path.join(top, "hold.yaml"), "hold: [migration]\n")
    for name in ("site-old", "notes-repo"):
        w(os.path.join(top, "approval-%s.json" % name), json.dumps({
            "source": os.path.join(code, name), "dest": os.path.join(top, "archive", "notes", name),
            "approved_by": "contract operator", "approved_at": "2026-11-07T00:00:00Z"}))
    old = time.time() - 3 * 3600
    for d, dirs, files in os.walk(top):
        for n in dirs + files:
            os.utime(os.path.join(d, n), (old, old), follow_symlinks=False)
    return top
