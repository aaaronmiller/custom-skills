#!/usr/bin/env python3
"""assess: turn quota readings and the workload block into a capacity status page.

Inputs
  --readings JSONL   history written by quota-probe.py --record
  --timeline PAGE    Living Documents page holding one fenced block that
                     starts with ```json capacity-workload (see SKILL.md)
  --calibration JSON per-pool cost of one agent-hour, as a fraction of each
                     window; the twice-daily meta-review owns this file
Outputs
  --page PAGE        the status page, rewritten whole (Living Documents report)
  --history JSONL    one summary line appended per run

Every number on the page carries its basis: a measured reading, a projection
from readings, or a calibration prior. Nothing here calls a model.
"""
import argparse
import datetime as dt
import json
import os
import re
from zoneinfo import ZoneInfo

PT = ZoneInfo("America/Los_Angeles")
NOW = dt.datetime.now(dt.timezone.utc)

# Window lengths in minutes, when the provider does not report one.
WINDOW_MIN = {"five_hour": 300, "seven_day": 10080, "seven_day_opus": 10080,
              "seven_day_sonnet": 10080, "weekly": 10080, "rolling": 300,
              "monthly": 43200, "daily": 1440}
# Units that mark a pre-AI estimate (see references/estimation-rules.md).
PRE_AI = re.compile(r"\b(\d+(\.\d+)?\s*(weeks?|months?|sprints?|days?|business days?))\b", re.I)
SINGLE_TASK_MAX_AGENT_HOURS = 8


def ts(s):
    if not s:
        return None
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def pt(d):
    return d.astimezone(PT).strftime("%a %m-%d %H:%M") if d else "-"


def hours(td):
    return td.total_seconds() / 3600


def load_readings(path):
    rows = []
    try:
        with open(path) as fh:
            for line in fh:
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    continue
    except OSError:
        pass
    return rows


def load_workload(page):
    with open(page) as fh:
        text = fh.read()
    m = re.search(r"```json capacity-workload\n(.*?)\n```", text, re.S)
    if not m:
        raise SystemExit(f"no ```json capacity-workload block in {page}")
    return json.loads(m.group(1))


def pool_rows(readings):
    """Latest reading per provider, plus same-window history for the slope."""
    latest = {}
    for r in readings:
        if r.get("status") == "unknown":
            continue
        latest[r["name"]] = r
    out = []
    for name, r in sorted(latest.items()):
        for wname, w in (r.get("windows") or {}).items():
            if w.get("used_fraction") is None:
                continue
            reset = ts(w.get("resets_at"))
            length = w.get("window_minutes") or WINDOW_MIN.get(wname)
            hist = [(ts(x["probed_at"]), x["windows"][wname]["used_fraction"])
                    for x in readings
                    if x.get("name") == name and x.get("probed_at")
                    and wname in (x.get("windows") or {})
                    and x["windows"][wname].get("resets_at") == w.get("resets_at")
                    and x["windows"][wname].get("used_fraction") is not None]
            hist = [h for h in hist if h[0] and NOW - h[0] <= dt.timedelta(hours=6)]
            out.append(dict(pool=name, window=wname, used=w["used_fraction"], reset=reset,
                            length_min=length, hist=hist, observed=ts(r.get("observed_at")),
                            source=r.get("source", "")))
    return out


def project(row):
    """Projected use at reset, its basis, and the pace against even burn."""
    u, reset, L = row["used"], row["reset"], row["length_min"]
    if not reset:
        return None, "no reset time", None
    left_h = max(hours(reset - NOW), 0)
    pace = None
    if L:
        elapsed_h = L / 60 - left_h
        if elapsed_h > 0.25:
            pace = round(u / (elapsed_h / (L / 60)), 2) if u else 0.0
    rate, basis = None, None
    h = sorted(row["hist"])
    if len(h) >= 2 and hours(h[-1][0] - h[0][0]) >= 0.5:
        rate = (h[-1][1] - h[0][1]) / hours(h[-1][0] - h[0][0])
        basis = f"slope of {len(h)} readings over {hours(h[-1][0] - h[0][0]):.1f} h"
    elif L and pace is not None:
        elapsed_h = L / 60 - left_h
        rate = u / elapsed_h if elapsed_h > 0 else 0
        basis = "average since the window opened"
    if rate is None:
        return None, "one reading; no rate yet", pace
    return round(min(u + max(rate, 0) * left_h, 9.99), 3), basis, pace


def verdict(row, proj):
    left_h = hours(row["reset"] - NOW) if row["reset"] else None
    if row["used"] >= 0.98:
        return "EXHAUSTED"
    if proj is None:
        return "watch"
    if proj >= 1.0:
        return "SLOW DOWN: runs out before reset"
    if left_h is not None and left_h <= 2 and 1 - row["used"] >= 0.4:
        return "USE IT: resets soon with headroom"
    if proj < 0.6:
        return "under-used: shift work here"
    return "on pace"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--readings", required=True)
    ap.add_argument("--timeline", required=True)
    ap.add_argument("--calibration", required=True)
    ap.add_argument("--page", required=True)
    ap.add_argument("--history", required=True)
    a = ap.parse_args()

    readings = load_readings(os.path.expanduser(a.readings))
    work = load_workload(a.timeline)
    with open(a.calibration) as fh:
        cal = json.load(fh)
    rows = pool_rows(readings)

    # Pools: keep the binding windows only (agy reports one per model; show the worst three).
    agy = sorted([r for r in rows if r["pool"] == "agy"], key=lambda r: -r["used"])[:3]
    rows = [r for r in rows if r["pool"] != "agy"] + agy

    lines, summary = [], {"at": NOW.strftime("%Y-%m-%dT%H:%M:%SZ"), "pools": [], "flags": []}
    lines.append("| Pool | Window | Used | Resets (PT) | Pace | Projected at reset | Basis | Verdict |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for r in rows:
        proj, basis, pace = project(r)
        v = verdict(r, proj)
        age = f", reading {int(hours(NOW - r['observed']) * 60)} min old" if r["observed"] else ""
        lines.append(f"| {r['pool']} | {r['window']} | {r['used']:.0%} | {pt(r['reset'])} | "
                     f"{'-' if pace is None else f'{pace}x'} | "
                     f"{'-' if proj is None else f'{proj:.0%}'} | {basis}{age} | {v} |")
        summary["pools"].append({"pool": r["pool"], "window": r["window"], "used": r["used"],
                                 "projected": proj, "pace": pace, "verdict": v})

    # Demand against headroom, per pool, using calibration priors.
    tasks = [t for t in work.get("tasks", []) if t.get("status") not in ("done", "dropped")]
    demand = {}
    for t in tasks:
        if t.get("blocked_on"):
            continue
        for pool, share in (t.get("pools") or {}).items():
            demand[pool] = demand.get(pool, 0) + float(t.get("remaining_agent_hours", 0)) * share
    dem_lines = ["| Pool | Agent-hours queued | Cost per agent-hour (prior) | Window cost | Headroom now | Fits? |",
                 "|---|---|---|---|---|---|"]
    for pool, ah in sorted(demand.items(), key=lambda kv: -kv[1]):
        c = cal.get("pools", {}).get(pool)
        if not c:
            dem_lines.append(f"| {pool} | {ah:.1f} | no prior | - | - | unknown |")
            continue
        win, per = c["window"], c["per_agent_hour"]
        cur = next((r for r in rows if r["pool"] == pool and r["window"] == win), None)
        head = 1 - cur["used"] if cur else None
        cost = ah * per
        fits = "-" if head is None else ("yes" if cost <= head else f"NO: short by {cost - head:.0%}")
        if head is not None and cost > head:
            summary["flags"].append(f"demand on {pool} {win} exceeds headroom")
        dem_lines.append(f"| {pool} | {ah:.1f} | {per:.1%} of {win} ({c.get('confidence', 'prior')}) | "
                         f"{cost:.0%} | {'-' if head is None else f'{head:.0%}'} | {fits} |")

    # Timeline: open, unblocked tasks in order, each on its own lanes.
    tl = ["| Task | Remaining agent-hours | Lanes | Wall hours | Starts (PT) | Done by (PT) | Basis | Flags |",
          "|---|---|---|---|---|---|---|---|"]
    clock = NOW
    serial = work.get("serial_lanes", 1)
    track = [NOW] * max(1, serial)
    ends = {}
    for t in tasks:
        flags = []
        text = json.dumps(t)
        if PRE_AI.search(text) and not t.get("observation"):
            flags.append("pre-AI units")
        if float(t.get("remaining_agent_hours", 0)) > SINGLE_TASK_MAX_AGENT_HOURS and not t.get("decomposed"):
            flags.append(f"over {SINGLE_TASK_MAX_AGENT_HOURS} agent-hours, not decomposed")
        if not t.get("basis"):
            flags.append("no basis")
        if flags:
            summary["flags"].append(f"{t['id']}: {', '.join(flags)}")
        if t.get("blocked_on"):
            tl.append(f"| {t['id']} {t.get('title', '')} | {t.get('remaining_agent_hours')} | - | - | "
                      f"blocked: {t['blocked_on']} | - | {t.get('basis', '')} | {', '.join(flags)} |")
            continue
        lanes = max(1, int(t.get("lanes", 1)))
        wall = float(t.get("wall_hours") or float(t.get("remaining_agent_hours", 0)) / lanes)
        deps = [ends[d] for d in t.get("after", []) if d in ends]
        if any(d not in ends for d in t.get("after", [])):
            summary["flags"].append(f"{t['id']}: depends on an unscheduled task {t.get('after')}")
        earliest = max([NOW, ts(t.get("not_before")) or NOW] + deps)
        if t.get("observation"):
            # A soak or unattended window: it occupies no work track.
            start = earliest
        else:
            i = min(range(len(track)), key=lambda k: track[k])
            start = max(track[i], earliest)
        end = start + dt.timedelta(hours=wall)
        if not t.get("observation"):
            track[i] = end
        ends[t["id"]] = end
        clock = max(clock, end)
        tl.append(f"| {t['id']} {t.get('title', '')} | {t.get('remaining_agent_hours')} | {lanes} | "
                  f"{wall:.1f} | {pt(start)} | {pt(end)} | {t.get('basis', '')} | {', '.join(flags)} |")
    summary["all_unblocked_done_by"] = clock.strftime("%Y-%m-%dT%H:%M:%SZ")

    page = f"""---
id: capacity-status
title: Capacity status
type: report
order: 7
status: active
parent: index
related: [capacity-watch-method, timeline]
updated: {NOW.astimezone(PT):%Y-%m-%d}
sources: capacity-watch assess.py over quota-probe readings, the timeline workload block and calibration.json
generated-by: capacity-watch assess.py (rewritten every run; edit timeline.md or calibration.json instead)
---

# Capacity status

## Why read this now (30s)

Job: see which quota pools have room, which will run out, and when the open masterplan work lands. Trigger: choosing where the next agent runs, or checking the timeline. Stop: after the verdict column and the done-by line.

Generated {pt(NOW)} PT. Every unblocked task lands by **{pt(clock)} PT** at the lanes listed.

## Pools

{chr(10).join(lines)}

Pace is use divided by the share of the window already gone: 1.0x burns the window exactly at reset, above 1.0x runs out early.

## Demand against headroom

{chr(10).join(dem_lines)}

Costs per agent-hour are priors from calibration.json until the meta-review fits them to measured readings.

## Timeline

{chr(10).join(tl)}

## Flags

{chr(10).join('- ' + f for f in summary['flags']) or 'None.'}
"""
    os.makedirs(os.path.dirname(a.page), exist_ok=True)
    tmp = a.page + ".tmp"
    with open(tmp, "w") as fh:
        fh.write(page)
    os.replace(tmp, a.page)
    os.makedirs(os.path.dirname(os.path.expanduser(a.history)), exist_ok=True)
    with open(os.path.expanduser(a.history), "a") as fh:
        fh.write(json.dumps(summary) + "\n")
    print(json.dumps({"page": a.page, "pools": len(summary["pools"]), "flags": len(summary["flags"]),
                      "done_by": summary["all_unblocked_done_by"]}))


if __name__ == "__main__":
    main()
