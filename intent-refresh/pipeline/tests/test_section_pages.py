"""12-render writes the Intent Archaeology section the page schema requires (MP-02).

LIVING_DOCUMENTS/system/PAGE-SCHEMA.json requires prompt-corpus,
intent-archaeology-findings and intent-archaeology-source-adjudication in
every dossier. 12-render writes them from the same records as its other
pages, and never touches a page of those names that it did not generate.

Run: python3 -I -m unittest discover -s <pipeline>/tests -v
Every test uses a throwaway INTENT_ARCH_HOME and LD_DATA_ROOT, never live data.
"""
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PIPE = Path(__file__).resolve().parent.parent
RUN = "2026-01-01"
SECTION = ("prompt-corpus", "intent-archaeology-findings", "intent-archaeology-source-adjudication")
HAND_CORPUS = ("---\nid: prompt-corpus\ntitle: Prompt corpus\ntype: evidence\norder: 95\n"
               "status: active\nparent: index\nrelated: []\nupdated: 2026-08-01\n---\n\n"
               "# Prompt corpus\n\nHand-made corpus. Must stay byte-identical.\n")


def frontmatter(text):
    out = {}
    for ln in text.split("\n---", 1)[0].splitlines()[1:]:
        k, _, v = ln.partition(":")
        out[k.strip()] = v.strip()
    return out


class SectionPages(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.home, self.ld = root / "ia", root / "ld"
        self.env = dict(os.environ, INTENT_ARCH_HOME=str(self.home), LD_DATA_ROOT=str(self.ld))
        r = subprocess.run([sys.executable, "-I", str(PIPE / "00-init.py")], env=self.env,
                           capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)

        # Two dossiers: "hand" already holds a hand-made prompt-corpus page,
        # "fresh" holds no section page at all.
        for d in ("hand", "fresh"):
            (self.ld / "projects" / d).mkdir(parents=True)
            (self.ld / "projects" / d / "project.md").write_text(f"---\nid: {d}\n---\n# {d}\n")
        (self.ld / "projects" / "hand" / "prompt-corpus.md").write_text(HAND_CORPUS)

        run = self.home / "corpus" / RUN
        (run / "refined").mkdir(parents=True)
        sessions, prompts = [], []
        for n, d in enumerate(("hand", "fresh")):
            sid = f"claude_code:s{n}"
            sessions.append({"id": sid, "harness": "claude_code", "session_id": f"s{n}" * 4,
                             "source_path": f"/x/s{n}.jsonl", "cwd": f"/code/{d}", "origin": "interactive",
                             "project": d, "rung": "cwd-in-dossier-root",
                             "first_ts": f"2026-01-0{n + 1}T10:00:00Z"})
            for k in range(3):
                prompts.append({"id": f"op_{d}_{k}", "session": sid, "origin": "interactive",
                                "ts": f"2026-01-0{n + 1}T10:0{k}:00Z", "repeats": 0,
                                "text": f"{d} prompt {k}: build it | with a pipe <!-- x -->"})
        (run / "sessions.jsonl").write_text("".join(json.dumps(s) + "\n" for s in sessions))
        (run / "prompts.jsonl").write_text("".join(json.dumps(p) + "\n" for p in prompts))

        db = sqlite3.connect(self.home / "archaeology.db")
        db.execute("INSERT INTO project (id,path,root,kind,pipeline_version,created_at)"
                   " VALUES ('p','/x/p','/x','project','t','t')")
        db.execute("INSERT INTO session (id,harness,source_path,project_id,pipeline_version,enriched)"
                   " VALUES ('s','claude_code','/x/s.jsonl','p','t',0)")
        for p in prompts:
            db.execute("INSERT INTO event (id,session_id,project_id,seq,ts,role,is_human,text,"
                       "pipeline_version) VALUES (?,?,?,?,?,?,?,?,?)",
                       ("evt_" + p["id"], "s", "p", 1, p["ts"], "user", 1, p["text"], "t"))
        rows = [("int_a1", "directive.feature", "Build it | with a pipe", None, 3, "op_hand_0"),
                ("int_a2", "bugreport", "It broke", "superseded", 1, "op_hand_1"),
                ("int_b1", "directive.constraint", "Never push", "active", 1, "op_fresh_0")]
        for iid, typ, stmt, status, occ, ev in rows:
            db.execute("INSERT INTO intent (id,project_id,type,statement,verbatim,status,first_ts,"
                       "occurrences,pipeline_version,created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                       (iid, "p", typ, stmt, stmt, status, "2026-01-01T10:00:00Z", occ, "t", "t"))
            db.execute("INSERT INTO intent_event (intent_id,event_id) VALUES (?,?)", (iid, "evt_" + ev))
        db.commit()
        db.close()

    def tearDown(self):
        self.tmp.cleanup()

    def render(self):
        r = subprocess.run([sys.executable, "-I", str(PIPE / "12-render.py"), "--run", RUN],
                           env=self.env, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def page(self, d, kind):
        return (self.ld / "projects" / d / f"{kind}.md").read_text()

    def test_fresh_dossier_gets_whole_section_with_schema_frontmatter(self):
        self.render()
        for kind in SECTION:
            fm = frontmatter(self.page("fresh", kind))
            for field in ("id", "title", "type", "order", "status", "parent", "related", "updated"):
                self.assertTrue(fm.get(field), f"{kind}: {field}")
            self.assertEqual(fm["id"], kind)
            self.assertEqual(fm["populator"], "intent-refresh 12-render")
            self.assertIn("## Why read this now (30s)", self.page("fresh", kind))
            self.assertIn("## User section", self.page("fresh", kind))
        self.assertEqual(frontmatter(self.page("fresh", "intent-archaeology-findings"))["type"], "evidence")
        self.assertEqual(frontmatter(self.page("fresh", "intent-archaeology-source-adjudication"))["type"],
                         "ledger")

    def test_content_comes_from_the_records(self):
        self.render()
        adj = self.page("hand", "intent-archaeology-source-adjudication")
        self.assertIn("`int_a1`", adj)
        self.assertIn("`int_a2`", adj)
        self.assertNotIn("`int_b1`", adj)  # belongs to the other dossier
        self.assertIn("Build it \\| with a pipe", adj)  # pipes cannot break the table
        self.assertIn("**Superseded.**", adj)
        self.assertIn("**Not yet adjudicated.**", adj)
        fnd = self.page("hand", "intent-archaeology-findings")
        self.assertIn("| operator prompts | 3 |", fnd)
        self.assertIn("| derived intents | 2 |", fnd)
        self.assertIn("| prompts with no derived intent | 1 |", fnd)
        self.assertIn("3 times", fnd)
        corpus = self.page("fresh", "prompt-corpus")
        self.assertIn("intent-verbatim.md#prompt-op-fresh-2", corpus)
        for kind in SECTION:
            body = self.page("fresh", kind).split("\n---", 1)[1]
            self.assertNotIn("<!-- x", body)  # recorded text stays inert

    def test_hand_made_page_is_never_touched(self):
        out = self.render()
        self.assertEqual(self.page("hand", "prompt-corpus"), HAND_CORPUS)
        self.assertIn("kept as found", out)
        self.assertTrue((self.ld / "projects" / "hand" / "intent-archaeology-findings.md").exists())

    def test_rerun_refreshes_only_its_own_blocks(self):
        self.render()
        f = self.ld / "projects" / "fresh" / "intent-archaeology-findings.md"
        f.write_text(f.read_text().replace(
            "Operator notes. Regeneration never touches this section.", "My own ruling."))
        first = f.read_text()
        self.render()
        second = f.read_text()
        self.assertEqual(first, second)
        self.assertIn("My own ruling.", second)
        self.assertEqual(second.count("intent-refresh:start run=2026-01-01 section=findings"), 1)


if __name__ == "__main__":
    unittest.main()
