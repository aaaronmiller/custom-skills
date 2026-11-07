#!/usr/bin/env python3
"""Export the capacity-watch state as CSV datasets for the Quota Ledger dashboard (MP-14).

  python3 -I dashboard-data.py [--out DIR]     (default ~/.local/state/capacity-watch/dashboard)

Reads only local state, writes counts and percentages only (no prompt text, no credentials):
  quota_history.csv   every probe reading per pool and window, plus Codex window snapshots from the ledger
  projections.csv     the latest assessment: used, projected at reset, pace, verdict per pool window
  usage_daily.csv     ledger calls and tokens per day, harness and model
  forecast_hours.csv  hourly quota targets against actual changes (from hour-*/scores.json)
  lane_trial.csv      the lane-trial summaries (validity, latency, allowance per valid chunk)
Each file is under 256 KB by design: usage is aggregated by day, quota history is deduplicated.
"""
import argparse
import csv
import glob
import json
import os
import sqlite3
from pathlib import Path

S = Path.home() / ".local/state/capacity-watch"


def write(path: Path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    return len(rows)


def quota_history(out: Path):
    seen, rows = set(), []
    for line in open(S / "readings.jsonl"):
        line = line.strip()
        if not line.startswith("{"):
            continue
        p = json.loads(line)
        for win, v in (p.get("windows") or {}).items():
            if v.get("used_fraction") is None:
                continue
            ts = (p.get("probed_at") or p.get("observed_at") or "")[:16]
            k = (ts, p["name"], win)
            if k in seen:
                continue
            seen.add(k)
            rows.append([ts, p["name"], win, round(v["used_fraction"] * 100, 1), (v.get("resets_at") or "")[:16], "probe"])
    db = S / "ledger.sqlite"
    if db.exists():
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        last = {}
        for ts, snap in con.execute("select ts, window_snapshot from calls where harness='codex' and window_snapshot is not null order by ts"):
            try:
                s = json.loads(snap)
            except (TypeError, ValueError):
                continue
            for key, win in (("primary", "five_hour"), ("secondary", "weekly")):
                w = s.get(key) or {}
                if w.get("used_percent") is None:
                    continue
                minute = ts[:15] + "0"  # 10-minute buckets keep the file small
                k = (minute, "codex", win)
                if k in seen or last.get(win) == (minute, w["used_percent"]):
                    continue
                seen.add(k)
                last[win] = (minute, w["used_percent"])
                rows.append([minute, "codex", win, w["used_percent"], "", "ledger"])
    rows.sort()
    return write(out / "quota_history.csv", ["ts", "pool", "window", "used_pct", "resets_at", "source"], rows)


def projections(out: Path):
    last = None
    for line in open(S / "assessments.jsonl"):
        if line.strip():
            last = json.loads(line)
    resets = {}  # latest reset time per pool window, from the probe readings
    for line in open(S / "readings.jsonl"):
        line = line.strip()
        if line.startswith("{"):
            r = json.loads(line)
            for win, v in (r.get("windows") or {}).items():
                if v.get("resets_at"):
                    resets[(r["name"], win)] = v["resets_at"][:16]
    rows = []
    for p in (last or {}).get("pools", []):
        if p.get("used") is None:
            continue
        proj = p.get("projected")
        rows.append([last["at"][:16], p["pool"], p["window"], round(p["used"] * 100, 1),
                     min(round(proj * 100, 1), 300) if proj is not None else "",
                     p.get("pace") if p.get("pace") is not None else "", resets.get((p["pool"], p["window"]), ""), p.get("verdict", "")])
    return write(out / "projections.csv", ["assessed_at", "pool", "window", "used_pct", "projected_at_reset_pct", "pace", "resets_at", "verdict"], rows)


def usage_daily(out: Path):
    con = sqlite3.connect(f"file:{S / 'ledger.sqlite'}?mode=ro", uri=True)
    q = """select substr(ts,1,10) day, harness, model, count(*), sum(coalesce(tokens_in,0)), sum(coalesce(tokens_out,0)),
                  sum(coalesce(tokens_cache_read,0)), round(sum(coalesce(list_cost_usd,0)),4), round(sum(coalesce(allowance_usd,0)),4),
                  sum(case when outcome like '%429%' then 1 else 0 end)
           from calls group by 1,2,3 order by 1,2,3"""
    rows = [list(r) for r in con.execute(q)]
    return write(out / "usage_daily.csv", ["day", "harness", "model", "calls", "tokens_in", "tokens_out", "tokens_cache_read",
                                          "list_cost_usd", "allowance_usd", "rate_limited"], rows)


def forecast_hours(out: Path):
    rows = []
    for f in sorted(glob.glob(str(S / "hour*/scores.json"))):
        for r in json.load(open(f)):
            rows.append([r["hour_start"], r["pool"], r["window"], r["baseline_pct"], r["target_delta"], r["actual_delta"], r.get("note", "")])
    return write(out / "forecast_hours.csv", ["hour_start", "pool", "window", "baseline_pct", "target_delta", "actual_delta", "note"], rows)


def lane_trial(out: Path):
    rows = []
    for f in sorted(glob.glob(str(S / "trials/*/*/summary.json"))):
        d = json.load(open(f))
        day = Path(f).parent.parent.name
        for m, s in d["summary"].items():
            rows.append([day, m, s["calls"], s["valid"], s["median_latency_s"], s["allowance_per_valid_chunk"],
                         s["tokens_per_min_per_lane"], s["project_agreement_mean"], sum(v for k, v in s["outcomes"].items() if k != "ok")])
    return write(out / "lane_trial.csv", ["trial_day", "model", "calls", "valid", "median_latency_s", "allowance_per_valid_usd",
                                         "tokens_per_min_per_lane", "project_agreement", "errors"], rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(S / "dashboard"))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    counts = {n: fn(out) for n, fn in [("quota_history", quota_history), ("projections", projections), ("usage_daily", usage_daily),
                                        ("forecast_hours", forecast_hours), ("lane_trial", lane_trial)]}
    sizes = {p.name: p.stat().st_size for p in out.glob("*.csv")}
    print(json.dumps({"out": str(out), "rows": counts, "bytes": sizes}))


if __name__ == "__main__":
    main()
