"""Tests for the agy backend of imagegen.sh (security review fixes, BACKLOG B074).

The 2026-11-09 review fixes (contain the backend, refuse planted symlinks and hard links,
close the TOCTOU race) had no committed tests. A stub `agy` on PATH plays the agent and
leaves whatever file the case needs at out.png in the workspace it was started in.

Run:  python3 -I -B -m unittest discover -s imagegen/tests
"""
import glob
import os
import pathlib
import subprocess
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "bin" / "imagegen.sh"
PNG = b"\x89PNG\r\n\x1a\nfakepixels"

STUB = r"""#!/usr/bin/env bash
case "${STUB_MODE:-png}" in
  png)      printf '\x89PNG\r\n\x1a\nfakepixels' > out.png;;
  none)     :;;
  symlink)  ln -s "$STUB_TARGET" out.png;;
  hardlink) ln "$STUB_TARGET" out.png;;
  fifo)     mkfifo out.png;;
  notpng)   echo "not a png" > out.png;;
  big)      python3 -I -c "f=open('out.png','wb'); f.write(b'\x89PNG\r\n\x1a\n'); f.truncate(70*1024*1024)";;
esac
exit 0
"""


class AgyBackend(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="imagegen-test-")
        self.root = pathlib.Path(self.tmp.name)
        (self.root / "bin").mkdir()
        (self.root / "work").mkdir()
        stub = self.root / "bin" / "agy"
        stub.write_text(STUB)
        stub.chmod(0o755)
        self.secret = self.root / "secret.txt"
        self.secret.write_text("TOP-SECRET")
        self.out = self.root / "outdir" / "image.png"

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, mode="png", *extra, ref=None, timeout=60):
        env = {"PATH": f"{self.root / 'bin'}:{os.environ['PATH']}", "HOME": str(self.root),
               "TMPDIR": str(self.root / "work"), "STUB_MODE": mode, "STUB_TARGET": str(self.secret)}
        cmd = ["bash", str(SCRIPT), "-b", "agy", "-p", "a red panda", "-o", str(self.out), *extra]
        if ref:
            cmd += ["-r", str(ref)]
        return subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=timeout)

    def leftovers(self):
        return glob.glob(str(self.root / "work" / "imagegen-agy.*")) + glob.glob(str(self.out) + ".imagegen-tmp*")

    def assertNoImage(self, r):
        self.assertNotEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), "", "a failed run must not print a path")
        self.assertEqual(self.leftovers(), [])

    def test_a_valid_png_is_delivered_and_the_workspace_is_removed(self):
        r = self.run_script()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), str(self.out))
        self.assertEqual(self.out.read_bytes(), PNG)
        self.assertEqual(self.leftovers(), [])

    def test_a_planted_symlink_is_refused_and_the_target_never_copied(self):
        r = self.run_script("symlink")
        self.assertNoImage(r)
        self.assertFalse(self.out.exists() and b"TOP-SECRET" in self.out.read_bytes())

    def test_a_hard_link_is_refused(self):
        self.assertNoImage(self.run_script("hardlink"))

    def test_a_fifo_is_refused_without_hanging(self):
        self.assertNoImage(self.run_script("fifo", timeout=30))

    def test_a_file_that_is_not_a_png_is_refused(self):
        self.assertNoImage(self.run_script("notpng"))

    def test_an_oversized_output_is_refused(self):
        r = self.run_script("big")
        self.assertNoImage(r)
        self.assertFalse(self.out.exists())

    def test_no_output_from_agy_is_an_error_even_when_an_old_file_sits_at_the_path(self):
        self.out.parent.mkdir(parents=True)
        self.out.write_bytes(PNG + b"stale")
        r = self.run_script("none")
        self.assertNotEqual(r.returncode, 0, "a stale OUT from an earlier run was reported as this run's image")
        self.assertEqual(r.stdout.strip(), "")
        self.assertEqual(self.leftovers(), [])

    def test_a_leftover_temp_file_does_not_block_later_runs(self):
        self.out.parent.mkdir(parents=True)
        pathlib.Path(str(self.out) + ".imagegen-tmp").write_bytes(b"left by a crashed run")
        r = self.run_script()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.out.read_bytes(), PNG)

    def test_a_timeout_that_is_not_a_plain_number_is_refused_before_any_expansion(self):
        marker = self.root / "MARKER"
        for bad in (f"a[$(touch {marker})]", "5m", "-3", "", "10", "1e3"):
            r = self.run_script("png", "-t", bad)
            self.assertNotEqual(r.returncode, 0, bad)
            self.assertFalse(marker.exists(), f"-t {bad!r} ran a command")
            self.assertEqual(self.leftovers(), [], bad)

    def test_a_plain_timeout_still_works(self):
        r = self.run_script("png", "-t", "30")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_a_reference_without_an_extension_in_a_dotted_directory_works_and_cleans_up(self):
        refdir = self.root / "dir.with.dots"
        refdir.mkdir()
        ref = refdir / "reference"
        ref.write_bytes(PNG)
        r = self.run_script("png", ref=ref)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.leftovers(), [])

    def test_a_missing_reference_cleans_up(self):
        r = self.run_script("png", ref=self.root / "nope.png")
        self.assertNoImage(r)


if __name__ == "__main__":
    unittest.main()
