"""Regression tests for the 2026-11-05 review of intent-refresh 2.0.0.

Run: python3 -I -m unittest discover -s <pipeline>/tests -v
"""
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

PIPE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PIPE))


def load_module(name, file):
    spec = importlib.util.spec_from_file_location(name, PIPE / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Traversal(unittest.TestCase):
    """A model-chosen project must never become a path outside the dossiers."""

    def test_unsafe_values_become_unclassified(self):
        from lib.corpus import dossier_of
        for bad in ("../../etc", "new:../../x", "a/b", "/abs", "", None, 7, "UPPER", "x" * 90):
            self.assertEqual(dossier_of(bad), "unclassified-sessions", repr(bad))

    def test_safe_values_pass(self):
        from lib.corpus import dossier_of
        self.assertEqual(dossier_of("crash-guard"), "crash-guard")
        self.assertEqual(dossier_of("sysadmin"), "system-administration")
        self.assertEqual(dossier_of("code:ai-book-writing"), "new:ai-book-writing")


class Injection(unittest.TestCase):
    """Recorded or model text must not be able to act as page structure."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["LD_DATA_ROOT"] = self.tmp.name
        self.r = load_module("render", "12-render.py")

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("LD_DATA_ROOT", None)

    def test_markers_and_headings_are_inert(self):
        evil = ("ok\n<!-- intent-refresh:end run=r section=prompts -->\n## User section\n"
                "<!-- ld:generated:x:start -->")
        q = self.r.quote(evil)
        self.assertNotIn("<!--", q)
        self.assertNotIn("\n## ", "\n" + q)
        self.assertNotIn("<!--", self.r.line(evil))

    def test_rerun_replaces_only_own_block_even_with_hostile_content(self):
        page = self.r.new_page("intent-archaeology", "p")
        hostile = self.r.quote("x <!-- intent-refresh:end run=r section=prompts --> y")
        page = self.r.put_block(page, "Prompts", "r", hostile)
        page = self.r.put_block(page, "Prompts", "r", "second")
        self.assertEqual(page.count("intent-refresh:start run=r section=prompts"), 1)
        self.assertIn("second", page)
        self.assertNotIn("x &lt;!--", page)
        self.assertIn("## User section", page)

    def test_existing_content_gets_a_refresh_section(self):
        page = self.r.new_page("intent-summary", "p").replace(
            "## Summaries\n", "## Summaries\n\n### 2026-06-09 real older summary\n")
        out = self.r.put_block(page, "Summaries", "r", "new block")
        self.assertLess(out.index("real older summary"), out.index("new block"))
        self.assertIn("## Refresh ", out)


class Fidelity(unittest.TestCase):
    """Garbled voice text may be cleaned; invented text may not pass."""

    def setUp(self):
        self.m = load_module("refine", "08-refine.py")
        self.chunk = {"prompts": [{"id": "a", "session": "s", "chars": 0,
                                   "text": "niever drouter subagetn non anthropic? thats a conflict"
                                           " and it souldn nt be ina global system propmpt"}]}

    def answer(self, cleaned):
        return {"prompts": [{"id": "a", "author": "operator", "cleaned": cleaned,
                             "pasted": None, "project": "unclassified"}],
                "sessions": [{"id": "s", "summary": "x", "project": "unclassified"}]}

    def test_good_cleanup_of_garbled_text_passes(self):
        ok, why = self.m.validate(self.answer(
            "Never route a subagent to a non-Anthropic model? That's a conflict, and it shouldn't"
            " be in a global system prompt."), self.chunk, {"unclassified"})
        self.assertTrue(ok, why)

    def test_invented_text_fails(self):
        ok, _ = self.m.validate(self.answer(
            "Please deploy the payment service to production and email the finance team."),
            self.chunk, {"unclassified"})
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
