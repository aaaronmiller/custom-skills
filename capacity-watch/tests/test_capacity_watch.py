"""Regression tests for capacity-watch. Run: python3 -m pytest -q tests/"""
import datetime as dt
import importlib.util
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent / "scripts"


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cat = load("free-catalog")
assess = load("assess")
probe = load("quota-probe")

SCORES = {"kimik3": (17.43, ""), "kimik31": (46.43, ""), "glm53": (31.48, ""),
          "glm53flash": (27.73, ""), "deepseekv41flash1017": (32.59, ""), "musespark13": (36.49, "")}


def test_exact_match_beats_longer_variant():
    assert cat.score_for("opencode-go/kimi-k3", SCORES)["score"] == 17.43


def test_longest_prefix_for_extended_ids():
    assert cat.score_for("opencode-go/kimi-k3.1-pro", SCORES)["ardf_identity"] == "kimik31"
    assert cat.score_for("opencode/glm-5.3-flash-free", SCORES)["ardf_identity"] == "glm53flash"
    assert cat.score_for("opencode-go/glm-5.3", SCORES)["ardf_identity"] == "glm53"


def test_bare_id_takes_shortest_scored_variant():
    assert cat.score_for("opencode/deepseek-v4.1-flash-free", SCORES)["score"] == 32.59


def test_contributor_maps_to_base_model():
    assert cat.score_for("kilo/meta/muse-spark-1.3-contributor", SCORES)["ardf_identity"] == "musespark13"


def test_non_chat_models_are_dropped():
    assert not cat.keep({"route": "groq/whisper-large-v3", "cost_in": 0, "cost_out": 0})
    assert cat.keep({"route": "opencode/big-pickle", "cost_in": 0, "cost_out": 0})


def test_pre_ai_units_are_flagged():
    assert assess.PRE_AI.search("about 3 weeks of work")
    assert not assess.PRE_AI.search("4 agent-hours")


def test_projection_from_average_flags_overrun():
    now = assess.NOW
    row = dict(pool="claude", window="seven_day", used=0.37, length_min=10080,
               reset=now + dt.timedelta(hours=123.5), hist=[], observed=now, source="")
    proj, basis, pace = assess.project(row)
    assert pace > 1.3 and proj > 1.0
    assert assess.verdict(row, proj).startswith("SLOW DOWN")


def test_use_it_verdict_near_reset():
    now = assess.NOW
    row = dict(pool="codex", window="five_hour", used=0.1, length_min=300,
               reset=now + dt.timedelta(hours=1), hist=[], observed=now, source="")
    proj, _, _ = assess.project(row)
    assert assess.verdict(row, proj).startswith("USE IT")


def test_rolled_over_window_reads_zero():
    w = probe.window(0.8, probe.NOW - 10)
    assert w["used_fraction"] == 0.0 and w.get("rolled_over")


def test_observation_row_snaps_to_its_pool_next_reset():
    now = assess.NOW
    reset = now + dt.timedelta(hours=30)
    rows = [dict(pool="codex", window="weekly", used=0.5, reset=reset, length_min=10080,
                 hist=[], observed=now, source=""),
            dict(pool="claude", window="seven_day", used=0.4, reset=now + dt.timedelta(hours=5),
                 length_min=10080, hist=[], observed=now, source="")]
    cal = {"pools": {"codex": {"window": "weekly"}, "claude": {"window": "seven_day"}}}
    soak = {"id": "S", "observation": True, "wall_hours": 168, "pools": {"codex": 0.7, "claude": 0.3}}
    # Ready early: waits for the largest-share pool's reset, not the claude one.
    start, flags = assess.snap_start(soak, rows, cal, now + dt.timedelta(hours=2))
    assert start == reset and not flags
    # A reading one second later than the not_before still counts as that reset.
    start, flags = assess.snap_start(soak, rows, cal, reset + dt.timedelta(seconds=1))
    assert start == reset and not flags
    # Ready after the reset: snaps a whole window later and says so.
    start, flags = assess.snap_start(soak, rows, cal, reset + dt.timedelta(hours=1))
    assert start == reset + dt.timedelta(days=7) and flags and "misses" in flags[0]
    # No pools: not snapped.
    assert assess.snap_start({"id": "T", "observation": True, "pools": {}}, rows, cal, now)[0] == now


def test_schedule_respects_after_and_observation(tmp_path):
    page = tmp_path / "timeline.md"
    work = {"serial_lanes": 1, "tasks": [
        {"id": "A", "remaining_agent_hours": 2, "lanes": 1, "pools": {}, "basis": "x"},
        {"id": "S", "remaining_agent_hours": 0, "wall_hours": 48, "observation": True,
         "after": ["A"], "pools": {}, "basis": "soak"},
        {"id": "B", "remaining_agent_hours": 1, "lanes": 1, "after": ["A"], "pools": {}, "basis": "x"}]}
    page.write_text("x\n```json capacity-workload\n" + json.dumps(work) + "\n```\n")
    cal = tmp_path / "cal.json"
    cal.write_text(json.dumps({"pools": {}}))
    out = tmp_path / "status.md"
    hist = tmp_path / "h.jsonl"
    r = subprocess.run([sys.executable, "-I", str(HERE / "assess.py"), "--readings", str(tmp_path / "none"),
                        "--timeline", str(page), "--calibration", str(cal), "--page", str(out),
                        "--history", str(hist)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    done = dt.datetime.fromisoformat(json.loads(hist.read_text())["all_unblocked_done_by"].replace("Z", "+00:00"))
    # The soak starts after A (2 h) and runs 48 h without blocking B.
    assert 49.5 <= (done - assess.NOW).total_seconds() / 3600 <= 50.5
