import unittest
"""Offline routing policy and end-to-end CLI fixtures."""
import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("which_tested", ROOT / "scripts/which_model.py")
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)
AT = "2026-11-07T01:00:00Z"


def candidate(route="opencode-go/able", score=40, free=False, **kwargs):
    return {"route": route, "score": score, "tier": "capable" if score is not None else "unscored",
            "cost_in": 0 if free else 1, "cost_out": 0 if free else 2,
            "have_access": True, "data_sharing": False, **kwargs}


def assessment(pool="opencode-go", used=0.2, projected=0.3, window="weekly"):
    return {"at": AT, "pools": [{"pool": pool, "window": window, "used": used, "projected": projected}]}


def fitted():
    return {"pools": {"opencode-go": {"window_allowance_usd": {"weekly": 30, "rolling": 12},
                                     "models": {"able": {"allowance_per_million_tokens": 1, "basis": "fixture"}}}}}


def rank(models, **kwargs):
    args = dict(task_class="bulk-json-text", catalog={"floor": 27, "models": models}, calls=[], scores={},
                trials={}, fitted=fitted(), calibration={}, assessment=assessment())
    args.update(kwargs)
    return q.rank_models(**args)


@pytest.mark.parametrize("demand,remaining,free,expected", [
    (0, 0.8, False, 0.1), (0.04, 0.8, False, 0.1), (0.4, 0.8, False, 0.5),
    (0.8, 0.1, False, 8), (0, 0, False, None), (1, 0, False, None),
    (None, 0.8, False, None), (100, 0, True, 0), (None, None, True, 0)])
def test_lambda_edges(demand, remaining, free, expected):
    assert q.shadow_price(demand, remaining, free) == expected


def test_forecast_uses_future_demand_not_total_projection():
    w = q.pool_windows(assessment(used=0.4, projected=1.0), "opencode-go")[0]
    assert w["lambda"] == pytest.approx(1)
    assert w["forecast_demand"] == pytest.approx(0.6)


def test_private_endpoint_and_sharing_filters():
    models = [candidate("openrouter/openai/able", free=True),
              candidate("openai/able", free=True),
              candidate("anthropic/able", free=True, data_sharing=True),
              candidate("opencode-go/claude-opus", free=True)]
    result = rank(models, private=True)
    assert [r["route"] for r in result["ranked"]] == ["openai/able"]
    assert all(any("privacy" in why for why in r["reasons"]) for r in result["filtered"])


def test_below_floor_cannot_be_overridden_by_trials_or_subscription():
    model = candidate("opencode-go/able", score=12, subscription=True)
    result = rank([model], trials={"able": {"calls": 10, "valid": 10, "tokens": 1000, "minutes": 1, "allowance": 0.001}})
    assert not result["ranked"]
    assert "quality: below catalog floor" in result["filtered"][0]["reasons"]


def test_unscored_requires_task_and_endpoint_specific_trial():
    trial = {"calls": 19, "valid": 17, "tokens": 10000, "minutes": 1, "allowance": 0}
    models = [candidate("opencode-go/stealth-free", score=None, free=True),
              candidate("opencode/stealth-free", score=None, free=True)]
    result = rank(models, trials={"stealth-free": trial})
    assert [r["route"] for r in result["ranked"]] == [models[0]["route"]]
    assert result["ranked"][0]["p_success"] == pytest.approx(18 / 21)
    assert not rank(models, trials={"stealth-free": trial}, task_class="code-review")["ranked"]


def test_beta_prior_and_trial_failures_are_not_transport_success():
    prior = q.beta_posterior(40)
    assert prior["mean"] == 0.4
    assert prior["alpha"] + prior["beta"] == 4
    posterior = q.beta_posterior(90, 11, 8, trial=True)
    assert posterior["mean"] == 12 / 21


def test_scarcity_reduces_score_and_short_window_exhaustion_filters():
    easy = rank([candidate()])["ranked"][0]
    scarce = rank([candidate()], assessment=assessment(used=0.9, projected=1.5))["ranked"][0]
    assert easy["score"] > scarce["score"]
    state = assessment()
    state["pools"].append({"pool": "opencode-go", "window": "rolling", "used": 1, "projected": 1})
    assert not rank([candidate()], assessment=state)["ranked"]


def test_free_score_has_no_zero_denominator_and_request_caps_apply():
    result = rank([candidate("openrouter/able:free", free=True)])
    r = result["ranked"][0]
    assert r["lambda"] == 0 and r["expected_quota_units"] == 0
    assert r["score"] == pytest.approx(r["p_success"] / (0.01 * r["expected_minutes"]))
    assert r["headroom"] is None
    assert not rank([candidate("openrouter/able:free", free=True)],
                    assessment=assessment(pool="openrouter", used=1, projected=1, window="free_daily"))["ranked"]


def test_go_free_routes_ignore_exhausted_paid_allowance():
    result = rank([candidate("opencode-go/able-free", free=True)],
                  assessment=assessment(used=1, projected=1))
    assert result["ranked"][0]["lambda"] == 0
    assert result["ranked"][0]["headroom"] is None


def test_missing_weight_and_forecast_are_explicit_filters():
    assert "weight" in rank([candidate()], fitted={})["filtered"][0]["reasons"][0]
    assert "forecast" in rank([candidate()], assessment=assessment(projected=None))["filtered"][0]["reasons"][0]


def test_binding_window_normalizes_allowance_and_does_not_sum_prices():
    state = assessment(used=0.8, projected=1.0)
    state["pools"].append({"pool": "opencode-go", "window": "rolling", "used": 0.8, "projected": 1.0})
    r = rank([candidate()], assessment=state)["ranked"][0]
    assert r["binding_window"] == "rolling"
    assert r["expected_quota_units"] == pytest.approx(0.015 / 12)
    assert r["score"] == pytest.approx(r["p_success"] / (0.015 / 12 + 0.02))


def test_429_filter_is_route_specific_and_lookback_bounded():
    rows = [{"ts": "2026-11-07T00:00:00Z", "provider": "opencode-zen", "model": "able-free",
             "route": "free", "harness": "omp", "outcome": "429"} for _ in range(10)]
    rows += [{**rows[0], "ts": "2026-10-01T00:00:00Z", "provider": "opencode-go"}]
    result = rank([candidate("opencode/able-free", free=True), candidate("opencode-go/able-free", free=True)], calls=rows)
    assert [r["route"] for r in result["ranked"]] == ["opencode-go/able-free"]
    assert result["filtered"][0]["rate_limit"]["rate"] == 1


def test_native_subscription_candidates_obey_floor():
    rows = [{"ts": AT, "provider": "anthropic", "model": "claude-lowmodel", "harness": "claude", "route": "unknown"}]
    cs = q.candidates({"floor": 27, "models": []}, rows, {"lowmodel": (10, "")})
    assert cs[0]["tier"] == "below-floor"
    assert cs[0]["endpoint"] == "claude"
    assert not cs[0]["free"]


def test_claude_api_alias_matches_ardf_without_changing_version():
    models = [candidate("claude/claude-opus-5-5"), candidate("claude/claude-opus-4-5")]
    for m in models:
        m.pop("score")
        m.pop("tier")
    cs = q.candidates({"floor": 27, "models": models}, [], {"opus55": (58.94, "Opus 5.5")})
    assert cs[0]["tier"] == "unscored"
    assert cs[1]["score"] == 58.94


def test_private_native_route_uses_shared_claude_weight_and_ardf_beta():
    models = [candidate("claude/claude-opus-5-5", score=58.94)]
    fit = {"pools": {"claude": {"windows": {"seven_day": {"models": {
        "*": {"usable": True, "percent_points_per_million_tokens": 20}}}}}}}
    result = rank(models, private=True, task_class="code-review", fitted=fit,
                  assessment=assessment(pool="claude", window="seven_day", used=0.4, projected=1.0))
    r = result["ranked"][0]
    assert r["expected_quota_units"] == pytest.approx(0.002)
    assert r["p_success"] == pytest.approx(0.5894)
    assert r["score"] == pytest.approx(0.5894 / (0.002 + 0.02))


def test_latest_catalog_ignores_previous_alias(tmp_path):
    for filename, at in (("catalog-a.json", "2026-11-07T00:00:00Z"),
                         ("catalog-b.json", "2026-11-06T00:00:00Z"),
                         ("catalog-previous.json", "2026-11-08T00:00:00Z")):
        (tmp_path / filename).write_text(json.dumps({"generated_at": at}))
    assert q.latest_catalog(tmp_path)[0].name == "catalog-a.json"


def test_trial_loader_counts_failures_deduplicates_and_ignores_text(tmp_path):
    folder = tmp_path / "date" / "main"
    folder.mkdir(parents=True)
    (folder / "summary.json").write_text(json.dumps({"summary": {"able": {}}, "chunks": [0, 1]}))
    ok = {"model": "able", "start": AT, "chunk": 0, "valid": True, "outcome": "ok", "latency_s": 60,
          "text": "DO NOT EXPOSE", "usage": {"opencode": {"allowance": 0.01, "tokens": {"input": 900, "output": 100}}}}
    fail = {"model": "able", "start": AT, "chunk": 1, "outcome": "429", "latency_s": 1, "error": "DO NOT EXPOSE"}
    (folder / "calls.jsonl").write_text("\n".join(json.dumps(r) for r in (ok, fail, ok)))
    result = q.trial_stats(tmp_path)
    assert result["able"]["calls"] == 2 and result["able"]["valid"] == 1
    assert result["able"]["tokens"] == 500
    assert result["able"]["allowance"] == 0.005
    assert "DO NOT EXPOSE" not in json.dumps(result)


def test_isolated_cli_works_on_synthetic_local_state(tmp_path):
    (tmp_path / "catalog").mkdir()
    (tmp_path / "catalog/catalog-2026-11-07.json").write_text(json.dumps({"generated_at": AT, "floor": 27,
                                                                         "models": [candidate()]}))
    (tmp_path / "assessments.jsonl").write_text(json.dumps(assessment()) + "\n")
    (tmp_path / "calibration.json").write_text("{}")
    (tmp_path / "weights.json").write_text(json.dumps(fitted()))
    ardf = tmp_path / "ardf.csv"
    ardf.write_text("identity,name,priors_score\nable,Able,40\n")
    db = tmp_path / "ledger.sqlite"
    with sqlite3.connect(db) as conn:
        conn.executescript(q.weights.ledger.SCHEMA)
    before = db.read_bytes()
    run = subprocess.run([sys.executable, "-I", str(ROOT / "scripts/which_model.py"), "bulk-json-text", "--json",
                          "--state", str(tmp_path), "--ledger", str(db), "--ardf", str(ardf)], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    result = json.loads(run.stdout, parse_constant=lambda s: pytest.fail(s))
    assert result["ranked"][0]["route"] == "opencode-go/able"
    assert db.read_bytes() == before


class LowTierRule(unittest.TestCase):
    def test_low_tier_names_are_filtered(self):
        import importlib.util, os
        spec = importlib.util.spec_from_file_location("wm", os.path.join(os.path.dirname(__file__), "..", "scripts", "which_model.py"))
        wm = importlib.util.module_from_spec(spec); spec.loader.exec_module(wm)
        for name in ("claude-haiku-5-5", "llama-scout-x", "gpt-6-mini"):
            r = wm.filter_reasons({"model": name, "route": "x/" + name, "tier": "capable", "score": 99, "endpoint": "claude", "data_sharing": False, "have_access": True},
                                  27.0, False, None, {"calls": 0, "rate": 0}, 0.1)
            self.assertTrue(any(x.startswith("policy: low-tier") for x in r), name)
        r = wm.filter_reasons({"model": "claude-opus-5-5", "route": "claude/claude-opus-5-5", "tier": "capable", "score": 60, "endpoint": "claude", "data_sharing": False, "have_access": True},
                              27.0, False, None, {"calls": 0, "rate": 0}, 0.1)
        self.assertFalse(any(x.startswith("policy: low-tier") for x in r))
