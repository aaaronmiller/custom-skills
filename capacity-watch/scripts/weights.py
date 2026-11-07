#!/usr/bin/env python3
"""Fit local quota weights, without network access or ledger mutations (stdlib only)."""
import argparse
import bisect
import collections
import datetime as dt
import importlib.util
import json
import math
import os
from pathlib import Path
import sqlite3
import tempfile

STATE = Path.home() / ".local/state/capacity-watch"
ROOT = Path(__file__).resolve().parent.parent


def sibling(name):
    # Explicit paths also work under python -I, without changing sys.path.
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), ROOT / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ledger = sibling("ledger")


def json_lines(path):
    if not path.exists():
        return
    with path.open() as stream:
        for line in stream:
            try:
                value = json.loads(line)
            except ValueError:
                continue
            if isinstance(value, dict):
                yield value


def read_calls(path):
    """Select only numeric usage and routing metadata, never session or prompt content."""
    columns = ("ts,provider,model,harness,route,tokens_in,tokens_out,tokens_cache_read,"
               "tokens_cache_write,list_cost_usd,allowance_usd,latency_s,outcome,window_snapshot")
    conn = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        conn.row_factory = sqlite3.Row
        return [dict(r) for r in conn.execute(f"SELECT {columns} FROM calls ORDER BY ts")]
    finally:
        conn.close()


def uncached(row):
    return sum(row.get(k) or 0 for k in ("tokens_in", "tokens_out", "tokens_cache_write"))


def nnls(matrix, targets, tolerance=1e-10, max_iterations=20000):
    """Cyclic exact coordinate descent on ||Xw-y|| squared, constrained w >= 0.

    Scale columns to unit norm. This avoids stopping too soon when model token
    totals differ greatly. Return convergence diagnostics, not just coefficients.
    """
    if not matrix:
        return [], {"converged": True, "iterations": 0, "kkt_error": 0.0}
    n = len(matrix[0])
    scales = [math.sqrt(sum(row[j] ** 2 for row in matrix)) for j in range(n)]
    cols = [[row[j] / scales[j] if scales[j] else 0.0 for row in matrix] for j in range(n)]
    weights, residual = [0.0] * n, list(targets)
    converged, kkt = False, 0.0
    for iteration in range(1, max_iterations + 1):
        for j, col in enumerate(cols):
            if not scales[j]:
                continue
            new = max(0.0, weights[j] + sum(x * r for x, r in zip(col, residual)))
            change = new - weights[j]
            weights[j] = new
            for i, x in enumerate(col):
                residual[i] -= x * change
        gradients = [sum(x * r for x, r in zip(col, residual)) for col in cols]
        kkt = max((abs(g) if w > 0 else max(g, 0) for w, g in zip(weights, gradients)), default=0.0)
        if kkt <= tolerance * max(1.0, math.sqrt(sum(y * y for y in targets))):
            converged = True
            break
    return [w / scale if scale else 0.0 for w, scale in zip(weights, scales)], {
        "converged": converged, "iterations": iteration, "kkt_error": kkt}


def matrix_rank(matrix):
    if not matrix:
        return 0
    # Normalize columns before elimination, so small token exposures still count.
    scales = [max(abs(row[j]) for row in matrix) for j in range(len(matrix[0]))]
    a = [[x / s if s else 0.0 for x, s in zip(row, scales)] for row in matrix]
    rank = 0
    for j in range(len(scales)):
        pivot = max(range(rank, len(a)), key=lambda i: abs(a[i][j]), default=None)
        if pivot is None or abs(a[pivot][j]) < 1e-9:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        divisor = a[rank][j]
        a[rank] = [x / divisor for x in a[rank]]
        for i in range(rank + 1, len(a)):
            factor = a[i][j]
            a[i] = [x - factor * y for x, y in zip(a[i], a[rank])]
        rank += 1
    return rank


def interval_samples(rows, pool, readings=()):
    """Retain monotone anchors, accumulate plateaus, sum calls in (start, end].

    Reset times are clustered within 900 seconds of the first reset in a group,
    not by chaining jitter indefinitely. A 100% endpoint is censored and omitted.
    Decreasing Codex observations do not move the high-water anchor.
    """
    rows = sorted((r for r in rows if ledger.in_pool(r, pool)), key=lambda r: r["ts"])
    points = collections.defaultdict(dict)
    for r in rows if pool == "codex" else readings:
        if pool == "codex":
            try:
                snap = json.loads(r.get("window_snapshot") or "{}")
            except ValueError:
                continue
            if not isinstance(snap, dict) or snap.get("limit_id") not in (None, "codex"):
                continue
            t = ledger.timestamp(r["ts"])
            windows = snap
        else:
            if r.get("name") != pool or r.get("status") != "ok":
                continue
            t = ledger.timestamp(r.get("observed_at") or r.get("probed_at"))
            windows = r.get("windows") or {}
        if not t:
            continue
        for name, w in windows.items():
            if not isinstance(w, dict) or w.get("rolled_over"):
                continue
            reset = ledger.timestamp(w.get("resets_at"))
            value = ledger.number(w.get("used_percent" if pool == "codex" else "used_fraction"))
            if value is None:
                continue
            pct = value if pool == "codex" else value * 100
            if reset and reset > t and 0 <= pct <= 100:
                key = (name, w.get("window_minutes"), reset)
                points[key][t] = max(pct, points[key].get(t, 0))
    models = sorted({r["model"] for r in rows}) if pool == "codex" else ["*"]
    times = [ledger.timestamp(r["ts"]) for r in rows]
    prefixes = {m: [0] for m in models}
    for r in rows:
        for m in models:
            prefixes[m].append(prefixes[m][-1] + (uncached(r) if m == "*" or r["model"] == m else 0))
    result = {}
    for name, minutes, reset, observations in ledger.window_instances(points):
        label = {"primary": "five_hour", "secondary": "weekly"}.get(name, name)
        item = result.setdefault(label, {"samples": [], "decreases_skipped": 0,
                                         "saturated_skipped": 0, "no_tokens_skipped": 0})
        anchor = None
        for t, pct in sorted(observations.items()):
            if anchor is None:
                anchor = (t, pct)
                continue
            if pct < anchor[1]:
                item["decreases_skipped"] += 1
                if pool != "codex":
                    anchor = (t, pct)
                continue
            if pct == anchor[1]:
                continue
            a, b = bisect.bisect_right(times, anchor[0]), bisect.bisect_right(times, t)
            tokens = {m: (prefixes[m][b] - prefixes[m][a]) / 1e6 for m in models}
            if pct >= 100:
                item["saturated_skipped"] += 1
            elif not sum(tokens.values()):
                item["no_tokens_skipped"] += 1
            else:
                item["samples"].append({"tokens_million": tokens, "delta": pct - anchor[1],
                                        "reset": reset})
            anchor = (t, pct)
    return result


def fit_window(data):
    samples = data["samples"]
    models = sorted({m for s in samples for m, x in s["tokens_million"].items() if x > 0})
    x = [[s["tokens_million"].get(m, 0) for m in models] for s in samples]
    y = [s["delta"] for s in samples]
    w, solver = nnls(x, y)
    rank = matrix_rank(x)
    residuals = [sum(a * b for a, b in zip(row, w)) - target for row, target in zip(x, y)]
    fitted = {}
    for j, model in enumerate(models):
        indices = [i for i, row in enumerate(x) if row[j] > 0]
        without = [[v for k, v in enumerate(row) if k != j] for row in x]
        identifiable = rank > matrix_rank(without)
        fitted[model] = {
            "percent_points_per_million_tokens": w[j],
            "samples": len(indices),
            "window_instances": len({samples[i]["reset"] for i in indices}),
            "fit_rmse_percent_points": math.sqrt(sum(residuals[i] ** 2 for i in indices) / len(indices)),
            "identifiable": identifiable,
            "usable": identifiable and solver["converged"] and w[j] > 0,
        }
    return {**{k: v for k, v in data.items() if k != "samples"}, "samples": len(samples),
            "rank": rank, "solver": solver, "models": fitted,
            "fit_rmse_percent_points": math.sqrt(sum(r * r for r in residuals) / len(y)) if y else None,
            "relative_l2_error": math.sqrt(sum(r * r for r in residuals) / sum(t * t for t in y)) if y else None}


def go_weights(rows, limits):
    grouped = collections.defaultdict(list)
    for row in rows:
        if row["provider"] == "opencode-go" and row["route"] in ("subscription", "free"):
            grouped[row["model"]].append(row)
    result = {}
    for model in sorted(set(grouped) | set(limits["models"])):
        spec = limits["models"].get(model, {})
        multiplier = (0.0 if spec.get("free") else
                      limits["allowance_pool_usd"] / spec["monthly_limit_usd"]
                      if spec.get("monthly_limit_usd") else None)
        calls = grouped[model]
        paired = [r for r in calls if r.get("list_cost_usd") is not None and r.get("allowance_usd") is not None]
        numeric = []
        observed_samples, inferred_samples = 0, 0
        for r in calls:
            amount = r.get("allowance_usd")
            observed = amount is not None
            if amount is None and multiplier is not None and r.get("list_cost_usd") is not None:
                amount = r["list_cost_usd"] * multiplier
            if amount is not None and uncached(r) > 0:
                numeric.append((uncached(r) / 1e6, amount))
                observed_samples += observed
                inferred_samples += not observed
        weight = sum(y for x, y in numeric) / sum(x for x, y in numeric) if numeric else None
        basis = "ledger allowance per uncached token, observed mix"
        if spec.get("free"):
            weight, basis = 0.0, "plan table: free"
        elif weight is None and multiplier is not None:
            weight = multiplier * (0.75 * spec["input_per_million"] + 0.25 * spec["output_per_million"])
            basis = "prior: plan prices, 3 input tokens per output, no caching"
        result[model] = {
            "allowance_per_list_cost": multiplier,
            "allowance_per_million_tokens": weight,
            "samples": len(numeric), "basis": basis,
            "observed_allowance_samples": observed_samples,
            "inferred_from_list_cost_samples": inferred_samples,
            "fit_rmse_allowance": math.sqrt(sum((weight * x - y) ** 2 for x, y in numeric) / len(numeric)) if numeric else None,
            "formula_check_samples": len(paired) if multiplier is not None else 0,
            "formula_rmse_allowance": math.sqrt(sum((r["list_cost_usd"] * multiplier - r["allowance_usd"]) ** 2 for r in paired) / len(paired)) if paired and multiplier is not None else None,
        }
    return {"window_allowance_usd": limits["window_allowance_usd"], "models": result}


def build_weights(rows, readings, limits):
    return {
        "schema_version": 1,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "ledger_calls": len(rows),
        "ledger_latest_at": max((r["ts"] for r in rows), default=None),
        "token_basis": "input + output + cache writes; cache reads excluded; reasoning already in output",
        "limits": ["Local ledger only; account-wide usage and effort differences can confound the fit.",
                   "Per-model RMSE is the whole-interval residual on samples containing that model, not causal attribution.",
                   "Fit errors are in-sample, not a passed reconciliation or a held-out validation.",
                   "Claude native billing is inferred and one shared coefficient is fitted per window."],
        "pools": {
            pool: {"windows": {name: fit_window(data) for name, data in interval_samples(rows, pool, readings).items()}}
            for pool in ("codex", "claude")
        } | {"opencode-go": go_weights(rows, limits)},
    }


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, prefix=path.name + ".", delete=False) as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
        temp = stream.name
    os.replace(temp, path)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--state", type=Path, default=STATE)
    ap.add_argument("--ledger", type=Path)
    ap.add_argument("--limits", type=Path, default=ROOT / "references/opencode-go-limits.json")
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    try:
        rows = read_calls(a.ledger or Path(os.environ.get("CAPACITY_LEDGER", a.state / "ledger.sqlite")))
        result = build_weights(rows, list(json_lines(a.state / "readings.jsonl")), json.loads(a.limits.read_text()))
        atomic_json(a.out or a.state / "weights.json", result)
    except (OSError, ValueError, sqlite3.Error, KeyError, TypeError):
        print(json.dumps({"error": "Cannot fit weights: check local input files and schemas."}))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
