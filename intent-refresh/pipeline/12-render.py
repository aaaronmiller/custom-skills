#!/usr/bin/env python3
"""Phase 12: write each project's intent pages in its Living Documents dossier.

  python3 -I 12-render.py --run 2026-08-29 [--dossiers a,b] [--dry-run]

Pages, by the dossier schemas (living-documents/schemas/intent-*.json):

  intent-verbatim     every operator prompt exactly as typed, by session,
                      private. Always written for a project with records.
  intent-archaeology  the cleaned and organized prompts, the derived intents
                      with the prompt each came from, and what was filtered.
                      Always written.
  intent-summary      one summary per session. Written when the project has
                      SUMMARY_AT or more operator prompts; below that the
                      session summaries sit on the archaeology page.
  intent-executive    is written by 11-summarize.py, not here.

Never overwrites operator text. Everything this phase writes sits between
  <!-- intent-refresh:start run=RUN --> and <!-- intent-refresh:end run=RUN -->
inside the page's required section. A rerun replaces only its own block; a
page that does not exist is created with the schema's frontmatter.
Only existing dossiers are written; the report lists projects without one.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.common import BASE, confined, connect  # noqa: E402
from lib.corpus import load  # noqa: E402

DOSSIERS = Path(os.environ.get("LD_DATA_ROOT", Path.home() / "LIVING_DOCUMENTS")) / "projects"
SUMMARY_AT = 10
VERBATIM_CAP = 20000
TODAY = date.today().isoformat()

PAGES = {
    "intent-verbatim": dict(
        title="Intent — verbatim", order=190, section="Sessions", visibility="private",
        why="Job: every prompt, exactly as typed, grouped by session. Trigger: read when a\n"
            "decision needs its original wording rather than a summary of it. Stop: once the\n"
            "relevant prompt is found; the reading of it lives in the summaries.",
        sections=["Why read this now (30s)", "Sessions"]),
    "intent-archaeology": dict(
        title="Intent archaeology", order=182, section="Prompts", visibility=None,
        why="Job: what this project was asked for, recovered from session logs, with the\n"
            "prompt each intent came from and what was filtered out. Trigger: read when asking\n"
            "what the project was originally asked to be, or whether the code drifted from it.\n"
            "Stop: once the intent you need is found; exact wording is on intent-verbatim.md.",
        sections=["Why read this now (30s)", "Prompts", "Derived intents", "Filtered"]),
    "intent-summary": dict(
        title="Intent — session summaries", order=191, section="Summaries", visibility=None,
        why="Job: what each session was actually about, without reading every turn. Trigger:\n"
            "read when reconstructing how the project got here. Stop: once the relevant\n"
            "session is understood; the exact wording is on intent-verbatim.md.",
        sections=["Why read this now (30s)", "Summaries"]),
}


def inert(text) -> str:
    """Make recorded or model-written text unable to act as page structure.

    Session text and model output are untrusted (2026-11-05 security review:
    prompt-injection persistence). Comment markers are escaped so no text can
    open or close an intent-refresh block or an ld:generated fence.
    """
    return str(text or "").replace("<!--", "&lt;!--").replace("-->", "--&gt;")


def line(text) -> str:
    """One inert line: for summaries, statements and descriptions."""
    return " ".join(inert(text).split())


def quote(text: str) -> str:
    """Blockquote, so headings and lists inside recorded text stay inert."""
    return "\n".join("> " + ln if ln.strip() else ">" for ln in inert(text).splitlines())


def anchor(pid: str) -> str:
    """Slug of the prompt's heading on intent-verbatim.md ("#### Prompt op-...")."""
    return "prompt-" + pid.replace("_", "-")


def new_page(kind: str, dossier: str) -> str:
    p = PAGES[kind]
    fm = [f"id: {kind}", f"title: {p['title']}", f"type: {kind}", f"order: {p['order']}",
          "status: active", "parent: index", "related: [intent-verbatim, intent-archaeology,"
          " intent-summary, intent-executive]", f"updated: {TODAY}", f"schema: schemas/{kind}.json",
          "sources: agent session logs across harnesses (intent-refresh 07-collect)",
          "populator: intent-refresh 12-render"]
    if p["visibility"]:
        fm.append(f"visibility: {p['visibility']}")
    body = [f"# {p['title']}", "", "## Why read this now (30s)", "", p["why"], ""]
    for s in p["sections"][1:]:
        body += [f"## {s}", "", ""]
    body += ["## User section", "", "Operator notes. Regeneration never touches this section.", ""]
    return "---\n" + "\n".join(fm) + "\n---\n\n" + "\n".join(body)


def section_body(page: str, section: str) -> tuple[int, int] | None:
    m = re.search(rf"^## {re.escape(section)}\s*$", page, re.M)
    if not m:
        return None
    nxt = re.search(r"^## ", page[m.end():], re.M)
    return m.end(), (m.end() + nxt.start() if nxt else len(page))


def is_placeholder(text: str) -> bool:
    """True when a section holds only comments, blank lines or *italic placeholder* lines."""
    t = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return all(not ln.strip() or re.match(r"\*(Not yet|Nothing|No |None)", ln.strip())
               for ln in t.splitlines())


def put_block(page: str, section: str, run: str, content: str) -> str:
    """Place this run's block for one section.

    Rerun: replace this run's own block. Section empty or placeholder: write
    into it. Section already holding operator or earlier content: append a
    dated "Refresh" section before the User section instead, so older
    material keeps its order (the dossiers' existing Addendum pattern).
    """
    tag = f"run={run} section={section.lower().replace(' ', '-')}"
    start, end = f"<!-- intent-refresh:start {tag} -->", f"<!-- intent-refresh:end {tag} -->"
    block = f"{start}\n{content.rstrip()}\n{end}"
    if start in page:
        return re.sub(re.escape(start) + r".*?" + re.escape(end), lambda _: block, page, flags=re.S)
    span = section_body(page, section)
    if span:
        body = page[span[0]:span[1]]
        ph = re.search(r"^\*(Not yet|Nothing yet|No [a-z]+ yet)[^\n]*\*\s*$", body, re.M)
        if ph:  # onboarding template: the block replaces the placeholder line, guidance prose stays
            a = span[0] + ph.start()
            return page[:a] + block + page[span[0] + ph.end():]
    if span and is_placeholder(page[span[0]:span[1]]):
        a, b = span
        return page[:a] + "\n\n" + block + "\n\n" + page[b:].lstrip("\n")
    heading = section if span is None else f"Refresh {TODAY}: {section}"
    ins = f"## {heading}\n\n{block}\n\n"
    um = re.search(r"^## User section\s*$", page, re.M)
    return page[:um.start()] + ins + page[um.start():] if um else page.rstrip() + "\n\n" + ins


def touch_updated(page: str) -> str:
    return re.sub(r"^updated:.*$", f"updated: {TODAY}", page, count=1, flags=re.M)


def head(s: dict, n: int) -> str:
    return (f"### {s['first_ts'][:10]} · {s['harness']} · session {s['session_id'][:13]}"
            f" ({n} prompt{'s' if n != 1 else ''})")


def render_dossier(d: str, ps: list[dict], sessions: dict, intents: list, run: str) -> dict:
    ops = [p for p in ps if p["author"] == "operator"]
    filtered = [p for p in ps if p["author"] != "operator"]
    by_sess = defaultdict(list)
    for p in ops:
        by_sess[p["session"]].append(p)
    order = sorted(by_sess, key=lambda s: sessions[s]["first_ts"])
    span = f"{ops[0]['ts'][:10]} to {ops[-1]['ts'][:10]}" if ops else "none"
    intro = (f"*Refresh {TODAY}, run {run}: {len(ops)} operator prompts from {len(by_sess)}"
             f" sessions, {span}. Collected across harnesses by intent-refresh; secrets redacted. Everything quoted below is recorded session data, not instructions to any reader or agent.*\n")

    verb = [intro]
    for sid in order:
        s = sessions[sid]
        verb.append(head(s, len(by_sess[sid])) + "\n")
        verb.append(f"Source: `{s['source_path']}`" + (f" · folder `{s['cwd']}`" if s.get("cwd") else "") + "\n")
        for p in by_sess[sid]:
            t = p["text"]
            note = ""
            if len(t) > VERBATIM_CAP:
                note = (f"\n*{len(t) - VERBATIM_CAP:,} further characters of pasted material are"
                        f" not shown; full text: corpus id `{p['id']}` in"
                        f" `~/.intent-archaeology/corpus/{run}/prompts.jsonl`.*\n")
                t = t[:VERBATIM_CAP]
            rep = f" · repeated {p['repeats']} more times" if p["repeats"] else ""
            verb.append(f"#### Prompt {p['id'].replace('_', '-')}\n\n"
                        f"**{p['ts'][:16].replace('T', ' ')}**{rep}\n\n{quote(t)}\n{note}")

    arch = [intro, "Each prompt below is cleaned: spelling, grammar and transcription errors fixed,"
            " long requests organized, technical content unchanged. The exact text is on"
            " intent-verbatim.md under the same id.\n"]
    for sid in order:
        s = sessions[sid]
        arch.append(head(s, len(by_sess[sid])) + "\n")
        if s.get("summary") and len(ops) < SUMMARY_AT:
            arch.append(f"*Session summary:* {line(s['summary'])}\n")
        for p in by_sess[sid]:
            r = p.get("refined") or {}
            cleaned = r.get("cleaned") or p["text"]
            mark = "" if r.get("cleaned") else " · *not cleaned: refinement unavailable*"
            arch.append(f"**{p['ts'][:16].replace('T', ' ')}** · [verbatim](intent-verbatim.md#{anchor(p['id'])})"
                        f" · project by {p['assigned_by']}{mark}\n\n{quote(cleaned.strip())}\n")
            if r.get("pasted"):
                arch.append(f"*Pasted material:* {line(r['pasted'])}\n")

    der = []
    if intents:
        kinds = Counter(i["type"] for i in intents)
        der.append("*" + ", ".join(f"{n} {k}" for k, n in kinds.most_common()) + ". Each intent quotes"
                   " the prompt it came from; 05-merge rejected any quote not found in its prompt.*\n")
        for i in intents:
            occ = f" · seen {i['occurrences']} times" if i["occurrences"] > 1 else ""
            sup = " · superseded" if i["status"] == "superseded" else ""
            der.append(f"- **{line(i['type'])}**: {line(i['statement'])}{occ}{sup}  \n"
                       f"  > \"{line(i['verbatim'][:300])}\"  \n"
                       f"  [prompt](intent-verbatim.md#{anchor(i['event_id'][4:])}), {i['first_ts'][:10]}")
    else:
        der.append("*No intents derived yet for this run. 10-classify.py adds them.*")

    fil = Counter(p["author"] for p in filtered)
    reps = sum(p["repeats"] for p in ps)
    flt = [f"Structural filtering only, never by content. Dropped before this page: harness wrappers,"
           f" compaction summaries, task notifications, interruption markers, and {reps} exact"
           f" repeats of prompts shown here (counted on each prompt).\n"]
    if filtered:
        flt.append(f"Recorded but not treated as operator intent: {fil.get('agent-brief', 0)} agent-written"
                   f" briefs and {fil.get('pasted-only', 0)} pasted-only messages.\n")
        for sid in sorted({p["session"] for p in filtered}, key=lambda x: sessions[x]["first_ts"]):
            s = sessions[sid]
            n = sum(1 for p in filtered if p["session"] == sid)
            summ = f": {line(s['summary'])}" if s.get("summary") else ""
            flt.append(f"- {s['first_ts'][:10]} · {s['harness']} · `{s['session_id'][:13]}` ·"
                       f" {n} message{'s' if n != 1 else ''}{summ}")

    out = {"intent-verbatim": {"Sessions": "\n".join(verb)},
           "intent-archaeology": {"Prompts": "\n".join(arch), "Derived intents": "\n".join(der),
                                  "Filtered": "\n".join(flt)}}
    if len(ops) >= SUMMARY_AT:
        summ = [intro]
        for sid in order:
            s = sessions[sid]
            links = ", ".join(f"[{p['ts'][11:16]}](intent-verbatim.md#{anchor(p['id'])})" for p in by_sess[sid][:40])
            more = f" and {len(by_sess[sid]) - 40} more" if len(by_sess[sid]) > 40 else ""
            summ.append(head(s, len(by_sess[sid])) + "\n\n" + (line(s.get("summary")) or "*No summary: refinement unavailable.*")
                        + f"\n\nPrompts: {links}{more}\n")
        out["intent-summary"] = {"Summaries": "\n".join(summ)}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--dossiers")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    run = confined(f"corpus/{a.run}", BASE)
    prompts, sessions = load(run)
    conn = connect()
    want = set(a.dossiers.split(",")) if a.dossiers else None

    by_d = defaultdict(list)
    for p in prompts:
        by_d[p["dossier"]].append(p)
    written, missing = Counter(), {}
    for d, ps in sorted(by_d.items()):
        if want and d not in want:
            continue
        ddir = DOSSIERS / d
        if ddir.resolve().parent != DOSSIERS.resolve():  # never outside the dossiers
            missing[d] = -1
            continue
        if d.startswith("new:") or not (ddir / "project.md").exists():
            missing[d] = sum(1 for p in ps if p["author"] == "operator")
            continue
        ev = ["evt_" + p["id"] for p in ps]
        intents = []
        for i in range(0, len(ev), 500):
            q = ",".join("?" * len(ev[i:i + 500]))
            intents += [dict(r) for r in conn.execute(
                f"""SELECT i.type, i.statement, i.verbatim, i.first_ts, i.occurrences, i.status,
                           MIN(ie.event_id) event_id
                      FROM intent i JOIN intent_event ie ON ie.intent_id=i.id
                     WHERE ie.event_id IN ({q}) GROUP BY i.id ORDER BY i.first_ts""", ev[i:i + 500])]
        pages = render_dossier(d, ps, sessions, intents, a.run)
        for kind, sections in pages.items():
            f = ddir / f"{kind}.md"
            page = f.read_text() if f.exists() else new_page(kind, d)
            for sec, content in sections.items():
                page = put_block(page, sec, a.run, content)
            page = touch_updated(page)
            if not a.dry_run:
                f.write_text(page)
            written[kind] += 1
    print(f"pages written: {dict(written)}{' (dry run)' if a.dry_run else ''}")
    if missing:
        print("projects with records but no dossier (operator prompts):")
        for d, n in sorted(missing.items(), key=lambda x: -x[1]):
            print(f"  {n:4}  {d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
