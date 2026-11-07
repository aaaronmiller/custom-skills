#!/usr/bin/env python3
"""Organize recovered Notepad and Notepad++ notes into a sliced, titled, de-duplicated library.

Stages (each cached, so a monthly rerun only pays for new text):
  gather    collect every extracted note from every recovery run, plus saved scratch files
  dedup     drop exact copies and older versions contained in a newer one
  slice     split each note into candidate blocks, then ask a model to group blocks into
            separate notes, each with a title, kind, summary, projects and themes
  cluster   group near-identical slices across notes into one aggregate
  write     notes/<project>/<date>-<slug>-<id>.md with YAML frontmatter, sources/<doc>.md,
            catalog.json and a self-contained index.html

Usage: python3 -I organize.py [--recovery DIR] [--out DIR] [--model M] [--workers N] [--stage all|gather|plan]
The model runs on OpenCode Go (OPENCODE_GO_API_KEY). Secrets are redacted before any text leaves
this machine, and the library itself only ever holds redacted text.
"""
import argparse, concurrent.futures as cf, datetime as dt, hashlib, html, json, os, re, sys, time
import urllib.request, uuid
from pathlib import Path

HOME = Path("/home/cheta")
RECOVERY = HOME / "agent-notes/recovery"
OUT = HOME / "agent-notes/library"
LD_PROJECTS = HOME / "LIVING_DOCUMENTS/projects"
SCRATCH_ROOTS = ("/mnt/c/Users/Administrator/Downloads", "/mnt/c/Users/Administrator/Documents",
                 "/mnt/c/Users/Administrator/Desktop", "/home/cheta/tmp")
ENDPOINT = "https://opencode.ai/zen/go/v1/chat/completions"
UA = "notes-organizer/1.0"
MAX_SAVED = 1_500_000  # the Apple Notes export (11.7M chars) is its own corpus
SESSION = str(uuid.uuid4())

SECRET_RES = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S), "private-key"),
    (re.compile(r"\b(sk-(?:ant-|proj-|or-v1-)?[A-Za-z0-9_\-]{20,})"), "api-key"),
    (re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{30,})"), "github-token"),
    (re.compile(r"\b(github_pat_[A-Za-z0-9_]{40,})"), "github-token"),
    (re.compile(r"\b(AKIA[0-9A-Z]{16})"), "aws-key"),
    (re.compile(r"\b(AIza[0-9A-Za-z_\-]{35})"), "google-key"),
    (re.compile(r"\b(xox[abpors]-[A-Za-z0-9\-]{10,})"), "slack-token"),
    (re.compile(r"\b(eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{10,})"), "jwt"),
    (re.compile(r"(?i)(bearer\s+)([A-Za-z0-9._\-]{24,})"), "bearer"),
    (re.compile(r"(?i)\b([A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|PWD)[A-Z0-9_]*\s*[=:]\s*)([\"']?)([^\s\"']{8,})"), "assignment"),
]


def redact(text):
    hits = 0
    for rx, kind in SECRET_RES:
        def sub(m, kind=kind):
            nonlocal hits
            hits += 1
            if kind == "bearer":
                return m.group(1) + "[REDACTED:bearer]"
            if kind == "assignment":
                return m.group(1) + m.group(2) + "[REDACTED:secret]"
            return f"[REDACTED:{kind}]"
        text = rx.sub(sub, text)
    return text, hits


def norm(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", "")
    return text.strip("\n\ufeff ")


def h(text, n=12):
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()[:n]


def read(p):
    b = Path(p).read_bytes()
    if b[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return b.decode("utf-16", "replace")
    return b.decode("utf-8", "replace")


# ---------------------------------------------------------------- gather
NPP_STAMP = re.compile(r"@(\d{4}-\d{2}-\d{2})_(\d{2})(\d{2})(\d{2})")
GUID = re.compile(r"^([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})")


def tab_date(run_dir, guid):
    for p in run_dir.glob(f"source-snapshots/windows-notepad/LocalState/TabState/{guid}.bin"):
        return dt.datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d")
    for p in run_dir.glob(f"final-state/windows-notepad/TabState/{guid}.bin"):
        return dt.datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d")
    return run_dir.name[:4] + "-" + run_dir.name[4:6] + "-" + run_dir.name[6:8]


def gather(recovery):
    items = []
    for run in sorted(p for p in recovery.iterdir() if p.is_dir() and re.match(r"\d{8}-\d{6}Z$", p.name)):
        # Windows Notepad: full TabState parse (current text, .bak versions, deleted history)
        for sub in ("extracted-full", "final-state/extracted-notepad"):
            d = run / sub
            if not d.is_dir():
                continue
            for f in sorted(d.iterdir()):
                m = GUID.match(f.name)
                if not m or not f.name.endswith(".txt"):
                    continue
                variant = "deleted-history" if "deleted-history" in f.name else ("autosave" if ".bak." in f.name else "current")
                items.append(dict(app="notepad", run=run.name, path=str(f), tab=m.group(1), variant=variant,
                                  date=tab_date(run, m.group(1)), tab_name=None))
        # Notepad++: unsaved buffers from session backups
        for sub in ("extracted-exact", "extracted-npp/unsaved"):
            d = run / sub
            if not d.is_dir():
                continue
            for f in sorted(d.iterdir()):
                if GUID.match(f.name) or not f.is_file():
                    continue  # GUID files in extracted-exact are the old Notepad longest-run parse
                name = re.sub(r"\.(recovered|txt)$", "", f.name)
                m = NPP_STAMP.search(name)
                date = m.group(1) if m else run.name[:4] + "-" + run.name[4:6] + "-" + run.name[6:8]
                items.append(dict(app="notepad++", run=run.name, path=str(f), tab=NPP_STAMP.sub("", name),
                                  variant="current", date=date, tab_name=NPP_STAMP.sub("", name)))
        # Saved Notepad++ tabs in scratch locations (aggregate sources saved to disk)
        inv = run / "reports/all-tabs.json"
        if inv.is_file():
            for t in json.loads(inv.read_text()):
                p = t.get("path") or ""
                if t.get("source") == "file-on-disk" and p.startswith(SCRATCH_ROOTS) and Path(p).is_file():
                    if Path(p).suffix.lower() not in (".md", ".txt", ".markdown", ""):
                        continue
                    date = dt.datetime.fromtimestamp(Path(p).stat().st_mtime).strftime("%Y-%m-%d")
                    items.append(dict(app="notepad++ (saved file)", run=run.name, path=p, tab=p, variant="current",
                                      date=date, tab_name=Path(p).name))
    docs = {}
    for it in items:
        try:
            text = norm(read(it["path"]))
        except OSError:
            continue
        if len(text) < 20:
            continue
        if it["app"].endswith("(saved file)") and len(text) > MAX_SAVED:
            print(f"skipped saved file over {MAX_SAVED:,} chars (separate corpus): {it['path']}", file=sys.stderr)
            continue
        text, _ = redact(text)
        key = h(text)
        d = docs.setdefault(key, dict(id=key, text=text, chars=len(text), occurrences=[]))
        d["occurrences"].append({k: it[k] for k in ("app", "run", "path", "tab", "tab_name", "variant", "date")})
    for d in docs.values():
        occ = d["occurrences"]
        d["app"] = sorted({o["app"] for o in occ})[0]
        d["date"] = min(o["date"] for o in occ)
        d["tab_name"] = next((o["tab_name"] for o in occ if o["tab_name"]), None)
        d["variant"] = "current" if any(o["variant"] == "current" for o in occ) else occ[0]["variant"]
    return items, docs


# ---------------------------------------------------------------- dedup (versions)
def shingles(text, k=8):
    w = re.findall(r"\w+", text.lower())
    if len(w) < k:
        return {" ".join(w)} if w else set()
    return {hash(" ".join(w[i:i + k])) for i in range(len(w) - k + 1)}


def drop_contained(docs, thresh=0.97):
    """A tab saved across runs grows by appends. Keep the newest superset; record the rest as versions."""
    order = sorted(docs.values(), key=lambda d: -d["chars"])
    sh = {d["id"]: shingles(d["text"]) for d in order}
    kept = []
    for d in order:
        s = sh[d["id"]]
        home = None
        if s:
            for k in kept:
                ks = sh[k["id"]]
                if len(s) <= len(ks) and len(s & ks) / len(s) >= thresh:
                    home = k
                    break
        if home:
            home.setdefault("versions", []).append({"id": d["id"], "chars": d["chars"], "date": d["date"]})
            home["occurrences"].extend(d["occurrences"])
            home["date"] = min(home["date"], d["date"])
        else:
            kept.append(d)
    return {d["id"]: d for d in kept}


# ---------------------------------------------------------------- slice
SEP = re.compile(r"^\s*(?:[-=*_~#]{3,}|[─━═]{3,}|[╭╰][─━].*)\s*$")
HEAD = re.compile(r"^#{1,2}\s+\S")


def blocks_of(text, min_chars=250):
    lines = text.split("\n")
    out, cur, blank = [], [], 0
    for ln in lines:
        boundary = False
        if not ln.strip():
            blank += 1
            cur.append(ln)
            continue
        if blank >= 2 or SEP.match(ln) or HEAD.match(ln):
            boundary = True
        blank = 0
        if boundary and "".join(cur).strip():
            out.append("\n".join(cur).strip("\n"))
            cur = []
        cur.append(ln)
    if "".join(cur).strip():
        out.append("\n".join(cur).strip("\n"))
    split = []
    for b in out:  # break walls of text at single blank lines, about 4,000 chars per block
        if len(b) <= 15000:
            split.append(b)
            continue
        cur = ""
        paras = []
        for para in re.split(r"\n\s*\n", b):
            paras.extend(para.split("\n") if len(para) > 4000 else [para])
        for para in paras:
            if cur and len(cur) + len(para) > 4000:
                split.append(cur)
                cur = ""
            cur = cur + "\n\n" + para if cur else para
        if cur:
            split.append(cur)
    out = split
    merged = []
    for b in out:
        if merged and len(merged[-1]) < min_chars:
            merged[-1] = merged[-1] + "\n\n" + b
        else:
            merged.append(b)
    if len(merged) > 1 and len(merged[-1]) < min_chars:
        last = merged.pop()
        merged[-1] = merged[-1] + "\n\n" + last
    return merged


def projects_list():
    ids = sorted(p.name for p in LD_PROJECTS.iterdir() if p.is_dir() and not p.name.startswith("."))
    return ids + ["sysadmin", "personal", "career", "finance", "unclassified"]


SYSTEM = """You organize an operator's scratchpad notes. The operator pastes prompts, agent replies, plans, configs and research into Notepad tabs while running many AI coding agents. One tab often holds several unrelated notes pasted one after another.

You get one tab as numbered blocks (head and tail of each block). Group consecutive blocks into separate notes: start a new note where the topic, purpose or source changes. A long agent reply split by headings stays one note. A pasted prompt followed by the reply to it can stay one note.

For each note return:
- start, end: first and last block numbers (inclusive, consecutive, covering every block exactly once)
- title: specific, 4 to 10 words, says what the note is (not "Notes" or "Untitled")
- kind: one of prompt, agent-reply, plan, task-list, spec, config, research, transcript, log, personal, reference, junk
- summary: one or two plain sentences
- projects: 1 to 3 ids from the PROJECT LIST that the note is about; use sysadmin, personal, career, finance or unclassified when no project fits
- themes: 2 to 5 short lowercase tags
- has_tasks: true when the note lists work still to be done
- status: actionable, reference, done or junk

Return JSON only: {"notes":[...]}"""


def outline(blocks, start, head=420, tail=160):
    parts = []
    for i in range(start, min(start + 60, len(blocks))):
        b = blocks[i]
        body = b if len(b) <= head + tail + 40 else b[:head] + f"\n[... {len(b) - head - tail} chars ...]\n" + b[-tail:]
        parts.append(f"<block n={i} chars={len(b)}>\n{body}\n</block>")
    return "\n".join(parts)


def call_model(model, system, user, key, retries=4):
    body = {"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "max_tokens": 8000, "response_format": {"type": "json_object"}}
    last = None
    for attempt in range(retries):
        req = urllib.request.Request(ENDPOINT, data=json.dumps(body).encode(), headers={
            "Authorization": "Bearer " + key, "Content-Type": "application/json",
            "User-Agent": UA, "x-opencode-session": SESSION})
        try:
            r = json.load(urllib.request.urlopen(req, timeout=240))
            txt = r["choices"][0]["message"]["content"] or ""
            txt = re.sub(r"^```(?:json)?\s*|\s*```$", "", txt.strip())
            return json.loads(txt), r.get("usage", {})
        except Exception as e:  # noqa: BLE001 - retried, then surfaced
            last = e
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"model call failed: {last}")


def plan_doc(doc, model, key, cache_dir, plist):
    cp = cache_dir / f"{doc['id']}.json"
    if cp.is_file():
        return json.loads(cp.read_text())
    blocks = blocks_of(doc["text"])
    notes, start, usage = [], 0, []
    while start < len(blocks):
        prev = f"The previous window ended inside the note titled: {notes[-1]['title']!r}. If block {start} continues it, start your first note at {start} with that same title.\n" if notes else ""
        user = (f"PROJECT LIST: {', '.join(plist)}\n\nTab name: {doc.get('tab_name') or '(unsaved tab)'}; app: {doc['app']}; "
                f"date: {doc['date']}; {len(blocks)} blocks in total, this window shows blocks {start} to {min(start + 60, len(blocks)) - 1}.\n{prev}\n"
                + outline(blocks, start))
        res, u = call_model(model, SYSTEM, user, key)
        usage.append(u)
        win_end = min(start + 60, len(blocks)) - 1
        got = sorted((n for n in res.get("notes", []) if isinstance(n.get("start"), int)), key=lambda n: n["start"])
        cursor = start
        for n in got:
            s, e = max(n["start"], cursor), min(int(n.get("end", n["start"])), win_end)
            if e < s:
                continue
            if s > cursor:  # fill a gap the model skipped
                notes.append(dict(n, start=cursor, end=s - 1, title=n.get("title", "Untitled") + " (preceding part)"))
            n = dict(n, start=s, end=e)
            if notes and notes[-1]["title"] == n.get("title") and notes[-1]["end"] == s - 1:
                notes[-1]["end"] = e
            else:
                notes.append(n)
            cursor = e + 1
        if cursor <= win_end:
            if notes:
                notes[-1]["end"] = win_end
            else:
                notes.append(dict(start=start, end=win_end, title=doc.get("tab_name") or "Untitled note", kind="reference",
                                  summary="", projects=["unclassified"], themes=[], has_tasks=False, status="reference"))
        start = win_end + 1
    out = {"blocks": blocks, "notes": notes, "usage": usage, "model": model}
    cp.write_text(json.dumps(out))
    return out


# ---------------------------------------------------------------- cluster + write
def slug(s, n=60):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:n].rstrip("-") or "note"


def cluster(slices, thresh=0.8):
    sh = [shingles(s["text"], 6) for s in slices]
    parent = list(range(len(slices)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    index = {}
    for i, s in enumerate(sh):
        for g in sorted(s)[:400]:  # bottom-k sketch: the same shingles are sampled from every note
            index.setdefault(g, []).append(i)
    cand = set()
    for ids in index.values():
        if 1 < len(ids) < 50:
            for a in ids:
                for b in ids:
                    if a < b:
                        cand.add((a, b))
    for a, b in cand:
        A, B = sh[a], sh[b]
        if not A or not B:
            continue
        inter = len(A & B)
        if inter / len(A | B) >= thresh or inter / min(len(A), len(B)) >= 0.8:
            parent[find(a)] = find(b)
    groups = {}
    for i in range(len(slices)):
        groups.setdefault(find(i), []).append(i)
    return list(groups.values())


def win_path(p):
    p = str(p)
    if p.startswith("/mnt/c/"):
        return "C:\\" + p[7:].replace("/", "\\")
    return "\\\\wsl.localhost\\Ubuntu" + p.replace("/", "\\")


def yaml_list(xs):
    return "[" + ", ".join(json.dumps(x) for x in xs) + "]"


def write_library(out, docs, plans):
    slices = []
    for d in docs.values():
        p = plans.get(d["id"])
        if not p:
            continue
        for i, n in enumerate(p["notes"]):
            text = "\n\n".join(p["blocks"][n["start"]:n["end"] + 1]).strip()
            if not text:
                continue
            slices.append(dict(doc=d["id"], part=i + 1, parts=len(p["notes"]), text=text, chars=len(text),
                               title=(n.get("title") or "Untitled note").strip(), kind=n.get("kind", "reference"),
                               summary=n.get("summary", ""), projects=n.get("projects") or ["unclassified"],
                               themes=n.get("themes") or [], has_tasks=bool(n.get("has_tasks")),
                               status=n.get("status", "reference"), date=d["date"], app=d["app"],
                               tab_name=d.get("tab_name"), variant=d.get("variant", "current")))
    groups = cluster(slices)
    notes = []
    for g in groups:
        g = sorted(g, key=lambda i: (-slices[i]["chars"], slices[i]["date"]))
        canon = dict(slices[g[0]])
        canon["id"] = h(canon["text"], 10)
        canon["copies"] = [{"doc": slices[i]["doc"], "part": slices[i]["part"], "date": slices[i]["date"],
                            "chars": slices[i]["chars"]} for i in g]
        canon["first_seen"] = min(slices[i]["date"] for i in g)
        notes.append(canon)
    plist = set(projects_list())
    notes_dir = out / "notes"
    # related notes: shared projects, themes and title words
    feats = []
    for n in notes:
        words = {w for w in re.findall(r"[a-z0-9]{4,}", n["title"].lower())}
        feats.append({"p:" + p for p in n["projects"] if p != "unclassified"} | {"t:" + t for t in n["themes"]} | {"w:" + w for w in words})
    for i, n in enumerate(notes):
        scored = []
        for j, f in enumerate(feats):
            if i != j and feats[i] and f:
                sc = len(feats[i] & f) / len(feats[i] | f)
                if sc >= 0.25:
                    scored.append((sc, notes[j]["id"]))
        n["related"] = [x for _, x in sorted(scored, reverse=True)[:6]]
    for n in notes:
        n["projects"] = [p for p in n["projects"] if p in plist] or ["unclassified"]
        n["file"] = f"notes/{n['projects'][0]}/{n['first_seen']}-{slug(n['title'])}-{n['id']}.md"
    by_doc = {}
    for n in notes:
        for c in n["copies"]:
            by_doc.setdefault(c["doc"], []).append((c["part"], n))
    # write note files
    if notes_dir.exists():
        for f in notes_dir.rglob("*.md"):
            f.unlink()
    for n in notes:
        p = out / n["file"]
        p.parent.mkdir(parents=True, exist_ok=True)
        srcs = sorted({c["doc"] for c in n["copies"]})
        fm = ["---", f"id: {n['id']}", f"title: {json.dumps(n['title'])}", f"kind: {n['kind']}", f"status: {n['status']}",
              f"date: {n['first_seen']}", f"projects: {yaml_list(n['projects'])}", f"themes: {yaml_list(n['themes'])}",
              f"has_tasks: {str(n['has_tasks']).lower()}", f"summary: {json.dumps(n['summary'])}",
              f"source_app: {json.dumps(n['app'])}", f"source_tab: {json.dumps(n['tab_name'] or '(unsaved tab)')}",
              f"sources: {yaml_list(['sources/' + s + '.md' for s in srcs])}",
              f"copies: {len(n['copies'])}", f"related: {yaml_list(n['related'])}", f"chars: {n['chars']}", "---", "", f"# {n['title']}", "",
              f"> {n['summary']}" if n["summary"] else "", "", n["text"], ""]
        p.write_text("\n".join(fm))
    # write source pages (one per original tab), listing its slices in order
    src_dir = out / "sources"
    src_dir.mkdir(parents=True, exist_ok=True)
    for f in src_dir.glob("*.md"):
        f.unlink()
    sources = []
    for d in docs.values():
        parts = sorted(by_doc.get(d["id"], []), key=lambda x: x[0])
        occ = d["occurrences"]
        paths = sorted({o["path"] for o in occ})
        title = d.get("tab_name") or (parts[0][1]["title"] if parts else "Untitled tab")
        lines = ["---", f"id: {d['id']}", f"title: {json.dumps(title)}", f"source_app: {json.dumps(d['app'])}",
                 f"date: {d['date']}", f"chars: {d['chars']}", f"sections: {len(parts)}",
                 f"versions_merged: {len(d.get('versions', []))}", "---", "", f"# {title}", "",
                 f"{d['app']}, first seen {d['date']}, {d['chars']:,} characters, sliced into {len(parts)} notes.", "",
                 "## Sections", ""]
        for part, n in parts:
            lines.append(f"{part}. [{n['title']}](../{n['file']}) ({n['kind']}; {', '.join(n['projects'])})")
        lines += ["", "## Recovered copies", ""] + [f"- `{p}`" for p in paths] + [""]
        (src_dir / f"{d['id']}.md").write_text("\n".join(lines))
        sources.append(dict(id=d["id"], title=title, app=d["app"], date=d["date"], chars=d["chars"],
                            sections=[n["id"] for _, n in parts], paths=paths, versions=len(d.get("versions", []))))
    catalog = dict(generated=dt.datetime.now().isoformat(timespec="seconds"), notes=[
        {k: n[k] for k in ("id", "title", "kind", "status", "summary", "projects", "themes", "has_tasks", "first_seen",
                           "app", "tab_name", "chars", "file", "copies", "related", "text")} for n in notes], sources=sources)
    (out / "catalog.json").write_text(json.dumps(catalog, indent=1))
    write_index(out, catalog)
    return catalog


INDEX_HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Notes Library</title>
<style>
:root{--bg:#f7f6f3;--panel:#fff;--ink:#1d1d1f;--muted:#6b6b70;--line:#e3e1dc;--accent:#2f5d8a;--chip:#eef2f6;--warn:#9a5b00;--mono:ui-monospace,SFMono-Regular,Consolas,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#151517;--panel:#1e1e21;--ink:#ececf0;--muted:#9a9aa3;--line:#2e2e33;--accent:#8fb8e0;--chip:#26303a;--warn:#e0a85a}}
:root[data-theme="dark"]{--bg:#151517;--panel:#1e1e21;--ink:#ececf0;--muted:#9a9aa3;--line:#2e2e33;--accent:#8fb8e0;--chip:#26303a;--warn:#e0a85a}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
header{position:sticky;top:0;z-index:2;background:var(--bg);border-bottom:1px solid var(--line);padding:12px 16px}
h1{font-size:18px;margin:0 0 8px}.stats{color:var(--muted);font-size:13px}
.controls{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
input,select,button{font:inherit;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:6px 8px}
input[type=search]{flex:1 1 260px}main{max-width:1100px;margin:0 auto;padding:12px 16px 60px}
.group h2{font-size:15px;margin:22px 0 6px;color:var(--accent)}
.note{background:var(--panel);border:1px solid var(--line);border-radius:8px;margin:6px 0;padding:8px 12px}
.note summary{cursor:pointer;list-style:none}.note summary::-webkit-details-marker{display:none}
.t{font-weight:600}.meta{color:var(--muted);font-size:12.5px}.chip{display:inline-block;background:var(--chip);border-radius:10px;padding:0 7px;margin:2px 3px 0 0;font-size:12px}
.task{color:var(--warn);font-weight:600}.sum{margin:4px 0 0}
pre{white-space:pre-wrap;word-break:break-word;font:12.5px/1.45 var(--mono);background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:10px;max-height:520px;overflow:auto}
.row{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:6px 0}.path{font:12px var(--mono);color:var(--muted);word-break:break-all}
.tabs button.on{background:var(--accent);color:var(--bg);border-color:var(--accent)}
</style></head><body>
<header><h1>Notes Library</h1><div class="stats" id="stats"></div>
<div class="controls tabs"><button id="vNotes" class="on">Notes by project</button><button id="vSources">Original tabs</button><button id="theme">Theme</button></div>
<div class="controls"><input type="search" id="q" placeholder="Search titles, summaries and text">
<select id="proj"><option value="">All projects</option></select><select id="kind"><option value="">All kinds</option></select>
<select id="status"><option value="">Any status</option><option>actionable</option><option>reference</option><option>done</option><option>junk</option></select>
<label class="meta"><input type="checkbox" id="tasks"> has tasks</label></div></header>
<main id="main"></main>
<script id="data" type="application/json">__DATA__</script>
<script>
const D=JSON.parse(document.getElementById('data').textContent);const $=s=>document.querySelector(s);
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const WIN=p=>'\\\\wsl.localhost\\Ubuntu\\home\\cheta\\agent-notes\\library\\'+p.replace(/\//g,'\\');
let view='notes';const byId=Object.fromEntries(D.notes.map(n=>[n.id,n]));
const projects=[...new Set(D.notes.flatMap(n=>n.projects))].sort();const kinds=[...new Set(D.notes.map(n=>n.kind))].sort();
projects.forEach(p=>$('#proj').insertAdjacentHTML('beforeend',`<option>${esc(p)}</option>`));kinds.forEach(k=>$('#kind').insertAdjacentHTML('beforeend',`<option>${esc(k)}</option>`));
$('#stats').textContent=`${D.notes.length} notes from ${D.sources.length} original tabs · ${projects.length} projects · ${D.notes.filter(n=>n.copies.length>1).length} notes found in more than one tab · generated ${D.generated}`;
function noteHTML(n){return `<details class="note"><summary><div class="t">${esc(n.title)}</div>
<div class="meta">${esc(n.first_seen)} · ${esc(n.kind)} · ${esc(n.status)} · ${n.chars.toLocaleString()} chars${n.copies.length>1?` · <b>${n.copies.length} copies merged</b>`:''}${n.has_tasks?' · <span class="task">has tasks</span>':''}</div>
<div>${n.projects.map(p=>`<span class="chip">${esc(p)}</span>`).join('')}${n.themes.map(t=>`<span class="chip">#${esc(t)}</span>`).join('')}</div>
${n.summary?`<p class="sum">${esc(n.summary)}</p>`:''}</summary>
<div class="row"><button data-copy="${n.id}">Copy text</button><button data-path="${esc(WIN(n.file))}">Copy file path</button><span class="path">${esc(n.file)}</span></div>
${n.related&&n.related.length?`<div class="meta">Related: ${n.related.map(i=>byId[i]).filter(Boolean).map(r=>`<a href="#" data-goto="${r.id}">${esc(r.title)}</a>`).join(' · ')}</div>`:''}
${n.copies.length>1?`<div class="meta">Also found in: ${n.copies.slice(1).map(c=>esc((D.sources.find(s=>s.id===c.doc)||{}).title||c.doc)).join(' · ')}</div>`:''}
<pre>${esc(n.text)}</pre></details>`}
function match(n,skipQ){const q=skipQ?'':$('#q').value.toLowerCase(),p=$('#proj').value,k=$('#kind').value,s=$('#status').value;
return(!p||n.projects.includes(p))&&(!k||n.kind===k)&&(!s||n.status===s)&&(!$('#tasks').checked||n.has_tasks)&&(!q||(n.title+' '+n.summary+' '+n.themes.join(' ')+' '+n.text).toLowerCase().includes(q))}
function render(){const m=$('#main');if(view==='notes'){const g={};D.notes.filter(match).forEach(n=>(g[n.projects[0]]??=[]).push(n));
m.innerHTML=Object.keys(g).sort().map(p=>`<section class="group"><h2>${esc(p)} (${g[p].length})</h2>${g[p].sort((a,b)=>b.first_seen.localeCompare(a.first_seen)).map(noteHTML).join('')}</section>`).join('')||'<p>No notes match.</p>'}
else{m.innerHTML=D.sources.sort((a,b)=>b.chars-a.chars).map(s=>{const hit=$('#q').value&&s.title.toLowerCase().includes($('#q').value.toLowerCase());const ns=s.sections.map(i=>byId[i]).filter(Boolean).filter(n=>match(n,hit));if(!ns.length)return'';
return `<section class="group"><h2>${esc(s.title)}</h2><div class="meta">${esc(s.app)} · first seen ${esc(s.date)} · ${s.chars.toLocaleString()} chars · ${s.sections.length} sections${s.versions?` · ${s.versions} older versions merged`:''}</div>${ns.map(noteHTML).join('')}</section>`}).join('')}}
document.addEventListener('click',e=>{const g=e.target.dataset.goto;if(g){e.preventDefault();$('#q').value=byId[g].title;$('#proj').value='';$('#kind').value='';$('#status').value='';$('#tasks').checked=false;render();const d=document.querySelector('details.note');if(d)d.open=true;return}const c=e.target.dataset.copy,p=e.target.dataset.path;if(c){navigator.clipboard.writeText(byId[c].text);e.target.textContent='Copied'}if(p){navigator.clipboard.writeText(p);e.target.textContent='Copied'}});
['#q','#proj','#kind','#status','#tasks'].forEach(s=>$(s).addEventListener('input',render));
$('#vNotes').onclick=()=>{view='notes';$('#vNotes').classList.add('on');$('#vSources').classList.remove('on');render()};
$('#vSources').onclick=()=>{view='sources';$('#vSources').classList.add('on');$('#vNotes').classList.remove('on');render()};
$('#theme').onclick=()=>{const r=document.documentElement;r.dataset.theme=r.dataset.theme==='dark'?'light':'dark'};render();
</script></body></html>"""


def write_index(out, catalog):
    data = json.dumps(catalog).replace("</", "<\\/")
    (out / "index.html").write_text(INDEX_HTML.replace("__DATA__", data))


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--recovery", default=str(RECOVERY))
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--model", default="gemini-4-argon")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--stage", default="all", choices=["all", "gather", "plan"])
    ap.add_argument("--limit", type=int, default=0, help="plan only the first N documents (trial runs)")
    a = ap.parse_args()
    out = Path(a.out)
    (out / ".cache/plans").mkdir(parents=True, exist_ok=True)
    items, docs = gather(Path(a.recovery))
    n_exact = len(docs)
    docs = drop_contained(docs)
    print(f"gathered {len(items)} extracted files -> {n_exact} distinct texts -> {len(docs)} after merging older versions; "
          f"{sum(d['chars'] for d in docs.values()):,} chars")
    if a.stage == "gather":
        for d in sorted(docs.values(), key=lambda d: -d["chars"])[:15]:
            print(f"  {d['chars']:>8,}  {len(blocks_of(d['text'])):>4} blocks  {d['app']:<10} {d['date']}  {(d.get('tab_name') or d['text'][:60]).splitlines()[0][:70]}")
        return 0
    key = os.environ.get("OPENCODE_GO_API_KEY")
    if not key:
        print("OPENCODE_GO_API_KEY is not set", file=sys.stderr)
        return 2
    plist = projects_list()
    todo = sorted(docs.values(), key=lambda d: d["chars"])
    if a.limit:
        todo = todo[:a.limit]
    plans, failed = {}, []
    with cf.ThreadPoolExecutor(a.workers) as ex:
        futs = {ex.submit(plan_doc, d, a.model, key, out / ".cache/plans", plist): d for d in todo}
        for i, f in enumerate(cf.as_completed(futs), 1):
            d = futs[f]
            try:
                plans[d["id"]] = f.result()
                print(f"[{i}/{len(todo)}] {d['id']} {len(plans[d['id']]['notes'])} notes", flush=True)
            except Exception as e:  # noqa: BLE001
                failed.append(d["id"])
                print(f"[{i}/{len(todo)}] {d['id']} FAILED {e}", flush=True)
    if a.stage == "plan":
        return 1 if failed else 0
    cat = write_library(out, {k: v for k, v in docs.items() if k in plans}, plans)
    print(f"wrote {len(cat['notes'])} notes from {len(cat['sources'])} tabs to {out}; failed tabs: {len(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
