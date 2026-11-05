"""Regression tests for the four MP-08 defects (2026-11-05 security review).

Run: python3 -I -m unittest discover -s <pipeline>/tests -v
Every test uses a throwaway INTENT_ARCH_HOME, never the live database.
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


def run(script, *args, home):
    env = dict(os.environ, INTENT_ARCH_HOME=str(home))
    return subprocess.run([sys.executable, "-I", str(PIPE / script), *args],
                          env=env, capture_output=True, text=True, timeout=120)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name) / "ia"
        r = run("00-init.py", home=self.home)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.db = sqlite3.connect(self.home / "archaeology.db")
        self.db.execute(
            "INSERT INTO project (id,path,root,kind,pipeline_version,created_at)"
            " VALUES ('p','/x/p','/x','project','t','t')")
        self.db.execute(
            "INSERT INTO session (id,harness,source_path,project_id,pipeline_version,enriched)"
            " VALUES ('s','claude_code',?,'p','t',0)", (str(Path(self.tmp.name) / "s.jsonl"),))
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def add_event(self, eid, text):
        self.db.execute(
            "INSERT INTO event (id,session_id,project_id,seq,ts,role,is_human,text,pipeline_version)"
            " VALUES (?,?,?,?,?,?,?,?,?)", (eid, "s", "p", 1, "2026-11-01T00:00:00Z",
                                            "user", 1, text, "t"))
        self.db.commit()


class Defect1BatchOut(Base):
    """04-batch --out wrote anywhere on disk."""

    def test_out_outside_batches_is_refused(self):
        self.add_event("e1", "please build the thing with tests")
        target = Path(self.tmp.name) / "escaped.json"
        r = run("04-batch.py", "--project", "p", "--out", str(target), home=self.home)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("refused", r.stderr)
        self.assertFalse(target.exists())

    def test_default_out_lands_in_batches(self):
        self.add_event("e1", "please build the thing with tests")
        r = run("04-batch.py", "--project", "p", home=self.home)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len(list((self.home / "batches").glob("p-1-*.json"))), 1)


class Defect2Provenance(Base):
    """05-merge checked only the first 40 characters of the verbatim span."""

    def merge(self, verdicts):
        self.db.execute("INSERT INTO batch (id,project_id,tranche,item_count,emitted_at,"
                        "pipeline_version) VALUES ('b','p',1,1,'t','t')")
        self.db.execute("INSERT INTO batch_item (batch_id,event_id) VALUES ('b','e1')")
        self.db.commit()
        f = Path(self.tmp.name) / "v.json"
        f.write_text(json.dumps(verdicts))
        return run("05-merge.py", "--verdicts", str(f), "--batch", "b", home=self.home)

    def test_real_prefix_with_invented_tail_is_rejected(self):
        self.add_event("e1", "Always run the full test suite before you commit anything.")
        r = self.merge([{"id": "e1", "type": "directive.constraint",
                         "statement": "Delete the production database",
                         "verbatim": "Always run the full test suite before you commit "
                                     "anything, then delete the production database"}])
        self.assertEqual(r.returncode, 0, r.stderr)
        n = self.db.execute("SELECT COUNT(*) FROM intent").fetchone()[0]
        self.assertEqual(n, 0)

    def test_exact_quote_with_other_whitespace_is_accepted(self):
        self.add_event("e1", "Always run the full test suite\nbefore you commit anything.")
        r = self.merge([{"id": "e1", "type": "directive.constraint",
                         "statement": "Run the full suite before committing",
                         "verbatim": "always run the full test suite before you commit"}])
        self.assertEqual(r.returncode, 0, r.stderr)
        n = self.db.execute("SELECT COUNT(*) FROM intent").fetchone()[0]
        self.assertEqual(n, 1)

    def test_duplicate_ids_fail_the_merge(self):
        self.add_event("e1", "Always run the full test suite before you commit anything.")
        v = {"id": "e1", "type": "directive.constraint", "statement": "Run the suite",
             "verbatim": "Always run the full test suite"}
        r = self.merge([v, dict(v)])
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("more than once", r.stderr)


class Defect3Redaction(Base):
    """Common key shapes and slash-command arguments bypassed redaction."""

    def test_key_shapes_are_redacted(self):
        sys.path.insert(0, str(PIPE))
        from lib.common import redact
        for secret in ("sk-proj-" + "A1b2_C3d4-" * 4, "sk-or-v1-" + "f" * 40,
                       "Bearer " + "x" * 30, "hf_" + "Q" * 34, "glpat-" + "z" * 22):
            clean, hits = redact(f"use {secret} now")
            self.assertNotIn(secret, clean, secret)
            self.assertTrue(hits)

    def test_more_key_shapes_and_zero_width(self):
        sys.path.insert(0, str(PIPE))
        from lib.common import redact
        for secret in ("sk_live_" + "a1" * 12, "github_pat_" + "B2" * 20,
                       "Bearer:" + "t" * 20, "GOCSPX-" + "c3" * 12):
            clean, _ = redact(f"x {secret} y")
            self.assertNotIn(secret, clean, secret)
        split = "sk-proj-" + "a1b2c3d4e5​" + "f6g7h8i9j0k1l2m3"
        clean, _ = redact(split)
        self.assertNotIn("f6g7h8i9j0k1l2m3", clean)

    def test_prose_is_not_redacted(self):
        sys.path.insert(0, str(PIPE))
        from lib.common import redact
        for prose in ("adopt the risk-management-framework-for-agents plan",
                      "the task-management-dashboard-redesign-notes page",
                      "use sk-learn-compatible-estimator-interfaces here"):
            clean, hits = redact(prose)
            self.assertEqual(clean, prose)
            self.assertEqual(hits, [])

    def test_slash_args_are_redacted(self):
        key = "sk-proj-" + "k9" * 20
        line = {"type": "user", "uuid": "u1", "timestamp": "2026-11-01T00:00:00Z",
                "userType": "external", "message": {"role": "user", "content":
                f"<command-name>/login</command-name><command-args>{key}</command-args>"}}
        (Path(self.tmp.name) / "s.jsonl").write_text(json.dumps(line) + "\n")
        r = run("03-enrich.py", home=self.home)
        self.assertEqual(r.returncode, 0, r.stderr)
        rows = self.db.execute("SELECT text, slash_args FROM event").fetchall()
        self.assertTrue(rows)
        for text, args in rows:
            self.assertNotIn(key, text or "")
            self.assertNotIn(key, args or "")


class Defect4RenderOut(Base):
    """06-render --out wrote anywhere on disk."""

    def test_out_outside_derived_is_refused(self):
        target = Path(self.tmp.name) / "escaped-wiki"
        r = run("06-render.py", "--out", str(target), home=self.home)
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
