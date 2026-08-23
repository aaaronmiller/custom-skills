#!/usr/bin/env python3
"""Append site scan row with timestamp. Usage: site_log.py --site URL --hunt N --jobs N --grade S --rationale "..." """
import csv, argparse, datetime, pathlib
ap = argparse.ArgumentParser()
ap.add_argument("--site", required=True); ap.add_argument("--hunt", required=True); ap.add_argument("--jobs", required=True); ap.add_argument("--grade", required=True); ap.add_argument("--rationale", required=True); ap.add_argument("--out", default="hunts/site-log.csv")
args = ap.parse_args()
p = pathlib.Path(args.out); p.parent.mkdir(parents=True, exist_ok=True)
new = not p.exists()
with open(p, "a", newline="") as f:
    w = csv.writer(f)
    if new: w.writerow(["timestamp","site_url","hunt","jobs_reviewed","grade","rationale"])
    w.writerow([datetime.datetime.now().isoformat(), args.site, args.hunt, args.jobs, args.grade, args.rationale])
print(f"Logged {args.site} -> {args.out}")
