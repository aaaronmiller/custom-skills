"""Synthetic quota recovery and safe local IO tests. No provider calls."""
import importlib.util
import json
from pathlib import Path
import sqlite3

import pytest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("weights_tested", ROOT / "scripts/weights.py")
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)


def call(minute, model="a", tokens=0, pct=None, reset="2026-11-07T05:00:00Z", pool="codex"):
    snap = {"limit_id": "codex", "primary": {"used_percent": pct, "resets_at": reset, "window_minutes": 300}}
    return {"ts": f"2026-11-07T00:{minute:02d}:00.000000Z", "harness": pool,
            "provider": "openai" if pool == "codex" else "anthropic", "route": "subscription",
            "model": model, "tokens_in": tokens, "tokens_out": 0, "tokens_cache_write": 0,
            "tokens_cache_read": 10000000, "window_snapshot": json.dumps(snap)}


def test_nnls_recovers_known_weights_with_mixed_exposures():
    x = [[1, 0], [0, 2], [1, 3], [4, 2], [0.1, 0.2]]
    y = [sum(a * b for a, b in zip(row, [12, 40])) for row in x]
    fitted, solver = w.nnls(x, y)
    assert solver["converged"]
    assert fitted == pytest.approx([12, 40], rel=1e-7)


def test_nnls_clamps_negative_unconstrained_solution_and_scales_columns():
    fitted, solver = w.nnls([[1, 0], [0, 1e-8], [1, 1e-8]], [-1, 2, 1])
    assert fitted[0] == 0
    assert fitted[1] == pytest.approx(1.5e8)
    assert solver["converged"]


def test_intervals_recover_known_model_weights():
    rows = [call(0, tokens=999999, pct=0), call(1, tokens=100000, pct=2),
            call(2, model="b", tokens=100000, pct=7), call(3, tokens=200000, pct=11),
            call(4, model="b", tokens=200000, pct=21)]
    fitted = w.fit_window(w.interval_samples(rows, "codex")["five_hour"])
    assert fitted["models"]["a"]["percent_points_per_million_tokens"] == pytest.approx(20)
    assert fitted["models"]["b"]["percent_points_per_million_tokens"] == pytest.approx(50)
    assert fitted["models"]["a"]["samples"] == 2
    assert fitted["fit_rmse_percent_points"] < 1e-8


def test_plateaus_jitter_stale_and_saturation_do_not_double_count():
    rows = [call(0, tokens=900000, pct=10), call(1, tokens=20000, pct=10),
            call(2, model="b", tokens=30000, pct=9),
            call(3, tokens=50000, pct=12, reset="2026-11-07T05:00:07Z"),
            call(4, tokens=50000, pct=100), call(5, tokens=50000, pct=100)]
    data = w.interval_samples(rows, "codex")["five_hour"]
    assert data["decreases_skipped"] == 1
    assert data["saturated_skipped"] == 1
    assert len(data["samples"]) == 1
    assert data["samples"][0]["tokens_million"] == {"a": 0.07, "b": 0.03}
    assert data["samples"][0]["delta"] == 2


def test_reset_boundary_and_non_codex_limit_are_excluded():
    rows = [call(0, pct=10), call(1, tokens=100000, pct=12),
            call(2, tokens=900000, pct=0, reset="2026-11-07T05:30:00Z"),
            call(3, tokens=100000, pct=2, reset="2026-11-07T05:30:00Z")]
    unrelated = call(4, tokens=0, pct=80)
    snap = json.loads(unrelated["window_snapshot"])
    snap["limit_id"] = "other"
    unrelated["window_snapshot"] = json.dumps(snap)
    data = w.interval_samples(rows + [unrelated], "codex")["five_hour"]
    assert len(data["samples"]) == 2
    assert sum(s["delta"] for s in data["samples"]) == 4


def test_collinear_models_are_marked_unidentifiable():
    fit = w.fit_window({"samples": [{"tokens_million": {"a": 1, "b": 2}, "delta": 10, "reset": "x"},
                                    {"tokens_million": {"a": 2, "b": 4}, "delta": 20, "reset": "x"}]})
    assert fit["rank"] == 1
    assert all(not model["usable"] for model in fit["models"].values())
    assert w.fit_window({"samples": []})["models"] == {}


def test_claude_uses_one_coefficient_across_models():
    rows = [call(1, "opus", 100000, pool="claude"), call(2, "sonnet", 200000, pool="claude")]
    readings = [{"name": "claude", "status": "ok", "observed_at": f"2026-11-07T00:0{minute}:00Z",
                 "windows": {"seven_day": {"resets_at": "2026-11-12T00:00:00Z", "used_fraction": used}}}
                for minute, used in ((0, 0.1), (3, 0.16))]
    fit = w.fit_window(w.interval_samples(rows, "claude", readings)["seven_day"])
    assert list(fit["models"]) == ["*"]
    assert fit["models"]["*"]["percent_points_per_million_tokens"] == pytest.approx(20)


def test_go_formula_and_unknown_limits_remain_distinct():
    limits = json.loads((ROOT / "references/opencode-go-limits.json").read_text())
    row = {"provider": "opencode-go", "route": "subscription", "model": "deepseek-v4.1-flash",
           "tokens_in": 1000000, "list_cost_usd": 2, "allowance_usd": 1.2}
    unknown = {**row, "model": "new-model", "list_cost_usd": None, "allowance_usd": 2}
    result = w.go_weights([row, unknown], limits)["models"]
    assert result[row["model"]]["allowance_per_list_cost"] == 0.6
    assert result[row["model"]]["formula_rmse_allowance"] == 0
    assert result["gemini-4-argon"]["allowance_per_list_cost"] == 2
    assert result["new-model"]["allowance_per_list_cost"] is None
    assert result["new-model"]["allowance_per_million_tokens"] == 2
    assert result["new-model"]["observed_allowance_samples"] == 1
    assert result["new-model"]["inferred_from_list_cost_samples"] == 0
    assert result["crouton-alpha-free"]["allowance_per_million_tokens"] == 0


def test_missing_ledger_is_not_created_and_existing_is_read_only(tmp_path):
    db = tmp_path / "ledger.sqlite"
    with pytest.raises(sqlite3.OperationalError):
        w.read_calls(db)
    assert not db.exists()
    with sqlite3.connect(db) as conn:
        conn.executescript(w.ledger.SCHEMA)
    before = db.read_bytes()
    assert w.read_calls(db) == []
    assert db.read_bytes() == before


def test_atomic_json_replaces_complete_document(tmp_path):
    out = tmp_path / "weights.json"
    out.write_text('{"old":true}')
    w.atomic_json(out, {"pools": {}})
    assert json.loads(out.read_text()) == {"pools": {}}
