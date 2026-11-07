"""Offline adapter fixtures and reconciliation regressions (also unittest compatible)."""
import collections
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests/fixtures/ledger"
spec = importlib.util.spec_from_file_location("ledger", ROOT / "scripts/ledger.py")
ledger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ledger)
SINCE = ledger.timestamp("2026-10-24")


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        paths = {"claude.jsonl": ".claude/projects/fixture/session.jsonl",
                 "claude-subagent.jsonl": ".claude/projects/fixture/claude-session/subagents/agent-1.jsonl",
                 "codex.jsonl": ".codex/sessions/2026/11/06/rollout-fixture.jsonl",
                 "omp.jsonl": ".omp/agent/sessions/fixture/session.jsonl",
                 "direct.jsonl": ".local/state/capacity-watch/calls-direct.jsonl",
                 "readings.jsonl": ".local/state/capacity-watch/readings.jsonl"}
        for name, target in paths.items():
            dest = self.home / target
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(FIXTURES / name, dest)
        self.source_db = self.home / ".local/share/opencode/opencode.db"
        self.source_db.parent.mkdir(parents=True)
        with sqlite3.connect(self.source_db) as conn:
            conn.executescript((FIXTURES / "opencode.sql").read_text())
        self.conn = sqlite3.connect(":memory:")
        self.addCleanup(self.conn.close)
        self.conn.executescript(ledger.SCHEMA)
        self.result = ledger.ingest(self.conn, self.home, SINCE, "fixture-host")

    def call(self, harness, message=None):
        self.conn.row_factory = sqlite3.Row
        query = "SELECT * FROM calls WHERE harness=?"
        params = [harness]
        if message:
            query += " AND message_id=?"
            params.append(message)
        return dict(self.conn.execute(query, params).fetchone())

    def test_all_adapters_and_idempotence(self):
        self.assertEqual(self.result["rows_by_harness"],
                         {"claude": 2, "codex": 4, "omp": 3, "opencode": 1, "direct-api": 3})
        before = self.conn.execute("SELECT * FROM calls ORDER BY harness,message_id").fetchall()
        result = ledger.ingest(self.conn, self.home, SINCE, "fixture-host")
        self.assertTrue(all(s["inserted_rows"] == 0 for s in result["adapters"].values()))
        self.assertEqual(before, self.conn.execute("SELECT * FROM calls ORDER BY harness,message_id").fetchall())

    def test_claude_fragments_merge_and_proxy_provider(self):
        r = self.call("claude", "call-1")
        self.assertEqual(r["model"], "muse-spark-1.3-contributor")
        self.assertEqual(r["provider"], "meta")
        self.assertEqual(r["route"], "unknown")
        self.assertEqual([r[f] for f in ledger.TOKEN_FIELDS], [100, 10, 30, 20, 0])
        self.assertEqual(r["outcome"], "ok")

    def test_codex_context_cache_and_snapshot(self):
        r = self.call("codex", "10")
        self.assertEqual(r["model"], "gpt-6-astra")
        self.assertEqual([r[f] for f in ledger.TOKEN_FIELDS], [60, 20, 20, 0, 5])
        self.assertEqual(json.loads(r["window_snapshot"])["plan_type"], "plus")
        self.assertNotIn("secret", r["window_snapshot"])
        self.assertEqual(self.result["adapters"]["codex"]["repeated_usage_events"], 1)

    def test_omp_exact_usage_and_model_changes(self):
        r = self.call("omp", "omp-call")
        self.assertEqual(r["provider"], "opencode-go")
        self.assertEqual(r["route"], "subscription")
        self.assertEqual([r[f] for f in ledger.TOKEN_FIELDS], [80, 20, 15, 5, 3])
        self.assertEqual(r["latency_s"], 1.5)
        self.assertEqual(r["list_cost_usd"], .001)
        missing = self.call("omp", "omp-call-2")
        self.assertIsNone(missing["tokens_in"])
        self.assertEqual(missing["model"], "beam-free")

    def test_opencode_readonly_and_reasoning(self):
        before = self.source_db.read_bytes()
        r = self.call("opencode")
        self.assertEqual([r[f] for f in ledger.TOKEN_FIELDS], [80, 20, 20, 0, 5])
        self.assertEqual(r["latency_s"], 2)
        ledger.ingest(self.conn, self.home, SINCE, "fixture-host")
        self.assertEqual(before, self.source_db.read_bytes())

    def test_opencode_schema_drift_skips(self):
        with sqlite3.connect(self.source_db) as conn:
            conn.execute("ALTER TABLE message RENAME COLUMN data TO unsupported")
        stats = collections.Counter()
        self.assertEqual(list(ledger.opencode(self.home, SINCE, "fixture-host", stats)), [])
        self.assertEqual(stats["schema_mismatch"], 1)

    def test_direct_billing_and_cached_tokens(self):
        rows = ledger.report(self.conn, SINCE, "model")
        muse = next(r for r in rows if r["model"] == "muse-spark-1.3-contributor")
        self.assertEqual(muse["allowance_usd"], .0006)
        self.assertEqual(muse["allowance_known_calls"], 1)
        r = self.call("direct-api")
        self.assertEqual([r[f] for f in ledger.TOKEN_FIELDS], [70, 20, 20, 10, 5])
        self.assertEqual(r["route"], "subscription")

    def test_report_no_double_count_reasoning_or_cache(self):
        r = next(r for r in ledger.report(self.conn, SINCE, "harness") if r["harness"] == "codex")
        self.assertEqual(r["tokens_total"], 400)
        self.assertEqual(r["tokens_reasoning"], 20)
        self.assertIsNone(r["list_cost_usd"])
        self.assertEqual(r["cost_known_calls"], 0)
        self.assertEqual(len(ledger.report(self.conn, SINCE, "day")), 1)

    def test_codex_reconcile_plateau_arithmetic(self):
        result = ledger.reconcile(self.conn, "codex", SINCE, self.home / "missing")
        primary = next(r for r in result["windows"] if r["window"] == "primary")
        self.assertEqual(primary["samples"], 1)
        self.assertEqual(primary["tokens_all"], 300)
        self.assertEqual(primary["tokens_uncached"], 240)
        self.assertEqual(primary["percent_delta"], 3)
        self.assertEqual(primary["all_tokens_per_percent"], 100)
        self.assertEqual(primary["uncached_tokens_per_percent"], 80)
        self.assertEqual(result["gate_within_10_percent"], "unverified")

    def test_go_reconcile_includes_all_go_harnesses_and_excludes_free(self):
        result = ledger.reconcile(self.conn, "opencode-go", SINCE,
                                  self.home / ".local/state/capacity-watch/readings.jsonl")
        w = result["windows"][0]
        self.assertEqual(w["samples"], 1)  # New reset is not another delta.
        self.assertEqual(w["tokens_all"], 240)  # 120 OMP plus 120 direct.
        self.assertEqual(w["tokens_uncached"], 205)  # Cache reads excluded.
        self.assertEqual(w["percent_delta"], 2)
        self.assertEqual(w["all_tokens_per_percent"], 120)

    def test_single_reading_cannot_reconcile(self):
        result = ledger.reconcile(self.conn, "claude", SINCE,
                                  self.home / ".local/state/capacity-watch/readings.jsonl")
        self.assertEqual(result["status"], "insufficient_samples")
        self.assertEqual(result["candidate_calls"], 0)  # Claude proxy is not Anthropic.

    def test_claude_subagent_file_and_vendor_prefix(self):
        r = self.call("claude", "sub-call-1")
        self.assertEqual(r["session_id"], "claude-session")
        self.assertEqual(r["provider"], "thinkingmachines")
        self.assertEqual(r["route"], "free")
        self.assertEqual(r["outcome"], "ok")

    def test_omp_rate_limit_status_is_429(self):
        r = self.call("omp", "omp-call-3")
        self.assertEqual(r["outcome"], "429")
        self.assertEqual(r["route"], "free")

    def codex_rows(self, observations, tokens_in=100):
        """Insert synthetic Codex calls: (minute, percent, reset jitter seconds)."""
        conn = sqlite3.connect(":memory:")
        self.addCleanup(conn.close)
        conn.executescript(ledger.SCHEMA)
        reset = 1794084000
        for i, (minute, pct, jitter) in enumerate(observations):
            r = ledger.row("codex", "s", str(i), f"2026-11-07T15:{minute:02d}:00Z", "h", "gpt-6.1-sol", "openai")
            ledger.usage(r, [tokens_in, 0, 1000, 0, 0])
            r["route"] = "subscription"
            r["window_snapshot"] = json.dumps({"limit_id": "codex", "plan_type": "plus", "primary": {
                "used_percent": pct, "window_minutes": 300, "resets_at": reset + jitter}})
            conn.execute(f"INSERT INTO calls VALUES ({','.join('?' for _ in ledger.COLUMNS)})",
                         [r[c] for c in ledger.COLUMNS])
        return conn

    def test_codex_stale_snapshots_and_reset_jitter(self):
        # 0 -> 10 -> 40 -> stale 20 -> 50, first reset 7 s early: one 50-point window.
        conn = self.codex_rows([(0, 0, 0), (1, 10, 7), (2, 40, 7), (3, 20, 7), (4, 50, 7)])
        w = ledger.reconcile(conn, "codex", SINCE, self.home / "missing")["windows"][0]
        self.assertEqual(w["percent_delta"], 50)
        self.assertEqual(w["samples"], 3)
        self.assertEqual(w["decreases_skipped"], 1)
        self.assertEqual(len(w["instances"]), 1)
        self.assertEqual(w["tokens_uncached"], 400)  # Calls after the baseline only.
        self.assertEqual(w["tokens_all"], 4400)
        self.assertEqual(w["uncached_tokens_per_percent"], 8)

    def test_expect_gate_arithmetic(self):
        conn = self.codex_rows([(0, 0, 0), (1, 10, 0), (2, 50, 0)])  # 200 tokens, 50 points.
        ok = ledger.reconcile(conn, "codex", SINCE, self.home / "missing", {"primary:300": 4.2})
        self.assertEqual(ok["windows"][0]["gate"]["relative_error"], round(4 / 4.2 - 1, 4))
        self.assertEqual(ok["gate_within_10_percent"], "pass")
        bad = ledger.reconcile(conn, "codex", SINCE, self.home / "missing", {"primary:300": 5})
        self.assertEqual(bad["windows"][0]["gate"]["relative_error"], -0.2)
        self.assertEqual(bad["gate_within_10_percent"], "fail")

    def test_instance_agreement_gate(self):
        conn = self.codex_rows([(0, 0, 0), (1, 10, 0), (2, 20, 0), (3, 0, 18000), (4, 10, 18000), (5, 21, 18000)])
        w = ledger.reconcile(conn, "codex", SINCE, self.home / "missing")["windows"][0]
        self.assertEqual(len(w["instances"]), 2)
        self.assertEqual(w["gate"]["verdict"], "pass")  # 10 and 9.52 per point, both within 3% of 400/41.
        self.assertEqual(w["percent_delta"], 41)

    def test_malformed_json_and_invalid_timestamp_skip(self):
        path = self.home / ".local/state/capacity-watch/calls-direct.jsonl"
        with path.open("a") as f:
            f.write('broken JSON\n{"ts":"bad-date","model":"beam-free"}\n')
        result = ledger.ingest(self.conn, self.home, SINCE, "fixture-host")
        self.assertEqual(result["adapters"]["direct-api"]["malformed_json"], 1)
        self.assertEqual(result["adapters"]["direct-api"]["invalid_timestamps"], 1)

    def test_no_prompt_text_in_ledger(self):
        self.assertNotIn("SYNTHETIC_PRIVATE_TEXT", "\n".join(self.conn.iterdump()))

    def test_cli_override_readonly_report(self):
        path = self.home / "ledger.sqlite"
        with sqlite3.connect(path) as conn:
            self.conn.backup(conn)
        before = path.read_bytes()
        env = {**os.environ, "CAPACITY_LEDGER": str(path)}
        run = subprocess.run([sys.executable, "-I", str(ROOT / "scripts/ledger.py"),
                              "report", "--days", "36500", "--by", "harness"],
                             env=env, text=True, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(sum(r["calls"] for r in json.loads(run.stdout)["rows"]), 13)
        self.assertEqual(before, path.read_bytes())


if __name__ == "__main__":
    unittest.main()
