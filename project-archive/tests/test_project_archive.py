#!/usr/bin/env python3
"""Unit and integration tests for the project-archive skill. Standard library only.

Usage: python3 -I -B tests/test_project_archive.py [--tmp DIR] [-v]

Every test builds its own fixture in a fresh temporary directory (under --tmp
when given) and removes only that directory afterwards. No other path is written.
"""
import ast
import json
import os
import shlex
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
S = os.path.join(HERE, "scripts")
sys.path.insert(0, S)
sys.path.insert(0, os.path.join(HERE, "tests", "fixtures"))
import _lib as L  # noqa: E402
import build_fixture as B  # noqa: E402

TMP = None


def py(script, *args, env=None):
    r = subprocess.run([sys.executable, "-I", "-B", os.path.join(S, script)] + list(args), capture_output=True, text=True, env=env)
    return r.returncode, r.stdout, r.stderr


class Base(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory(dir=TMP)
        self.box = self._td.name
        self.top = B.build(os.path.join(self.box, "fx"))
        self.root = os.path.join(self.top, "root")
        self.pa = os.path.join(self.root, "proj-a")
        self.pb = os.path.join(self.root, "proj-b")
        self.da = os.path.join(self.top, "archive-root", "demo", "proj-a")

    def tearDown(self):
        self._td.cleanup()

    def plan(self, staging, approval=True, hold=True, folder=None, dest=None):
        args = ["--folder", folder or self.pa, "--dest", dest or self.da, "--roots", self.root, "--staging", staging]
        if hold:
            args += ["--hold-file", os.path.join(self.top, "hold.yaml")]
        if approval:
            args += ["--approval", os.path.join(self.top, "approval-proj-a.json")]
        return py("plan.py", *args)


class Consumers(Base):
    def test_three_planted_consumers_and_near_miss_ignored(self):
        rc, so, se = py("consumers.py", self.pa, "--roots", self.root, "--json", os.path.join(self.box, "c.json"))
        self.assertEqual(rc, 0, se)
        res = L.read_json(os.path.join(self.box, "c.json"))
        got = sorted((c["kind"], os.path.relpath(c["path"], self.root)) for c in res["consumers"])
        self.assertEqual(got, [("path-reference", "config/app.json"), ("path-reference", "scripts/run.sh"), ("symlink", "tools/proj-a-link")])
        self.assertNotIn("unrelated.sh", so)

    def test_secrets_never_printed(self):
        secret = "sk-" + "Q7x9" * 8
        with open(os.path.join(self.root, "config", "deploy.conf"), "w") as fh:
            fh.write("path=%s api_key=%s\n" % (self.pa, secret))
        with open(os.path.join(self.root, "config", ".env"), "w") as fh:
            fh.write("DATA=%s\nTOKEN=%s\n" % (self.pa, secret))
        rc, so, se = py("consumers.py", self.pa, "--roots", self.root, "--json", os.path.join(self.box, "c.json"))
        with open(os.path.join(self.box, "c.json")) as fh:
            blob = so + se + fh.read()
        self.assertNotIn(secret, blob)
        self.assertIn("withheld: sensitive file name", blob)
        self.assertIn("[redacted]", blob)

    def test_internal_absolute_refs_reported(self):
        with open(os.path.join(self.pa, "venv.cfg"), "w") as fh:
            fh.write("home = %s/bin\n" % self.pa)
        rc, so, _ = py("consumers.py", self.pa, "--roots", self.root)
        self.assertIn("internal absolute self-references: 1", so)


class PlanAndMover(Base):
    def test_no_approval_is_refused_never_class(self):
        st = os.path.join(self.box, "st")
        d0 = L.tree_digest(self.pa)
        self.plan(st, approval=False, hold=False)
        rc, so, _ = py("move_dryrun.py", "--staging", st)
        self.assertEqual(rc, 2)
        self.assertIn("REFUSED (never-class)", so)
        self.assertEqual(L.tree_digest(self.pa), d0)

    def test_seven_artifacts_and_readiness(self):
        st = os.path.join(self.box, "st")
        rc, so, se = self.plan(st)
        self.assertEqual(rc, 0, se)
        for n in ("consumers.json", "manifest.json", "path-map.json", "old-path-links.json", "working-copy-repair.json",
                  "live-use-guard.json", "sandbox-test.json", "readiness.json"):
            self.assertTrue(os.path.isfile(os.path.join(st, n)), n)
        r = L.read_json(os.path.join(st, "readiness.json"))
        self.assertTrue(r["ready"], r["blockers"])
        self.assertEqual(r["move_class"], "never")
        self.assertTrue(L.read_json(os.path.join(st, "sandbox-test.json"))["passed"])
        pm = L.read_json(os.path.join(st, "path-map.json"))
        self.assertEqual(len(pm["rewrites"]), 2)
        self.assertEqual(len(pm["relinks"]), 1)
        rc, so, _ = py("move_dryrun.py", "--staging", st)
        self.assertEqual(rc, 0)
        self.assertIn("DRY RUN", so)
        self.assertIn("ln -s -- %s %s" % (self.da, self.pa), so)
        self.assertTrue(os.path.isdir(self.pa) and not os.path.exists(self.da))

    def test_tampered_artifact_refused(self):
        st = os.path.join(self.box, "st")
        self.plan(st)
        with open(os.path.join(st, "consumers.json"), "a") as fh:
            fh.write(" ")
        rc, so, _ = py("move_dryrun.py", "--staging", st)
        self.assertEqual(rc, 2)
        self.assertIn("changed after it was recorded", so)

    def test_approval_for_other_move_refused(self):
        st = os.path.join(self.box, "st")
        self.plan(st, dest=os.path.join(self.top, "archive-root", "elsewhere", "proj-a"))
        rc, so, _ = py("move_dryrun.py", "--staging", st)
        self.assertEqual(rc, 2)
        self.assertIn("exact source and destination", so)

    def test_live_use_guard_defers_recent_changes(self):
        st = os.path.join(self.box, "st")
        self.plan(st)
        with open(os.path.join(self.pa, "README.md"), "a") as fh:
            fh.write("touched\n")
        rc, so, _ = py("move_dryrun.py", "--staging", st)
        self.assertEqual(rc, 2)
        self.assertIn("live-use guard", so)

    def test_staging_inside_folder_refused(self):
        rc, _, se = self.plan(os.path.join(self.pa, "staging"))
        self.assertEqual(rc, 2)
        self.assertIn("refused", se)

    def test_mover_has_no_effect_calls(self):
        with open(os.path.join(S, "move_dryrun.py")) as fh:
            tree = ast.parse(fh.read())
        banned = {"rename", "replace", "move", "symlink", "unlink", "remove", "rmtree", "link", "makedirs", "mkdir", "system", "run", "Popen", "copy", "copy2", "copytree", "chmod"}
        calls = [n.func.attr for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in banned]
        self.assertEqual(calls, [])

    def test_git_facts_do_not_write_the_repo(self):
        before = L.tree_digest(self.pb)
        L.git_facts(self.pb)
        py("consumers.py", self.pb, "--roots", self.root)
        self.assertEqual(L.tree_digest(self.pb), before)


class ArchiveOrder(Base):
    def gate(self, allowed):
        p = os.path.join(self.box, "gate.json")
        with open(p, "w") as fh:
            json.dump({"schema": "lineage-gate/1", "folder": self.pb, "allowed": allowed,
                       "unique_without_destination": 0 if allowed else 1, "counts": {}, "clauses": []}, fh)
        return p

    def test_out_of_order_steps_refused(self):
        w = os.path.join(self.box, "w")
        self.assertEqual(py("archive.py", "index", "--work", w)[0], 3)
        self.assertEqual(py("archive.py", "move", "--work", w)[0], 3)

    def test_mine_refused_when_lineage_gate_refuses(self):
        rc, _, se = py("archive.py", "mine", "--work", os.path.join(self.box, "w"), "--folder", self.pb, "--archive-root",
                       os.path.join(self.top, "archive-root"), "--project", "demo", "--lineage-gate", self.gate(False))
        self.assertEqual(rc, 4)
        self.assertIn("DA-034", se)

    def test_mine_twice_refused_and_real_move_only_printed(self):
        w = os.path.join(self.box, "w")
        ar = os.path.join(self.top, "archive-root")
        args = ["--work", w, "--folder", self.pb, "--archive-root", ar, "--project", "demo", "--lineage-gate", self.gate(True)]
        self.assertEqual(py("archive.py", "mine", *args)[0], 0)
        self.assertEqual(py("archive.py", "mine", *args)[0], 3)
        self.assertEqual(py("archive.py", "index", "--work", w)[0], 0)
        db = os.path.join(ar, "demo", "proj-b")
        py("plan.py", "--folder", self.pb, "--dest", db, "--roots", self.root, "--staging", os.path.join(w, "plan"),
           "--approval", os.path.join(self.top, "approval-proj-b.json"))
        rc, so, _ = py("archive.py", "move", "--work", w)
        self.assertEqual(rc, 0)
        self.assertIn("DRY RUN", so)
        self.assertTrue(os.path.isdir(self.pb) and not os.path.islink(self.pb) and not os.path.exists(db))
        self.assertEqual([r["step"] for r in L.read_receipts(w)], ["mine", "index"])
        rc, _, se = py("archive.py", "move", "--work", w, "--sandbox-root", self.box)
        self.assertEqual(rc, 3)
        self.assertIn("marker", se)

    def test_discovery_check_fails_without_exclusion(self):
        cfg = os.path.join(self.box, "disc.json")
        os.makedirs(os.path.join(self.top, "archive-root", "demo", "old", ".git"))
        with open(cfg, "w") as fh:
            json.dump({"roots": [self.top], "exclude": []}, fh)
        rc, so, _ = py("discovery.py", "check", "--config", cfg, "--archive-root", os.path.join(self.top, "archive-root"))
        self.assertEqual(rc, 1)
        self.assertIn("no exclude entry", so)
        rc, so, _ = py("discovery.py", "check", "--config", os.path.join(self.top, "discovery.json"), "--archive-root", os.path.join(self.top, "archive-root"))
        self.assertEqual(rc, 0, so)


HOSTILE = "odd name;touch pwned$(id)`id`'q\"x"


class PrintedCommandsAreQuoted(Base):
    """Commands the scripts print or record are pasted into a shell by a person.

    Paths reach them from the command line and from a scan of the disk, so each
    one must survive a shell round trip as exactly one argument.
    """

    def test_repair_commands_round_trip(self):
        import plan as P  # scripts folder is on sys.path
        dest = os.path.join(self.top, "dest " + HOSTILE)
        wt = os.path.join(self.top, "linked " + HOSTILE)
        facts = {"is_linked_worktree": True, "worktrees": []}
        cons = {"consumers": [{"kind": "linked-worktree", "path": wt}], "internal_absolute_refs": []}
        cmds = P.working_copy_repair(self.pa, dest, facts, cons)["commands"]
        self.assertEqual([shlex.split(c) for c in cmds],
                         [["git", "-C", dest, "worktree", "repair"],
                          ["git", "-C", wt, "worktree", "repair", dest]])

    def test_old_path_link_command_round_trips(self):
        st = os.path.join(self.box, "st")
        dest = os.path.join(self.top, "archive-root", "demo", "proj " + HOSTILE)
        self.plan(st, dest=dest)
        links = L.read_json(os.path.join(st, "old-path-links.json"))["links"][0]
        self.assertEqual(shlex.split(links["command"]), ["ln", "-s", "--", dest, self.pa])

    def test_recovery_steps_in_the_archive_record_round_trip(self):
        folder = os.path.join(self.root, "proj " + HOSTILE)
        os.makedirs(folder)
        with open(os.path.join(folder, "README.md"), "w") as fh:
            fh.write("# odd\n")
        gate = os.path.join(self.box, "gate.json")
        with open(gate, "w") as fh:
            json.dump({"schema": "lineage-gate/1", "folder": folder, "allowed": True,
                       "unique_without_destination": 0, "counts": {}, "clauses": []}, fh)
        w = os.path.join(self.box, "w")
        ar = os.path.join(self.top, "archive-root")
        rc, _, se = py("archive.py", "mine", "--work", w, "--folder", folder, "--archive-root", ar,
                       "--project", "demo", "--lineage-gate", gate)
        self.assertEqual(rc, 0, se)
        rc, _, se = py("archive.py", "index", "--work", w)
        self.assertEqual(rc, 0, se)
        steps = L.read_json(os.path.join(w, "archive-record.json"))["recovery"]["human_steps"]
        dest = os.path.join(ar, "demo", os.path.basename(folder))
        head = steps.split(" ; then run")[0]  # "unlink A ; mv B C"
        unlink, mv = head.split(" ; ")
        self.assertEqual(shlex.split(unlink), ["unlink", folder])
        self.assertEqual(shlex.split(mv), ["mv", dest, folder])


class Redaction(unittest.TestCase):
    def test_url_userinfo_is_masked(self):
        for raw in ("https://alice:hunter2@example.com/r.git", "https://ghp_abcdefghijkl1234@github.com/o/r.git",
                    "ssh://user@host.example/r.git"):
            out = L.redact(raw)
            self.assertNotIn("hunter2", out)
            self.assertNotIn("ghp_abcdefghijkl1234", out)
            self.assertNotIn("alice", out)
            self.assertIn("[redacted]@", out)
        self.assertEqual(L.redact("https://example.com/r.git"), "https://example.com/r.git")

    def test_git_facts_redact_remotes_and_stash_messages(self):
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            def git(*a):
                r = subprocess.run(["git", "-C", td, "-c", "user.name=t", "-c", "user.email=t@example.com",
                                    "-c", "commit.gpgsign=false"] + list(a), capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, r.stderr)
            git("init", "-q")
            with open(os.path.join(td, "f.txt"), "w") as fh:
                fh.write("one\n")
            git("add", "f.txt")
            git("commit", "-q", "-m", "init")
            git("remote", "add", "origin", "https://alice:hunter2@example.com/r.git")
            with open(os.path.join(td, "f.txt"), "w") as fh:
                fh.write("two\n")
            git("stash", "push", "-q", "-m", "wip password=hunter2 token=abcd1234")
            facts = L.git_facts(td)
            blob = json.dumps(facts)
            self.assertNotIn("hunter2", blob)
            self.assertNotIn("abcd1234", blob)
            self.assertEqual(facts["stash_count"], 1)
            self.assertEqual(facts["remotes"], ["https://[redacted]@example.com/r.git"])


class Contract(unittest.TestCase):
    def test_contract_program_passes(self):
        pl = os.path.join(os.path.dirname(HERE), "portfolio-lineage")
        if not os.path.isdir(pl) and not os.environ.get("PORTFOLIO_LINEAGE_DIR"):
            self.skipTest("portfolio-lineage is not installed beside project-archive")
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            r = subprocess.run([sys.executable, "-I", "-B", os.path.join(HERE, "bin", "contract"), "--fixture", "", "--sandbox", os.path.join(td, "s")],
                               capture_output=True, text=True)
            out = json.loads(r.stdout)
            bad = [c for c in out["checks"] if not c["ok"]]
            self.assertEqual(bad, [])
            self.assertEqual(r.returncode, 0)


if __name__ == "__main__":
    if "--tmp" in sys.argv:
        i = sys.argv.index("--tmp")
        TMP = os.path.abspath(sys.argv[i + 1])
        del sys.argv[i:i + 2]
    unittest.main()
