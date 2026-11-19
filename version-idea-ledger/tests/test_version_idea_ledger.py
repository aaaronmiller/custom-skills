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

    def test_prefer_makes_canonical_the_original_and_copy_rules_match_copies(self):
        with open(self.rules, "w") as fh:
            json.dump({"rules": [
                {"id": "C1", "glob": "*", "copy": True, "disposition": "removal-candidate", "reason": "byte copy", "ideas": "none"},
                {"id": "C2", "glob": "*", "disposition": "keep", "reason": "original"}]}, fh)
        run("inventory.py", "--ledger", self.files, "--root", f"old={self.old}", "--root", f"current={self.cur}",
            "--rules", self.rules, "--no-known", "--prefer", self.cur)
        rows = {r["path"]: r for r in jl(self.files)}
        canon, copy = os.path.join(self.cur, "pkg", "rank.py"), os.path.join(self.old, "copy.py")
        self.assertEqual(rows[copy]["same_as"], canon)
        self.assertEqual(rows[copy]["rule"], "C1")
        self.assertEqual(rows[canon]["rule"], "C2")

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
        run("screen_removals.py", "--ledgers", self.L)
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

    def test_quote_checked_inside_zip_member_and_html(self):
        import zipfile
        spec = self.ledger_ok()
        zpath = os.path.join(self.old, "docs", "snap.zip")
        with zipfile.ZipFile(zpath, "w") as z:
            z.writestr("v4/notes.md", "# Notes\n\nRetry a failed probe twice.\n")
        hpath = os.path.join(self.old, "docs", "page.html")
        with open(hpath, "w") as fh:
            fh.write("<p>Show the <b>cost</b> per task &amp; per token.</p>")
        self.inv()
        wjl(os.path.join(self.t, "ideas-z.jsonl"), [
            {"id": "Z-001", "version": "old", "source": zpath, "member": "v4/notes.md", "loc": "L3",
             "quote": "Retry a failed probe twice.", "idea": "Retry probes.", "category": "rejected", "reason": "noise"},
            {"id": "Z-002", "version": "old", "source": hpath, "loc": "L1", "quote": "cost per task & per token",
             "idea": "Show both costs.", "category": "rejected", "reason": "noise"},
            {"id": "Z-003", "version": "old", "source": zpath, "member": "v4/notes.md", "loc": "L3",
             "quote": "Retry three times.", "idea": "x", "category": "rejected", "reason": "noise"}])
        run("ideas_tool.py", "merge", "--ledger", self.ideas, os.path.join(self.t, "ideas-z.jsonl"))
        r = run("check_ledgers.py", "--files", self.files, "--ideas", self.ideas, "--canonical-root", self.cur,
                "--allow-pending", ok=False)
        self.assertNotIn("Z-001: quote", r.stdout)
        self.assertNotIn("Z-002: quote", r.stdout)
        self.assertIn("Z-003: quote not found", r.stdout)
        self.assertTrue(spec)

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


class RemovalScreen(unittest.TestCase):
    """One test per screen rule (H1 to H5), each a lesson from the 2026-11-19 model-scan judge."""

    def setUp(self):
        self.t = tempfile.mkdtemp()
        self.cur = os.path.join(self.t, "current")
        self.old = os.path.join(self.t, "old")
        os.makedirs(self.cur)
        os.makedirs(self.old)
        self.L = os.path.join(self.t, "dossier", "ledgers")
        os.makedirs(self.L)
        self.files = os.path.join(self.L, "file-ledger.jsonl")
        self.ideas = os.path.join(self.L, "idea-ledger.jsonl")
        self.rules = os.path.join(self.L, "rules.json")
        self.protect = []
        wjl(self.ideas, [])

    def tearDown(self):
        shutil.rmtree(self.t, ignore_errors=True)

    def put(self, rel, text, root=None):
        path = os.path.join(root or self.old, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w" if isinstance(text, str) else "wb") as fh:
            fh.write(text)
        return path

    def zip(self, rel, members):
        import zipfile
        path = os.path.join(self.old, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with zipfile.ZipFile(path, "w") as z:
            for name, text in members.items():
                z.writestr(name, text)
        return path

    def screen(self, *extra):
        """Everything under old/ is proposed for removal; current/ is kept."""
        with open(self.rules, "w") as fh:
            json.dump({"protect": self.protect, "rules": [
                {"id": "KEEP", "glob": self.cur + "/*", "disposition": "keep", "reason": "current", "ideas": "none"},
                {"id": "OLD", "glob": self.old + "/*", "disposition": "removal-candidate",
                 "reason": "superseded snapshot", "ideas": "none"}]}, fh)
        run("inventory.py", "--ledger", self.files, "--root", f"current={self.cur}", "--root", f"old={self.old}",
            "--rules", self.rules, "--no-known", "--prefer", self.cur)
        run("screen_removals.py", "--ledgers", self.L, *extra)
        return {r["path"]: r for r in jl(self.files)}

    def assertHeld(self, row, code):
        self.assertEqual(row["disposition"], "archive", row)
        self.assertEqual(row["rule_disposition"], "removal-candidate")
        self.assertTrue(any(h.startswith(code) for h in row["held"]), row["held"])

    def assertPassed(self, row, kind):
        self.assertEqual(row["disposition"], "removal-candidate", row.get("held"))
        self.assertEqual(row["survivor"]["kind"], kind)
        self.assertEqual(row["screened_sha256"], row["sha256"])

    def test_h4_copy_counts_only_if_it_survives_the_whole_set(self):
        # 182 of 266 counterparts were candidates too: two identical candidates, no kept copy.
        a = self.put("v1/notes.md", "# Notes\n\nA unique benchmark table.\n")
        b = self.put("v2/notes.md", "# Notes\n\nA unique benchmark table.\n")
        rows = self.screen()
        self.assertHeld(rows[a], "H4")  # first in keeper order is kept
        self.assertPassed(rows[b], "loose")
        self.assertEqual(rows[b]["survivor"]["path"], a)

    def test_h4_copy_of_a_kept_file_passes(self):
        self.put("rank.py", "def rank():\n    return []\n", root=self.cur)
        c = self.put("rank.py", "def rank():\n    return []\n")
        self.assertPassed(self.screen()[c], "loose")

    def test_h4_generated_output_and_superseded_data_without_copy_are_held(self):
        csv = self.put("data/old-comparison.csv", "model,score\na,1\nb,2\n")
        dash = self.put("dashboard.html", "<script>const DATA=[1,2,3]</script>")
        log = self.put("logs/run.log", "2026-08-11 run ok\n")
        cov = self.put(".coverage", "binary-ish coverage data")
        rows = self.screen()
        for p in (csv, dash, log, cov):
            self.assertHeld(rows[p], "H4")

    def test_h4_only_fixed_ephemeral_types_pass_without_copy(self):
        pid = self.put("run/scan.pid", "4242\n")
        self.assertPassed(self.screen()[pid], "ephemeral")

    def test_h4_survivor_rehashed_live_same_name_is_not_same_file(self):
        # The fold changed verify_dashboard.py after inventory: its declared copy no longer matches.
        kept = self.put("verify.py", "print('v1')\n", root=self.cur)
        c = self.put("verify.py", "print('v1')\n")
        with open(self.rules, "w") as fh:
            json.dump({"rules": [
                {"id": "KEEP", "glob": self.cur + "/*", "disposition": "keep", "reason": "current", "ideas": "none"},
                {"id": "OLD", "glob": self.old + "/*", "disposition": "removal-candidate", "reason": "copy",
                 "ideas": "none"}]}, fh)
        run("inventory.py", "--ledger", self.files, "--root", f"current={self.cur}", "--root", f"old={self.old}",
            "--rules", self.rules, "--no-known", "--prefer", self.cur)
        with open(kept, "w") as fh:
            fh.write("print('v2 with playwright')\n")
        run("screen_removals.py", "--ledgers", self.L)
        self.assertHeld({r["path"]: r for r in jl(self.files)}[c], "H4")

    def test_h1_candidate_changed_since_inventory_is_held(self):
        self.put("a.py", "x = 1\n", root=self.cur)
        c = self.put("a.py", "x = 1\n")
        self.screen()
        with open(c, "a") as fh:
            fh.write("y = 2\n")
        run("screen_removals.py", "--ledgers", self.L)
        self.assertHeld({r["path"]: r for r in jl(self.files)}[c], "H1")

    def test_h2_idea_source_is_held_until_repointed(self):
        kept = self.put("spec.md", "# Spec\n\nRetry twice.\n", root=self.cur)
        c = self.put("spec.md", "# Spec\n\nRetry twice.\n")
        wjl(self.ideas, [{"id": "X-001", "version": "old", "source": c, "loc": "L3", "quote": "Retry twice.",
                          "idea": "Retry twice.", "category": "rejected", "reason": "noise"}])
        self.assertHeld(self.screen()[c], "H2")
        run("ideas_tool.py", "set", "--ledger", self.ideas, "--id", "X-001", f"source={kept}")
        run("screen_removals.py", "--ledgers", self.L)
        self.assertPassed({r["path"]: r for r in jl(self.files)}[c], "loose")

    def test_h3_operator_words_held_even_with_a_byte_copy(self):
        self.put("user-prompt-aggregation.md", "do the thing\n", root=self.cur)
        c = self.put("user-prompt-aggregation.md", "do the thing\n")
        t = self.put("qwen-transcript.md", "chat\n")
        rows = self.screen()
        self.assertHeld(rows[c], "H3")
        self.assertHeld(rows[t], "H3")

    def test_h3_credential_handling_text_held(self):
        self.put("plan.md", "Load OPENROUTER_API_KEY from the vault, never inline.\n", root=self.cur)
        c = self.put("plan.md", "Load OPENROUTER_API_KEY from the vault, never inline.\n")
        self.assertHeld(self.screen()[c], "H3")

    def test_h3_protect_glob_from_rules(self):
        self.put("ledger.tsv", "a\tb\n", root=self.cur)
        c = self.put("audit/ledger.tsv", "a\tb\n")
        self.protect = [{"glob": self.old + "/audit/*", "reason": "lineage audit evidence"}]
        self.assertHeld(self.screen()[c], "H3")

    def test_h3_archive_with_protected_member_held(self):
        z = self.zip("rel/v6.zip", {"v6/sources/prompt ot make it.md": "build it\n"})
        self.put("v6/sources/prompt ot make it.md", "build it\n", root=self.cur)
        self.assertHeld(self.screen()[z], "H3")

    def test_h5_zip_with_exclusive_member_held_and_its_loose_copies_released(self):
        z = self.zip("rel/v4.zip", {"v4/a.md": "shared\n", "v4/only-here.md": "exclusive payload\n"})
        loose = self.put("v4-extract/a.md", "shared\n")
        rows = self.screen()
        self.assertHeld(rows[z], "H5")
        self.assertPassed(rows[loose], "zip-member")
        self.assertEqual(rows[loose]["survivor"]["member"], "v4/a.md")

    def test_h5_zip_whose_members_all_survive_passes(self):
        self.put("a.md", "shared\n", root=self.cur)
        z = self.zip("rel/v5.zip", {"v5/a.md": "shared\n"})
        self.assertPassed(self.screen()[z], "members")

    def test_h4_loose_copy_inside_a_removed_zip_is_not_a_survivor(self):
        # Two zips hold the same exclusive member: one zip is kept, the other and the loose copy go.
        z1 = self.zip("a/rel.zip", {"x.md": "payload\n"})
        z2 = self.zip("b/rel.zip", {"x.md": "payload\n"})
        loose = self.put("c/x.md", "payload\n")
        rows = self.screen()
        held = [p for p in (z1, z2, loose) if rows[p]["disposition"] == "archive"]
        self.assertEqual(len(held), 1, [rows[p].get("held") for p in (z1, z2, loose)])
        for p in (z1, z2, loose):
            if p not in held:
                sv = rows[p]["survivor"]
                paths = [m["path"] for m in sv.get("members", [sv])]
                self.assertTrue(all(q in held for q in paths), (p, sv, held))

    def test_git_blob_counts_only_in_a_named_tree(self):
        repo = self.cur
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                   GIT_COMMITTER_EMAIL="t@t")
        g = lambda *a: subprocess.run(["git", "-C", repo, *a], check=True, capture_output=True, env=env)
        g("init", "-q")
        self.put("calibrate.py", "fold version\n", root=repo)
        g("add", "-A")
        g("commit", "-qm", "fold")
        fold = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        self.put("calibrate.py", "later version\n", root=repo)
        g("commit", "-qam", "change")
        c = self.put("calibrate.py", "fold version\n")
        rows = self.screen("--git-root", repo)
        self.assertHeld(rows[c], "H4")  # only in history, not in HEAD
        run("screen_removals.py", "--ledgers", self.L, "--git-root", repo, "--git-root", f"{repo}@{fold[:7]}")
        row = {r["path"]: r for r in jl(self.files)}[c]
        self.assertPassed(row, "git-blob")
        self.assertTrue(row["survivor"]["tree_path"].startswith(fold + ":"))

    def test_render_and_gate_refuse_unscreened_candidates_and_inventory_clears_stamps(self):
        self.put("a.py", "x = 1\n", root=self.cur)
        c = self.put("a.py", "x = 1\n")
        self.screen()
        run("inventory.py", "--ledger", self.files, "--root", f"current={self.cur}", "--root", f"old={self.old}",
            "--rules", self.rules, "--no-known", "--prefer", self.cur)
        row = {r["path"]: r for r in jl(self.files)}[c]
        self.assertNotIn("survivor", row)
        page = os.path.join(self.t, "dossier", "page.md")
        r = run("render.py", "--ledgers", self.L, "--page", page, ok=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("screen_removals.py", r.stdout + r.stderr)
        r = run("check_ledgers.py", "--files", self.files, "--ideas", self.ideas, "--canonical-root", self.cur, ok=False)
        self.assertIn("without a current screen stamp", r.stdout)
        run("screen_removals.py", "--ledgers", self.L)
        run("render.py", "--ledgers", self.L, "--page", page)
        rc = jl(os.path.join(self.L, "removal-candidates.jsonl"))
        self.assertEqual(rc[0]["survivor"]["kind"], "loose")

    def test_screen_never_deletes(self):
        a = self.put("v1/notes.md", "same\n")
        b = self.put("v2/notes.md", "same\n")
        self.screen()
        self.assertTrue(os.path.exists(a) and os.path.exists(b))


if __name__ == "__main__":
    unittest.main(verbosity=1)
