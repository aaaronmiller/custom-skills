#!/usr/bin/env python3
"""Phase 7: render the prompt wiki.

Everything written here is derived and regenerable. Files live under
derived/prompt-wiki/ and every one is wrapped in a generated fence. Human
commentary goes in human/notes/ and is never touched by this script.

The per-project pages are the obvious output and the least interesting one.
The value is in the cross-cutting pages, because those are the views you
cannot get by reading any single session.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.common import DERIVED, HUMAN, PIPELINE_VERSION, connect, log, now, report  # noqa: E402

OPEN = "<!-- GENERATED:intent-archaeology BEGIN. Do not edit inside this fence. -->"
CLOSE = "<!-- GENERATED:intent-archaeology END -->"


def fence(body: str) -> str:
    return f"{OPEN}\n\n{body}\n\n{CLOSE}\n"


def head(title: str, desc: str) -> str:
    return (f"---\ngenerated: {now()}\npipeline_version: {PIPELINE_VERSION}\n"
            f"owner: machine\n---\n\n# {title}\n\n{desc}\n\n")


def table(rows: list[tuple], cols: list[str]) -> str:
    if not rows:
        return "_Nothing recorded yet._\n"
    out = ["| " + " | ".join(cols) + " |",
           "|" + "|".join("---" for _ in cols) + "|"]
    for r in rows:
        cells = [str(c).replace("|", "\\|").replace("\n", " ")[:300] for c in r]
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out) + "\n"


def write(path: Path, title: str, desc: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(head(title, desc) + fence(body))


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase 7: render the prompt wiki")
    ap.add_argument("--out", default=str(DERIVED / "prompt-wiki"))
    args = ap.parse_args()

    conn = connect()
    out = Path(args.out)
    log(conn, "render", "start", str(out))

    q = conn.execute

    constraints = q(
        """SELECT i.statement, i.occurrences, p.id project, i.last_ts
             FROM intent i JOIN project p ON p.id=i.project_id
            WHERE i.type='directive.constraint' AND i.superseded_by IS NULL
            ORDER BY i.occurrences DESC, i.last_ts DESC LIMIT 200"""
    ).fetchall()
    write(out / "constraints.md", "Standing constraints",
          "Your de facto constitution, discovered rather than authored. "
          "Ranked by how often you had to say it. High counts belong in "
          "`constitution.md` and `AGENTS.md`.",
          table([(r["statement"], r["occurrences"], r["project"]) for r in constraints],
                ["Constraint", "Times said", "Project"]))

    corrections = q(
        """SELECT i.statement, i.occurrences, p.id project
             FROM intent i JOIN project p ON p.id=i.project_id
            WHERE i.type='correction.behavior' AND i.occurrences >= 2
              AND i.superseded_by IS NULL
            ORDER BY i.occurrences DESC LIMIT 200"""
    ).fetchall()
    write(out / "corrections.md", "Repeated corrections",
          "Every behavioural correction you have issued more than once. Each row "
          "is a rule you keep having to repeat, which means it is not in your "
          "standing instructions yet. This is the most directly actionable page here.",
          table([(r["statement"], r["occurrences"], r["project"]) for r in corrections],
                ["Correction", "Times repeated", "Project"]))

    abandoned = q(
        """SELECT i.statement, p.id project, i.last_ts
             FROM intent i JOIN project p ON p.id=i.project_id
            WHERE i.type='scope.cut' ORDER BY i.last_ts DESC LIMIT 300"""
    ).fetchall()
    write(out / "abandoned.md", "Abandoned",
          "Things you explicitly cut. This page exists so nothing, human or agent, "
          "resurrects work you already decided against. `scope.cut` is terminal.",
          table([(r["statement"], r["project"], (r["last_ts"] or "")[:10]) for r in abandoned],
                ["Cut", "Project", "When"]))

    deferred = q(
        """SELECT i.statement, p.id project, i.last_ts FROM intent i
             JOIN project p ON p.id=i.project_id
            WHERE i.type='scope.defer' AND i.superseded_by IS NULL
            ORDER BY i.last_ts DESC LIMIT 300"""
    ).fetchall()
    write(out / "deferred.md", "Deferred",
          "Postponed rather than rejected. This is a backlog, not a gap list.",
          table([(r["statement"], r["project"], (r["last_ts"] or "")[:10]) for r in deferred],
                ["Deferred", "Project", "When"]))

    questions = q(
        """SELECT i.statement, p.id project FROM intent i
             JOIN project p ON p.id=i.project_id
            WHERE i.type='question' AND i.superseded_by IS NULL
            ORDER BY i.occurrences DESC LIMIT 200"""
    ).fetchall()
    write(out / "questions.md", "Open questions",
          "Things you asked and, so far as the record shows, kept asking.",
          table([(r["statement"], r["project"]) for r in questions], ["Question", "Project"]))

    echoes = q(
        """SELECT i.statement, COUNT(DISTINCT i.project_id) n,
                  GROUP_CONCAT(DISTINCT i.project_id) projects
             FROM intent i WHERE i.superseded_by IS NULL
            GROUP BY LOWER(i.statement) HAVING n >= 2 ORDER BY n DESC LIMIT 150"""
    ).fetchall()
    write(out / "echoes.md", "Cross-project echoes",
          "Intents that recur across projects. These are your architectural priors, "
          "and they are the mechanism for propagating an improvement made on one "
          "project to the others that share it.",
          table([(r["statement"], r["n"], r["projects"]) for r in echoes],
                ["Intent", "Projects", "Where"]))

    projects = q(
        """SELECT p.id, p.description, p.lifecycle, p.description_stale,
                  COUNT(DISTINCT s.id) sessions,
                  COUNT(DISTINCT i.id) intents
             FROM project p
             LEFT JOIN session s ON s.project_id = p.id
             LEFT JOIN intent i ON i.project_id = p.id AND i.superseded_by IS NULL
            WHERE p.kind IN ('project','monorepo')
            GROUP BY p.id ORDER BY intents DESC, sessions DESC"""
    ).fetchall()

    for r in projects:
        if not r["intents"]:
            continue
        rows = q(
            """SELECT type, statement, occurrences, status, first_ts
                 FROM intent WHERE project_id=? AND superseded_by IS NULL
                ORDER BY type, occurrences DESC""", (r["id"],)).fetchall()
        write(out / "projects" / f"{r['id']}.md", r["id"],
              (r["description"] or "_No description recovered._")
              + ("\n\n**Description looks stale**: the code is much newer than the docs."
                 if r["description_stale"] else ""),
              table([(x["type"], x["statement"], x["occurrences"],
                      x["status"] or "unassessed", (x["first_ts"] or "")[:10]) for x in rows],
                    ["Type", "Intent", "Times", "Status", "First said"]))

    index_rows = [(f"[{r['id']}](projects/{r['id']}.md)" if r["intents"] else r["id"],
                   r["lifecycle"] or "underived", r["sessions"] or 0, r["intents"] or 0)
                  for r in projects]
    body = table(index_rows, ["Project", "Lifecycle", "Sessions", "Intents"])
    body += ("\n## Cross-cutting\n\n"
             "- [Standing constraints](constraints.md)\n"
             "- [Repeated corrections](corrections.md)\n"
             "- [Abandoned](abandoned.md)\n"
             "- [Deferred](deferred.md)\n"
             "- [Open questions](questions.md)\n"
             "- [Cross-project echoes](echoes.md)\n")
    write(out / "index.md", "Prompt wiki",
          "Built entirely from your own submitted prompts. Every statement here is "
          "normalized for reading; the verbatim span is stored immutably in the "
          "database and is never edited. Everything in this tree is regenerable, "
          "so do not hand-edit it. Your own commentary belongs in "
          f"`{HUMAN / 'notes'}`, which no script writes to.", body)

    (HUMAN / "notes").mkdir(parents=True, exist_ok=True)

    log(conn, "render", "done")
    report("Rendered", [
        ("index", str(out / "index.md")),
        ("projects with intents", sum(1 for r in projects if r["intents"])),
        ("standing constraints", len(constraints)),
        ("repeated corrections", len(corrections)),
        ("abandoned items", len(abandoned)),
        ("cross-project echoes", len(echoes)),
        ("your notes (never overwritten)", str(HUMAN / "notes")),
    ])
    print("\nRead corrections.md first. It is a to-do list for your standing instructions.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
