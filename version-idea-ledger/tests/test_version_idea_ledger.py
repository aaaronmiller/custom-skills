#!/usr/bin/env python3
"""Tests for version-idea-ledger. Builds a fixture family in a temporary folder."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(SKILL, "scripts")


def run(script, *args, ok=True):
    r = subprocess.run([sys.executable, "-I", "-B", os.path.join(S, script), *args], capture_output=True, text=True)
    if ok and r.returncode != 0:
        raise AssertionError(f"{script} failed: {r.stdout}\n{r.stderr}")
    return r


def jl(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def wjl(path, rows):
    with open(path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")


class Family(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.mkdtemp()
        t = self.t
        self.cur = os.path.join(t, "current")
        self.old = os.path.join(t, "old")
        os.makedirs(os.path.join(self.cur, "pkg"))
        os.makedirs(os.path.join(self.old, "docs"))
        os.makedirs(os.path.join(self.old, "node_modules"))
        with open(os.path.join(self.cur, "pkg", "rank.py"), "w") as fh:
            fh.write('"""Rank models by a weighted benchmark formula."""\n\ndef rank():\n    return []\n')
        with open(os.path.join(self.old, "docs", "spec.md"), "w") as fh:
            fh.write("# Spec\n\nThe ranker uses a weighted benchmark formula.\n\nA cache refresh runs weekly.\n")
        with open(os.path.join(self.old, "copy.py"), "w") as fh:
            with open(os.path.join(self.cur, "pkg", "rank.py")) as src:
                fh.write(src.read())
        with open(os.path.join(self.old, "node_modules", "x.js"), "w") as fh:
            fh.write("junk")
        self.L = os.path.join(t, "dossier", "ledgers")
        os.makedirs(self.L)
        self.files = os.path.join(self.L, "file-ledger.jsonl")
        self.ideas = os.path.join(self.L, "idea-ledger.jsonl")
        self.rules = os.path.join(self.L, "rules.json")
        rules = {"rules": [
            {"id": "R1", "glob": self.cur + "/*", "disposition": "keep", "reason": "current implementation", "ideas": "none"},
            {"id": "R2", "glob": self.old + "/copy.py", "disposition": "removal-candidate", "reason": "byte copy of pkg/rank.py", "ideas": "none"},
            {"id": "R3", "glob": self.old + "/docs/*", "disposition": "archive", "reason": "spec grouping still useful"},
        ]}
        with open(self.rules, "w") as fh:
            json.dump(rules, fh)

    def tearDown(self):
        shutil.rmtree(self.t, ignore_errors=True)

    def inv(self):
        return run("inventory.py", "--ledger", self.files, "--root", f"current={self.cur}", "--root",
                   f"old={self.old}", "--rules", self.rules, "--no-known", "--run-out", os.path.join(self.L, "run.json"))

    def test_inventory_hashes_skips_and_finds_copies(self):
        self.inv()
        rows = {r["path"]: r for r in jl(self.files)}
        self.assertEqual(len(rows), 3)
        self.assertNotIn(os.path.join(self.old, "node_modules", "x.js"), rows)
        copy = rows[os.path.join(self.old, "copy.py")]
        self.assertEqual(copy["disposition"], "removal-candidate")
        self.assertEqual(copy["same_as"], os.path.join(self.cur, "pkg", "rank.py"))
        with open(os.path.join(self.L, "run.json")) as fh:
            run_rec = json.load(fh)
        self.assertTrue(any("node_modules" in s for s in run_rec["skipped"]))

    def test_rerun_keeps_unchanged_and_resets_changed(self):
        self.inv()
        spec = os.path.join(self.old, "docs", "spec.md")
        wjl(os.path.join(self.t, "cov.jsonl"), [{"path": spec, "status": "mined"}])
        run("record_mining.py", "--ledger", self.files, "--coverage", os.path.join(self.t, "cov.jsonl"))
        out = self.inv().stdout
        self.assertIn('"unchanged": 3', out)
        self.assertEqual({r["path"]: r for r in jl(self.files)}[spec]["ideas_status"], "mined")
        with open(spec, "a") as fh:
            fh.write("\nNew idea.\n")
        self.inv()
        row = {r["path"]: r for r in jl(self.files)}[spec]
        self.assertEqual(row["ideas_status"], "pending")
        self.assertIn("previous_sha256", row)

    def test_missing_file_is_marked_not_dropped(self):
        self.inv()
        os.remove(os.path.join(self.old, "copy.py"))
        self.inv()
        row = {r["path"]: r for r in jl(self.files)}[os.path.join(self.old, "copy.py")]
        self.assertIn("missing", row)

    def test_unmatched_file_stays_pending_and_gate_refuses(self):
        with open(os.path.join(self.old, "stray.txt"), "w") as fh:
            fh.write("stray")
        self.inv()
        wjl(self.ideas, [])
        r = run("check_ledgers.py", "--files", self.files, "--ideas", self.ideas, "--canonical-root", self.cur, ok=False)
        self.assertEqual(r.returncode, 1)
        self.assertIn("stray.txt: disposition 'pending'", r.stdout)

    def ledger_ok(self):
        self.inv()
        spec = os.path.join(self.old, "docs", "spec.md")
        wjl(os.path.join(self.t, "cov.jsonl"), [{"path": spec, "status": "mined"}])
        run("record_mining.py", "--ledger", self.files, "--coverage", os.path.join(self.t, "cov.jsonl"))
        wjl(os.path.join(self.t, "ideas-a.jsonl"), [
            {"id": "A-001", "version": "old", "source": spec, "loc": "L3", "quote": "uses a weighted benchmark formula",
             "idea": "Rank with a weighted benchmark formula.", "category": "implemented", "where": "pkg/rank.py:1"},
            {"id": "A-002", "version": "old", "source": spec, "loc": "L5", "quote": "A cache refresh runs weekly.",
             "idea": "Refresh the cache weekly.", "category": "to-incorporate", "target": "pkg/cron.py"},
        ])
        run("ideas_tool.py", "merge", "--ledger", self.ideas, os.path.join(self.t, "ideas-a.jsonl"))
        return spec

    def test_gate_passes_on_a_good_ledger_and_renders(self):
        self.ledger_ok()
        r = run("check_ledgers.py", "--files", self.files, "--ideas", self.ideas, "--canonical-root", self.cur)
        self.assertIn("PASS", r.stdout)
        with open(os.path.join(self.L, "canonical.json"), "w") as fh:
            json.dump({"decision": "current", "canonical_root": self.cur, "reasons": ["tests pass"]}, fh)
        page = os.path.join(self.t, "dossier", "version-ledger.md")
        run("render.py", "--ledgers", self.L, "--page", page)
        with open(page) as fh:
            text = fh.read()
        self.assertIn("## Incorporation list", text)
        self.assertIn("pkg/cron.py", text)
        rc = jl(os.path.join(self.L, "removal-candidates.jsonl"))
        self.assertEqual([os.path.basename(r["path"]) for r in rc], ["copy.py"])

    def test_gate_refuses_bad_quote_missing_fields_and_bad_where(self):
        spec = self.ledger_ok()
        wjl(os.path.join(self.t, "ideas-b.jsonl"), [
            {"id": "B-001", "version": "old", "source": spec, "loc": "L3", "quote": "a sentence that is not there",
             "idea": "x", "category": "rejected", "reason": "worse"},
            {"id": "B-002", "version": "old", "source": spec, "loc": "L5", "quote": "cache refresh",
             "idea": "y", "category": "rejected"},
            {"id": "B-003", "version": "old", "source": spec, "loc": "L5", "quote": "cache refresh",
             "idea": "z", "category": "implemented", "where": "pkg/nothing.py:3"},
            {"id": "B-004", "version": "old", "source": spec, "loc": "L5", "quote": "cache refresh",
             "idea": "w", "category": "duplicate", "duplicate_of": "B-404"},
            {"id": "B-005", "version": "old", "source": spec, "loc": "L5", "quote": "cache refresh",
             "idea": "v", "category": "maybe"},
        ])
        run("ideas_tool.py", "merge", "--ledger", self.ideas, os.path.join(self.t, "ideas-b.jsonl"))
        r = run("check_ledgers.py", "--files", self.files, "--ideas", self.ideas, "--canonical-root", self.cur, ok=False)
        self.assertEqual(r.returncode, 1)
        for needle in ("B-001: quote not found", "B-002: rejected without reason", "B-003: where path does not exist",
                       "B-004: duplicate_of", "B-005: category"):
            self.assertIn(needle, r.stdout)

    def test_archived_file_cannot_hold_unknown(self):
        spec = self.ledger_ok()
        run("ideas_tool.py", "set", "--ledger", self.ideas, "--id", "A-002", "category=unknown", "question=is it wanted?")
        r = run("check_ledgers.py", "--files", self.files, "--ideas", self.ideas, "--canonical-root", self.cur, ok=False)
        self.assertIn("archived but the source of an unknown idea", r.stdout)
        self.assertIn(os.path.basename(spec), r.stdout)

    def test_dupes_suggests_cross_source_pairs(self):
        spec = self.ledger_ok()
        other = os.path.join(self.cur, "pkg", "rank.py")
        wjl(os.path.join(self.t, "ideas-c.jsonl"), [
            {"id": "C-001", "version": "current", "source": other, "loc": "L1", "quote": "weighted benchmark formula",
             "idea": "Rank models with a weighted benchmark formula.", "category": "implemented", "where": "pkg/rank.py"}])
        run("ideas_tool.py", "merge", "--ledger", self.ideas, os.path.join(self.t, "ideas-c.jsonl"))
        r = run("ideas_tool.py", "dupes", "--ledger", self.ideas, "--threshold", "0.4")
        self.assertIn("A-001 | C-001", r.stdout)
        self.assertTrue(spec)

    def test_canonical_map_lists_purpose(self):
        r = run("canonical_map.py", self.cur)
        self.assertIn("pkg/rank.py`: Rank models by a weighted benchmark formula.", r.stdout)

    def test_judge_verdict_survives_rerender(self):
        self.ledger_ok()
        page = os.path.join(self.t, "dossier", "version-ledger.md")
        run("render.py", "--ledgers", self.L, "--page", page)
        rc_path = os.path.join(self.L, "removal-candidates.jsonl")
        rows = jl(rc_path)
        rows[0]["verdict"], rows[0]["judge_reason"] = "confirm", "identical bytes"
        wjl(rc_path, rows)
        run("render.py", "--ledgers", self.L, "--page", page)
        self.assertEqual(jl(rc_path)[0]["verdict"], "confirm")


if __name__ == "__main__":
    unittest.main(verbosity=1)
