"""Shared reader for a collected and refined corpus run (07 and 08 output).

The project assignment rule lives here once, so the loader (09) and the page
renderer (12) can never disagree:

  1. A session whose working folder matched a dossier (07's deterministic
     rungs) gives that dossier to every prompt in it.
  2. Otherwise the model's per-prompt project from 08 is used.
  3. A per-prompt "unclassified" below 0.5 confidence falls back to the
     model's session project.
  4. Anything still without a project is "unclassified".

"sysadmin" and "unclassified" are real destinations: dossiers named
system-administration and unclassified-sessions. "new:<name>" means a project
with no dossier yet.
"""
from __future__ import annotations

import json
from pathlib import Path

DETERMINISTIC = {"cwd-in-dossier-root", "repo-name-matches-dossier"}
FALLBACK_DOSSIER = {"sysadmin": "system-administration",
                    "unclassified": "unclassified-sessions"}


def dossier_of(project: str | None) -> str:
    if not project:
        return FALLBACK_DOSSIER["unclassified"]
    if project.startswith("code:"):
        return "new:" + project[5:]
    return FALLBACK_DOSSIER.get(project, project)


def load(run: Path) -> tuple[list[dict], dict[str, dict]]:
    """Return (prompts, sessions), each prompt carrying its refinement and final dossier."""
    sessions = {}
    for line in open(run / "sessions.jsonl"):
        s = json.loads(line)
        sessions[s["id"]] = s
    refined, sess_ref = {}, {}
    for f in sorted((run / "refined").glob("chunk-*.json")):
        ans = json.loads(f.read_text())
        for r in ans.get("prompts", []):
            if isinstance(r, dict) and r.get("id"):
                refined[r["id"]] = dict(r, model=ans.get("model"))
        for s in ans.get("sessions", []):
            if isinstance(s, dict) and s.get("id"):
                sess_ref[s["id"]] = s
    prompts = []
    for line in open(run / "prompts.jsonl"):
        p = json.loads(line)
        s = sessions[p["session"]]
        r = refined.get(p["id"], {})
        sr = sess_ref.get(p["session"], {})
        if s.get("rung") in DETERMINISTIC:
            proj, how = s["project"], "folder"
        elif r.get("project") and not (r["project"] == "unclassified"
                                       and (r.get("project_confidence") or 0) < 0.5):
            proj, how = r["project"], "model-prompt"
        elif sr.get("project"):
            proj, how = sr["project"], "model-session"
        elif s.get("project"):
            proj, how = s["project"], "folder-no-dossier"
        else:
            proj, how = "unclassified", "none"
        p.update(refined=r or None, dossier=dossier_of(proj), assigned_by=how,
                 author=(r.get("author") if r else None)
                 or ("agent-brief" if p["origin"] == "dispatched" else "operator"))
        prompts.append(p)
    for sid, s in sessions.items():
        s["summary"] = (sess_ref.get(sid) or {}).get("summary")
        s["summary_project"] = (sess_ref.get(sid) or {}).get("project")
    return prompts, sessions
