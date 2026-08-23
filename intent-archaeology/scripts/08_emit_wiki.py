#!/usr/bin/env python3
"""Phase 8: emit Karpathy-style wiki from the SQLite state.

Outputs markdown files to --out. Uses templates in assets/templates/.
Run lint_wiki.py after to validate.

Usage:
    python scripts/08_emit_wiki.py \
        --db ~/.intent-archaeology/state.db \
        --out ~/intent-wiki/
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from string import Template

TEMPLATES = Path(__file__).parent.parent / "assets" / "templates"


def load_template(name: str) -> Template:
    return Template((TEMPLATES / name).read_text())


def emit_master_index(conn: sqlite3.Connection, out_dir: Path) -> None:
    projects = conn.execute(
        "SELECT name, lifecycle, era, last_audited FROM projects ORDER BY name"
    ).fetchall()
    rows = []
    for name, lifecycle, era, last_audited in projects:
        rows.append(f"| [{name}](projects/{name}.md) | {lifecycle or '-'} | {era or '-'} | {last_audited or '-'} |")
    tmpl = load_template("master_index.md.tmpl")
    content = tmpl.substitute(
        generated_at=datetime.now().isoformat(),
        project_count=len(projects),
        project_rows="\n".join(rows) or "| (no projects) | - | - | - |",
    )
    (out_dir / "index.md").write_text(content)


def emit_project_pages(conn: sqlite3.Connection, out_dir: Path) -> None:
    out_dir = out_dir / "projects"
    out_dir.mkdir(exist_ok=True)
    projects = conn.execute(
        "SELECT id, name, path, description, era, lifecycle, canonical_prd_path, spec_lineage FROM projects"
    ).fetchall()
    tmpl = load_template("project_page.md.tmpl")
    for pid, name, path, desc, era, lifecycle, canonical_prd, spec_lineage_json in projects:
        # Get status vector
        sv = conn.execute(
            "SELECT completed, in_progress, drifted, superseded, abandoned, not_begun FROM status_vectors WHERE project_id = ? ORDER BY computed_at DESC LIMIT 1",
            (pid,),
        ).fetchone()
        sv_line = " | ".join(f"{c}={v:.2f}" for c, v in zip(
            ["completed", "in_progress", "drifted", "superseded", "abandoned", "not_begun"],
            sv or [0]*6,
        ) if v > 0) or "(no data)"
        # Get intent type frequency
        type_freq = conn.execute(
            "SELECT type, COUNT(*) FROM intents WHERE project_id = ? GROUP BY type ORDER BY COUNT(*) DESC",
            (pid,),
        ).fetchall()
        type_freq_lines = "\n".join(f"- {t}: {n}" for t, n in type_freq) or "- (no intents)"
        # Get prompts (newest-first, top 20)
        prompts = conn.execute(
            "SELECT created_at, prompt_text FROM prompts WHERE project_id = ? ORDER BY created_at DESC LIMIT 20",
            (pid,),
        ).fetchall()
        prompt_lines = "\n".join(f"- `{c}`: {t[:200]}" for c, t in prompts) or "- (no prompts)"

        content = tmpl.substitute(
            project_name=name,
            project_path=path,
            description=desc or "(no description)",
            era=era or "-",
            lifecycle=lifecycle or "-",
            canonical_prd=canonical_prd or "(none)",
            spec_lineage=spec_lineage_json or "[]",
            status_vector=sv_line,
            type_frequency=type_freq_lines,
            recent_prompts=prompt_lines,
            generated_at=datetime.now().isoformat(),
        )
        (out_dir / f"{name}.md").write_text(content)


def emit_cross_cutting(conn: sqlite3.Connection, out_dir: Path) -> None:
    """Emit cross-cutting pages: standing_constraints, repeated_corrections,
    abandoned, corrections_by_era."""
    out_dir = out_dir / "cross-cutting"
    out_dir.mkdir(exist_ok=True)

    # standing_constraints: intents with type='constraint', grouped by summary
    constraints = conn.execute(
        """SELECT summary, COUNT(*) as n FROM intents
           WHERE type = 'constraint' GROUP BY summary ORDER BY n DESC LIMIT 50""",
    ).fetchall()
    lines = "\n".join(f"- ({n}x) {s}" for s, n in constraints) or "- (none)"
    tmpl = load_template("standing_constraints.md.tmpl")
    (out_dir / "standing-constraints.md").write_text(
        tmpl.substitute(generated_at=datetime.now().isoformat(), items=lines)
    )

    # repeated_corrections: type='correction', grouped by summary
    corrections = conn.execute(
        """SELECT summary, COUNT(*) as n FROM intents
           WHERE type = 'correction' GROUP BY summary HAVING n > 2 ORDER BY n DESC LIMIT 50""",
    ).fetchall()
    lines = "\n".join(f"- ({n}x) {s}" for s, n in corrections) or "- (none)"
    tmpl = load_template("repeated_corrections.md.tmpl")
    (out_dir / "repeated-corrections.md").write_text(
        tmpl.substitute(generated_at=datetime.now().isoformat(), items=lines)
    )

    # abandoned: type='scope-cut'
    cuts = conn.execute(
        """SELECT project_id, summary FROM intents WHERE type = 'scope-cut' ORDER BY project_id""",
    ).fetchall()
    lines = "\n".join(f"- project {pid}: {s}" for pid, s in cuts) or "- (none)"
    tmpl = load_template("abandoned.md.tmpl")
    (out_dir / "abandoned.md").write_text(
        tmpl.substitute(generated_at=datetime.now().isoformat(), items=lines)
    )

    # corrections_by_era: corrections grouped by project era
    corr_era = conn.execute(
        """SELECT p.era, COUNT(*) FROM intents i
           JOIN projects p ON i.project_id = p.id
           WHERE i.type = 'correction' GROUP BY p.era ORDER BY p.era""",
    ).fetchall()
    lines = "\n".join(f"- era {e}: {n} corrections" for e, n in corr_era) or "- (none)"
    tmpl = load_template("corrections_by_era.md.tmpl")
    (out_dir / "corrections-by-era.md").write_text(
        tmpl.substitute(generated_at=datetime.now().isoformat(), items=lines)
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", required=True)
    ap.add_argument("--out", required=True, help="Output directory for wiki markdown")
    args = ap.parse_args()

    out_dir = Path(args.out).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(args.db) as conn:
        emit_master_index(conn, out_dir)
        emit_project_pages(conn, out_dir)
        emit_cross_cutting(conn, out_dir)
    print(f"OK: wiki emitted to {out_dir}", file=sys.stderr)
    print(f"Run scripts/lint_wiki.py --wiki {out_dir} to validate.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
