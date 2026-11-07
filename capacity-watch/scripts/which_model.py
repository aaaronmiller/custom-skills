#!/usr/bin/env python3
"""which-model: rank local model routes for a task, without dispatch or API calls."""
import re
import argparse
import collections
import datetime as dt
import importlib.util
import json
import math
import os
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("capacity_weights", ROOT / "scripts/weights.py")
weights = importlib.util.module_from_spec(spec)
spec.loader.exec_module(weights)
catalog_module = weights.sibling("free-catalog")

PRIOR_STRENGTH = 4.0
TASK_PRIORS = {"bulk-json-text": (15000, 2.0), "code-review": (10000, 2.0)}


def shadow_price(demand, remaining, free=False):
    """Demand and remaining must share units. None means unknown or exhausted.

    Exhaustion is a hard filter, not a JSON Infinity. Free quota price is zero,
    but a free route can still be unavailable due to a request limit.
    """
    if free:
        return 0.0
    if remaining is None or remaining <= 0 or demand is None:
        return None
    return max(0.1, max(0.0, demand) / remaining)


def beta_posterior(score=None, successes=0, failures=0, trial=False):
    # ARDF is an index, not a task success frequency. The mapping and strength
    # are deliberately weak explicit priors, pending task-tagged validator data.
    if trial or score is None:
        alpha, beta = 1.0, 1.0
        basis = "uniform Beta(1,1)"
    else:
        mean = min(0.95, max(0.05, score / 100))
        alpha, beta = mean * PRIOR_STRENGTH, (1 - mean) * PRIOR_STRENGTH
        basis = "ARDF index / 100, clipped to [0.05,0.95], strength 4 (heuristic prior)"
    alpha += successes
    beta += failures
    return {"alpha": alpha, "beta": beta, "mean": alpha / (alpha + beta),
            "successes": successes, "failures": failures, "prior": basis}


def trial_stats(root):
    """Only completed lane-trial runs count. Never return error or response text.

    Summary files identify these runs; per-call validity is the task gate.
    Evidence stays specific to the Go endpoint and bulk-json-text task class.
    """
    grouped, seen = collections.defaultdict(list), set()
    for path in sorted(root.glob("*/*/summary.json")):
        summary = json.loads(path.read_text())
        if not isinstance(summary.get("summary"), dict) or "chunks" not in summary:
            continue
        for r in weights.json_lines(path.with_name("calls.jsonl")):
            model = r.get("model")
            if model not in summary["summary"]:
                continue
            key = (model, r.get("start"), r.get("chunk"))
            if key in seen:
                continue
            seen.add(key)
            usage = r.get("usage") or {}
            oc = usage.get("opencode") or {}
            tokens = oc.get("tokens") or {}
            count = sum(tokens.get(k) or 0 for k in ("input", "output", "cache_write_5m", "cache_write_1h")) if tokens else None
            grouped[model].append({"valid": r.get("valid") is True and r.get("outcome") == "ok",
                                   "tokens": count, "allowance": oc.get("allowance"),
                                   "seconds": weights.ledger.number(r.get("latency_s")),
                                   "outcome": r.get("outcome")})
    result = {}
    for model, rows in grouped.items():
        # Transport failures with no usage are assumed unbilled. A successful
        # call lacking usage is unknown and cannot yield a measured cost mean.
        usage_complete = all(r["tokens"] is not None or r["outcome"] != "ok" for r in rows)
        allowance_complete = all(r["allowance"] is not None or r["outcome"] != "ok" for r in rows)
        result[model] = {"calls": len(rows), "valid": sum(r["valid"] for r in rows),
                         "tokens": sum(r["tokens"] or 0 for r in rows) / len(rows) if usage_complete else None,
                         "allowance": sum(r["allowance"] or 0 for r in rows) / len(rows) if allowance_complete else None,
                         "minutes": sum(r["seconds"] for r in rows) / len(rows) / 60 if all(r["seconds"] is not None for r in rows) else None}
    return result


def route_for_call(row):
    model = row["model"]
    if row["harness"] == "codex" and row["route"] == "subscription" and row["provider"] in ("openai", "openai-codex"):
        return "codex/" + model
    if row["harness"] == "claude" and row["provider"] == "anthropic" and model.startswith("claude-"):
        return "claude/" + model
    provider = {"opencode-zen": "opencode"}.get(row["provider"], row["provider"])
    # Most aggregators store the vendor/model id, while Groq may repeat itself.
    return model if model.startswith(provider + "/") else provider + "/" + model


def candidates(catalog, calls, scores):
    found = {m["route"]: dict(m) for m in catalog["models"]}
    for r in calls:
        route = route_for_call(r)
        if route.startswith(("codex/", "claude/")) or (r["provider"] == "opencode-go" and r["route"] in ("subscription", "free")):
            found.setdefault(route, {"route": route, "subscription": r["route"] != "free",
                                     "data_sharing": False if route.startswith(("codex/", "claude/")) else bool(catalog_module.SHARING.search(route)),
                                     "have_access": True, "access_basis": "seen in local ledger; not a live authentication check"})
    for c in found.values():
        c["endpoint"], c["model"] = c["route"].split("/", 1)
        if "score" not in c:
            # ARDF names native Claude models Opus/Sonnet/Fable/Haiku, without
            # the API's claude- prefix. Preserve version numbers and exact ids.
            identity = c["model"].removeprefix("claude-")
            c.update(catalog_module.score_for(identity, scores) or {})
        # Exact catalog floor rejection is never overridden by a successful trial.
        c.setdefault("tier", "unscored" if c.get("score") is None else
                     "capable" if c["score"] >= catalog["floor"] else "below-floor")
        c["free"] = (c.get("cost_in") == 0 and c.get("cost_out") == 0) or c["model"].endswith(("-free", ":free"))
        if c["endpoint"] in ("codex", "claude"):
            c["free"] = False
    return sorted(found.values(), key=lambda c: c["route"])


def learned_rates(calls, as_of, days=7):
    end = weights.ledger.epoch(as_of)
    start = end - days * 86400
    grouped = collections.defaultdict(collections.Counter)
    for r in calls:
        timestamp = weights.ledger.epoch(r["ts"])
        if start <= timestamp <= end:
            group = grouped[route_for_call(r)]
            group["calls"] += 1
            group["429"] += r.get("outcome") == "429"
    return {route: {"calls": counts["calls"], "429": counts["429"],
                    "rate": counts["429"] / counts["calls"]}
            for route, counts in grouped.items()}


# Standing operator rule: no low-tier models, whatever their benchmark score.
LOW_TIER = re.compile(r"(?i)(haiku|scout|nano|\bmini\b|-mini|lite\b|tiny)")


def filter_reasons(candidate, floor, private, trial, rate, max_429_rate):
    reasons = []
    if LOW_TIER.search(str(candidate.get("model") or candidate.get("route") or "")):
        reasons.append("policy: low-tier model (operator rule: never use low-tier models)")
    if private and (candidate.get("data_sharing") is not False or
                    candidate["endpoint"] not in ("claude", "codex", "anthropic", "openai", "openai-codex")):
        reasons.append("privacy: requires a non-sharing Anthropic or OpenAI endpoint")
    if candidate["tier"] == "below-floor" or (candidate.get("score") is not None and candidate["score"] < floor):
        reasons.append("quality: below catalog floor")
    elif candidate.get("score") is None:
        # Unscored models get a task-specific admission after a majority-valid
        # lane trial of at least five calls. This is not a general ARDF rating.
        if not trial or trial["calls"] < 5 or trial["valid"] / trial["calls"] < 0.5:
            reasons.append("quality: unscored and no qualifying task-specific trial")
    if candidate.get("have_access") is not True:
        reasons.append("access: catalog does not show this endpoint available")
    if rate["calls"] >= 10 and rate["rate"] >= max_429_rate:
        reasons.append("learned limit: observed 429 rate at or above threshold")
    return reasons


def pool_windows(assessment, pool):
    result = []
    for r in assessment.get("pools", []):
        if r.get("pool") != pool:
            continue
        used = weights.ledger.number(r.get("used"))
        if used is None:
            continue
        # The operator reserve (assess.py) lowers the cap agents may plan against until it is released.
        cap = weights.ledger.number(r.get("cap"))
        remaining = max(0.0, (cap if cap is not None else 1) - used)
        projected = weights.ledger.number(r.get("projected"))
        demand = max(0.0, projected - used) if projected is not None else None
        result.append({"window": r["window"], "headroom": remaining,
                       "forecast_demand": demand, "lambda": shadow_price(demand, remaining)})
    return result


def quota_estimate(candidate, tokens, minutes, trial, fitted, calibration, assessment):
    pool, model = candidate["endpoint"], candidate["model"]
    windows = pool_windows(assessment, pool)
    if candidate["free"]:
        # Go free routes consume no paid allowance. Only request-count windows
        # constrain them, not the paid rolling/weekly/monthly percentages.
        request_windows = [w for w in windows if w["window"] in ("free_daily", "hourly_per_ip", "daily_requests")]
        if any(w["headroom"] <= 0 for w in request_windows):
            return None, "quota: free endpoint request limit exhausted"
        return {"pool": pool, "window": "free", "lambda": 0.0,
                "headroom": min((w["headroom"] for w in request_windows), default=None),
                "expected_quota_units": 0.0, "quota_cost": 0.0,
                "quota_basis": "free; remaining request capacity unknown unless assessed"}, None
    if not windows:
        return None, "quota: no assessed subscription pool (metered spend is not estimated)"
    if any(w["headroom"] <= 0 for w in windows):
        return None, "quota: an assessed window is exhausted"
    if any(w["lambda"] is None for w in windows):
        return None, "quota: forecast demand is unknown"
    pool_fit = fitted.get("pools", {}).get(pool, {})
    priced = []
    for w in windows:
        expected, basis = None, None
        if pool == "opencode-go":
            allowance = trial.get("allowance") if trial else None
            basis = "lane-trial mean allowance per attempt"
            if allowance is None:
                fit = pool_fit.get("models", {}).get(model, {})
                per_m = fit.get("allowance_per_million_tokens")
                if per_m is not None:
                    allowance = per_m * tokens / 1e6
                    basis = fit["basis"]
            size = pool_fit.get("window_allowance_usd", {}).get(w["window"])
            if allowance is not None and size:
                expected = allowance / size
        else:
            fit = pool_fit.get("windows", {}).get(w["window"], {}).get("models", {}).get("*" if pool == "claude" else model, {})
            if fit.get("usable"):
                expected = fit["percent_points_per_million_tokens"] * tokens / 1e6 / 100
                basis = "NNLS uncached-token fit; in-sample, not reconciled"
            else:
                prior = calibration.get("pools", {}).get(pool, {})
                if prior.get("window") == w["window"] and prior.get("per_agent_hour") is not None:
                    expected = prior["per_agent_hour"] * minutes / 60
                    basis = "calibration per-agent-hour prior; model weight unavailable"
        if expected is None or expected <= 0:
            return None, "quota: no positive weight or applicable prior for " + w["window"]
        if expected > w["headroom"]:
            return None, "quota: expected task exceeds remaining " + w["window"]
        priced.append({**w, "pool": pool, "expected_quota_units": expected,
                       "quota_cost": expected * w["lambda"], "quota_basis": basis})
    # Shared quota consumed in multiple windows is not added multiple times.
    # Use the greatest scarcity-weighted fraction and enforce every window.
    binding = max(priced, key=lambda w: w["quota_cost"])
    return {**binding, "windows": priced}, None


def rank_models(task_class, catalog, calls, scores, trials, fitted, calibration, assessment,
                private=False, time_weight=0.01, max_429_rate=0.1):
    rates = learned_rates(calls, assessment["at"])
    ranked, filtered = [], []
    for c in candidates(catalog, calls, scores):
        trial = trials.get(c["model"]) if task_class == "bulk-json-text" and c["endpoint"] == "opencode-go" else None
        rate = rates.get(c["route"], {"calls": 0, "429": 0, "rate": 0.0})
        reasons = filter_reasons(c, catalog["floor"], private, trial, rate, max_429_rate)
        posterior = beta_posterior(c.get("score"), trial["valid"] if trial else 0,
                                   trial["calls"] - trial["valid"] if trial else 0, trial=bool(trial))
        tokens, minutes = TASK_PRIORS.get(task_class, (10000, 2.0))
        token_basis = time_basis = "task-size prior; no task-tagged ledger observations"
        if c["free"]:
            minutes = calibration.get("throughput", {}).get("free_lane_chunk_minutes", {}).get("value", 6.0)
            time_basis = "calibration free-lane time prior; not measured for this route/task"
        if trial:
            if trial.get("tokens") is not None and trial["tokens"] > 0:
                tokens, token_basis = trial["tokens"], "lane-trial mean uncached tokens per attempt"
            if trial.get("minutes") is not None and trial["minutes"] > 0:
                minutes, time_basis = trial["minutes"], "lane-trial mean minutes per attempt, including failures"
        quota, quota_reason = quota_estimate(c, tokens, minutes, trial, fitted, calibration, assessment)
        if quota_reason:
            reasons.append(quota_reason)
        if reasons:
            filtered.append({"route": c["route"], "reasons": reasons, "ardf_score": c.get("score"),
                             "rate_limit": rate})
            continue
        score = posterior["mean"] / (quota["quota_cost"] + time_weight * minutes)
        ranked.append({"route": c["route"], "model": c["model"], "score": score,
                       "lambda": quota["lambda"], "headroom": quota["headroom"],
                       "pool": quota["pool"], "binding_window": quota["window"],
                       "p_success": posterior["mean"], "posterior": posterior,
                       "expected_tokens": tokens, "token_basis": token_basis,
                       "expected_minutes": minutes, "time_basis": time_basis,
                       "expected_quota_units": quota["expected_quota_units"],
                       "quota_basis": quota["quota_basis"], "rate_limit": rate,
                       "window_estimates": quota.get("windows", []),
                       "quality_basis": "catalog/ARDF floor" if c.get("score") is not None else "task-specific lane trial; ARDF unscored"})
    ranked.sort(key=lambda r: (-r["score"], r["route"]))
    return {"task_class": task_class, "private": private, "assessment_at": assessment["at"],
            "floor": catalog["floor"], "time_weight": time_weight,
            "policy": {"429_lookback_days": 7, "429_min_calls": 10, "429_rate_threshold": max_429_rate,
                       "quota_unit": "fraction of binding window, not dollars or percent points",
                       "lambda": "max(0.1, (projected-used)/(1-used)); free=0; all windows enforced",
                       "unscored_admission": "bulk-json-text on Go only: at least 5 trial calls and 50% valid; never overrides below-floor",
                       "selection": "deterministic posterior mean; no dispatch or Thompson sampling"},
            "limitations": ["Assessment-time recommendation, not a live quota or authentication check.",
                            "Forecast demand is projected minus used; assessment projections may be capped at 9.99.",
                            "No task-class or validation table exists in the current ledger. Transport ok is not task success.",
                            "ARDF-to-success mapping, task sizes, time weight and 429 threshold remain priors or policy choices.",
                            "ARDF scores use the best available effort, matching the catalog; the selector does not choose effort.",
                            "Native Claude routing is inferred from its harness, Anthropic provider and model id; the ledger has no endpoint URL or billing proof.",
                            "Lane trials are small first-attempt validity samples, not correctness or agreement scores.",
                            "429 rates describe the observed traffic mix; RPM, TPM and concurrency ceilings cannot be inferred from this ledger.",
                            "Calls failing without usage in trials are assumed unbilled."],
            "ranked": ranked, "filtered": filtered}


def latest_catalog(directory):
    # Exclude catalog-previous.json; choose the newest actual generated snapshot.
    snapshots = []
    for p in directory.glob("catalog-*.json"):
        if p.name == "catalog-previous.json":
            continue
        d = json.loads(p.read_text())
        snapshots.append((weights.ledger.epoch(d["generated_at"]), p.name, p, d))
    if not snapshots:
        raise ValueError("missing catalog")
    _, _, path, data = max(snapshots)
    return path, data


def main():
    ap = argparse.ArgumentParser(prog="which-model", description=__doc__)
    ap.add_argument("task_class")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--private", action="store_true")
    ap.add_argument("--state", type=Path, default=weights.STATE)
    ap.add_argument("--ledger", type=Path)
    ap.add_argument("--ardf", type=Path, default=Path(catalog_module.ARDF_CSV))
    ap.add_argument("--time-weight", type=float, default=0.01)
    ap.add_argument("--max-429-rate", type=float, default=0.1)
    a = ap.parse_args()
    if not math.isfinite(a.time_weight) or a.time_weight <= 0:
        ap.error("--time-weight must be finite and positive")
    if not math.isfinite(a.max_429_rate) or not 0 < a.max_429_rate <= 1:
        ap.error("--max-429-rate must be in (0,1]")
    try:
        cat_path, catalog = latest_catalog(a.state / "catalog")
        assessments = weights.json_lines(a.state / "assessments.jsonl")
        assessment = collections.deque(assessments, maxlen=1)
        if not assessment:
            raise ValueError("missing assessment")
        fitted = json.loads((a.state / "weights.json").read_text())
        calibration = json.loads((a.state / "calibration.json").read_text())
        calls = weights.read_calls(a.ledger or Path(os.environ.get("CAPACITY_LEDGER", a.state / "ledger.sqlite")))
        result = rank_models(a.task_class, catalog, calls, catalog_module.ardf_scores(a.ardf),
                             trial_stats(a.state / "trials"), fitted, calibration, assessment[0],
                             a.private, a.time_weight, a.max_429_rate)
        now = dt.datetime.now(dt.timezone.utc)
        result["generated_at"] = now.isoformat()
        result["assessment_age_hours"] = max(0, (now.timestamp() - weights.ledger.epoch(assessment[0]["at"])) / 3600)
        result["sources"] = {"catalog": str(cat_path), "catalog_generated_at": catalog["generated_at"],
                             "ardf": str(a.ardf), "weights_generated_at": fitted.get("generated_at"),
                             "ledger_latest_at": max((r["ts"] for r in calls), default=None)}
    except (OSError, ValueError, KeyError, TypeError, sqlite3.Error):
        print(json.dumps({"error": "Cannot rank models: check local catalog, ledger, assessment, calibration and weights schemas."}))
        return 1
    if a.json:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    else:
        print(f"{a.task_class}: assessment {result['assessment_at']}; {len(result['ranked'])} ranked")
        for r in result["ranked"]:
            print(f"{r['route']}: score={r['score']:.4f} lambda={r['lambda']:.4f} p_success={r['p_success']:.4f} headroom={r['headroom']}")
        for r in result["filtered"]:
            print(f"filtered {r['route']}: {'; '.join(r['reasons'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
