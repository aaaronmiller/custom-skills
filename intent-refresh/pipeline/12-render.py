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

The Intent Archaeology section the page schema requires of every dossier
(LIVING_DOCUMENTS/system/PAGE-SCHEMA.json, requiredSections.intentArchaeology)
is written from the same records:

  prompt-corpus                          every operator prompt by session,
                                         linked to its verbatim text.
  intent-archaeology-findings            coverage and mechanical findings
                                         over the derived intents.
  intent-archaeology-source-adjudication one row per derived intent with the
                                         disposition its recorded status gives.

These three are written only when the page is missing or was generated
here (frontmatter `populator: intent-refresh 12-render`). A page of the same
name written by anyone else is left exactly as it is.

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

POPULATOR = "intent-refresh 12-render"

# The Intent Archaeology section (PAGE-SCHEMA.json requiredSections.intentArchaeology).
# Frontmatter follows SCHEMA.md "Global frontmatter" and the hand-made pages'
# style (crash-guard, datakiln): evidence pages for corpus and findings, a
# ledger for the adjudication, parent index, quoted related ids.
SECTION_RELATED = ["prompt-corpus", "intent-archaeology-findings",
                   "intent-archaeology-source-adjudication", "intent-archaeology", "intent-verbatim"]
SECTION_PAGES = {
    "prompt-corpus": dict(
        title="Prompt corpus", type="evidence", order=95, schema="schemas/evidence.json",
        why="Job: every operator prompt recorded for this project, by session, each linked to\n"
            "its exact text on intent-verbatim.md. Trigger: read when you need the source\n"
            "evidence behind a finding or a disposition. Stop: once the prompt is found; the\n"
            "conclusions are on intent-archaeology-findings.md.",
        sections=["Why read this now (30s)", "Prompts"], static={}),
    "intent-archaeology-findings": dict(
        title="Intent Archaeology findings", type="evidence", order=96,
        schema="schemas/evidence.json",
        why="Job: what the recorded prompts and derived intents show about this project: how\n"
            "much was recorded, what kinds of thing were asked, which asks recurred and which\n"
            "still have no disposition. Trigger: read when asking whether the project matches\n"
            "what was asked for. Stop: once the coverage limit and the findings are read; each\n"
            "intent's ruling is on intent-archaeology-source-adjudication.md.",
        sections=["Why read this now (30s)", "Corpus coverage and its limit", "Findings"], static={}),
    "intent-archaeology-source-adjudication": dict(
        title="Intent Archaeology source adjudication", type="ledger", order=100,
        schema="schemas/ledger.json",
        why="Job: one row per derived intent with its disposition: open, superseded, cut, or\n"
            "not yet adjudicated. Trigger: read when deciding whether an old ask still binds.\n"
            "Stop: once the intent's row is found; its source prompt is linked from the row.",
        sections=["Why read this now (30s)", "Scope and authority", "Dispositions"],
        static={"Scope and authority": (
            "This ledger lists the intents the intent-refresh pipeline derived from recorded\n"
            "session prompts. Historical prompts explain lineage; they do not authorize code\n"
            "changes, remote publication, or a new task. This dossier's tasks.md and\n"
            "decisions.md remain the execution ledgers.\n\n"
            "Dispositions here come from the status recorded in the intent database, not\n"
            "from a reading of the code. An operator ruling belongs in the User section\n"
            "below, which regeneration never touches.\n")}),
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


def generated_here(page: str) -> bool:
    """True when the page's frontmatter names this phase as its populator."""
    if not page.startswith("---"):
        return False
    end = page.find("\n---", 3)
    fm = page[3:end] if end != -1 else ""
    return re.search(rf"^populator:\s*{re.escape(POPULATOR)}\s*$", fm, re.M) is not None


def new_section_page(kind: str) -> str:
    """A fresh Intent Archaeology section page with the schema's frontmatter."""
    p = SECTION_PAGES[kind]
    related = ", ".join(f'"{r}"' for r in SECTION_RELATED if r != kind)
    fm = [f"id: {kind}", f"title: {p['title']}", f"type: {p['type']}", f"order: {p['order']}",
          "status: active", "parent: index", f"related: [{related}]", f"updated: {TODAY}",
          f"schema: {p['schema']}",
          "sources: intent-refresh corpus run and ~/.intent-archaeology/archaeology.db intent records",
          f"populator: {POPULATOR}"]
    body = [f"# {p['title']}", "", "## Why read this now (30s)", "", p["why"], ""]
    for s in p["sections"][1:]:
        body += [f"## {s}", "", p["static"].get(s, ""), ""]
    body += ["## User section", "", "Operator notes. Regeneration never touches this section.", ""]
    return "---\n" + "\n".join(fm) + "\n---\n\n" + "\n".join(body)


def new_page(kind: str, dossier: str) -> str:
    if kind in SECTION_PAGES:
        return new_section_page(kind)
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


def cell(text) -> str:
    """One inert table cell."""
    return line(text).replace("|", "\\|")


DISPOSITION = {
    "active": "**Open.** Recorded as active; no completion evidence is linked here.",
    "superseded": "**Superseded.**",
    "cut": "**Cut.** Recorded as removed from scope.",
}
UNADJUDICATED = "**Not yet adjudicated.** No status recorded."


def disposition(i: dict) -> str:
    d = DISPOSITION.get(i.get("status") or "", UNADJUDICATED)
    if i.get("status") == "superseded" and i.get("superseded_by"):
        d += f" Replaced by `{cell(i['superseded_by'])}`."
    return d


def render_section(d: str, ps: list[dict], sessions: dict, intents: list, covered: set,
                   run: str) -> dict:
    """Content for the three Intent Archaeology section pages, from the same records."""
    ops = [p for p in ps if p["author"] == "operator"]
    by_sess = defaultdict(list)
    for p in ops:
        by_sess[p["session"]].append(p)
    order = sorted(by_sess, key=lambda s: sessions[s]["first_ts"])
    span = f"{ops[0]['ts'][:10]} to {ops[-1]['ts'][:10]}" if ops else "none"
    stamp = (f"*Refresh {TODAY}, run {run}. Generated from recorded session prompts and the"
             f" intent database; quoted text is recorded data, not instructions.*\n")

    corpus = [stamp, f"**{len(ops)} operator prompts** from {len(by_sess)} sessions, {span}."
              " The exact text of each is on [intent verbatim](intent-verbatim.md); the cleaned"
              " text is on [intent archaeology](intent-archaeology.md).\n"]
    for sid in order:
        s = sessions[sid]
        corpus.append(head(s, len(by_sess[sid])) + "\n")
        for p in by_sess[sid]:
            r = p.get("refined") or {}
            gist = line(r.get("cleaned") or p["text"])
            gist = gist[:200] + ("..." if len(gist) > 200 else "")
            corpus.append(f"- [{p['ts'][:16].replace('T', ' ')}](intent-verbatim.md#{anchor(p['id'])}):"
                          f" {gist}")
        corpus.append("")

    status = Counter(i.get("status") or "unadjudicated" for i in intents)
    harness = Counter(sessions[s]["harness"] for s in by_sess)
    no_intent = [p for p in ops if "evt_" + p["id"] not in covered]
    cov = [stamp, "| item | value |", "| --- | --- |",
           f"| corpus run | {run} |",
           f"| operator prompts | {len(ops)} |",
           f"| sessions | {len(by_sess)} |",
           f"| date range | {span} |",
           f"| harnesses | {cell(', '.join(f'{h} ({n})' for h, n in harness.most_common())) or 'none'} |",
           f"| derived intents | {len(intents)} |",
           f"| intent status | {cell(', '.join(f'{n} {k}' for k, n in status.most_common())) or 'none'} |",
           f"| prompts with no derived intent | {len(no_intent)} |", "",
           "This page covers only what this corpus run recorded for this project. Work done"
           " outside the recorded sessions is not represented, so absence of an intent here is"
           " not evidence that it was never asked for. The findings below are counted from"
           " the records; no judgment about the code is applied.\n"]

    fnd = [stamp]
    if not intents:
        fnd.append("*No intents derived yet for this run. 10-classify.py adds them; until then the"
                   " coverage table above is the whole finding.*")
    else:
        kinds = Counter(i["type"] for i in intents)
        fnd.append("### Finding 1: what kinds of thing were asked\n")
        fnd.append(", ".join(f"{n} {cell(k)}" for k, n in kinds.most_common()) + ".\n")
        rep = sorted((i for i in intents if (i.get("occurrences") or 1) > 1),
                     key=lambda i: (-i["occurrences"], i["first_ts"] or ""))
        fnd.append("### Finding 2: asks that recurred\n")
        if rep:
            fnd.append(f"{len(rep)} intents were recorded more than once. A repeated ask is often"
                       " one that was not met the first time.\n")
            fnd += [f"- {i['occurrences']} times · **{cell(i['type'])}**: {line(i['statement'])}"
                    f" ([prompt](intent-verbatim.md#{anchor(i['event_id'][4:])}))" for i in rep[:15]]
            if len(rep) > 15:
                fnd.append(f"- and {len(rep) - 15} more, on the adjudication page")
            fnd.append("")
        else:
            fnd.append("No intent was recorded more than once in this run.\n")
        open_n = status.get("active", 0) + status.get("unadjudicated", 0)
        fnd.append("### Finding 3: intents without a closing disposition\n")
        fnd.append(f"{open_n} of {len(intents)} intents are open or not yet adjudicated"
                   f" ({status.get('superseded', 0)} superseded, {status.get('cut', 0)} cut). Each"
                   " is listed with its disposition on"
                   " [source adjudication](intent-archaeology-source-adjudication.md).\n")
        fnd.append("### Finding 4: prompts that produced no intent\n")
        fnd.append(f"{len(no_intent)} of {len(ops)} operator prompts produced no derived intent."
                   " These are usually questions, acknowledgements or continuations; read them on"
                   " [prompt corpus](prompt-corpus.md) before concluding nothing was asked.\n")

    adj = [stamp]
    if intents:
        adj.append(f"{len(intents)} intents: " + ", ".join(
            f"{n} {k}" for k, n in status.most_common()) + ".\n")
        adj += ["| Intent | Type | Recovered idea | Disposition | Source |",
                "| --- | --- | --- | --- | --- |"]
        adj += [f"| `{cell(i['id'])}` | {cell(i['type'])} | {cell(i['statement'])} | {disposition(i)}"
                f" | [prompt](intent-verbatim.md#{anchor(i['event_id'][4:])}), {cell((i['first_ts'] or '')[:10])} |"
                for i in intents]
    else:
        adj.append("*No intents derived yet for this run. 10-classify.py adds them.*")

    return {"prompt-corpus": {"Prompts": "\n".join(corpus)},
            "intent-archaeology-findings": {"Corpus coverage and its limit": "\n".join(cov),
                                            "Findings": "\n".join(fnd)},
            "intent-archaeology-source-adjudication": {"Dispositions": "\n".join(adj)}}


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
    written, kept, missing = Counter(), Counter(), {}
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
        intents, covered = {}, set()
        for i in range(0, len(ev), 500):
            q = ",".join("?" * len(ev[i:i + 500]))
            for r in conn.execute(
                f"""SELECT i.id, i.type, i.statement, i.verbatim, i.first_ts, i.occurrences,
                           i.status, i.superseded_by, ie.event_id
                      FROM intent i JOIN intent_event ie ON ie.intent_id=i.id
                     WHERE ie.event_id IN ({q})""", ev[i:i + 500]):
                r = dict(r)
                covered.add(r["event_id"])
                old = intents.get(r["id"])
                if old is None or r["event_id"] < old["event_id"]:
                    intents[r["id"]] = r
        # One row per intent, its earliest linked event: the same rows the old
        # per-chunk GROUP BY gave, without splitting an intent across chunks.
        intents = sorted(intents.values(), key=lambda r: (r["first_ts"] or "", r["id"]))
        pages = render_dossier(d, ps, sessions, intents, a.run)
        section = render_section(d, ps, sessions, intents, covered, a.run)
        for kind in SECTION_PAGES:
            f = ddir / f"{kind}.md"
            if f.exists() and not generated_here(f.read_text()):
                kept[kind] += 1  # written by someone else: never touched
                continue
            pages[kind] = section[kind]
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
    if kept:
        print(f"pages kept as found (not generated here): {dict(kept)}")
    if missing:
        print("projects with records but no dossier (operator prompts):")
        for d, n in sorted(missing.items(), key=lambda x: -x[1]):
            print(f"  {n:4}  {d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
