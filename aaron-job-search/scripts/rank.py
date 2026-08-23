#!/usr/bin/env python3
"""Composite scoring: Likelihood×1.5 + Income×1.3 + Growth+Stability+Flex+Leverage. Usage: rank.py --input jobs.json --output ranked.json"""
import json, argparse, sys
ap = argparse.ArgumentParser()
ap.add_argument("--input", required=True)
ap.add_argument("--output", required=True)
args = ap.parse_args()
data = json.loads(open(args.input).read())
for j in data:
    L=j.get("likelihood",5); I=j.get("income_score",5); G=j.get("growth",5); S=j.get("stability",5); F=j.get("flexibility",5); V=j.get("leverage",5)
    j["composite"] = round(L*1.5 + I*1.3 + G + S + F + V, 2)
data.sort(key=lambda x: (-x["composite"], -x.get("likelihood",0)))
open(args.output,"w").write(json.dumps(data,indent=2))
print(f"Ranked {len(data)} jobs -> {args.output}")
