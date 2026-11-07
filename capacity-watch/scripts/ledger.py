#!/usr/bin/env python3
"""Local call ledger. Standard library only; never reads credentials or calls APIs.

Run with python3 -I. Sources are read-only; only CAPACITY_LEDGER is written.
Tokens use disjoint input/cache buckets; output includes reasoning, which is
also reported separately. Costs absent from a source remain NULL, not zero.
"""
import argparse
import bisect
import collections
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import socket
import sqlite3


STATE = Path.home() / ".local/state/capacity-watch"
TOKEN_FIELDS = ("tokens_in", "tokens_out", "tokens_cache_read",
                "tokens_cache_write", "tokens_reasoning")
COLUMNS = ("ts", "host", "harness", "session_id", "message_id", "cwd", "task_id",
           "provider", "model", "route", *TOKEN_FIELDS, "list_cost_usd",
           "allowance_usd", "latency_s", "outcome", "window_snapshot")
SCHEMA = """
CREATE TABLE IF NOT EXISTS calls (
    ts TEXT NOT NULL, host TEXT NOT NULL, harness TEXT NOT NULL,
    session_id TEXT NOT NULL, message_id TEXT NOT NULL, cwd TEXT, task_id TEXT,
    provider TEXT NOT NULL, model TEXT NOT NULL,
    route TEXT NOT NULL CHECK(route IN ('subscription','free','metered','unknown')),
    tokens_in INTEGER, tokens_out INTEGER, tokens_cache_read INTEGER,
    tokens_cache_write INTEGER, tokens_reasoning INTEGER,
    list_cost_usd REAL, allowance_usd REAL, latency_s REAL, outcome TEXT,
    window_snapshot TEXT,
    PRIMARY KEY (harness, session_id, message_id)
);
CREATE INDEX IF NOT EXISTS calls_ts ON calls(ts);
"""


def timestamp(value):
    try:
        if isinstance(value, (int, float)):
            value = dt.datetime.fromtimestamp(value / 1000 if value > 1e11 else value,
                                              dt.timezone.utc)
        else:
            value = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        if value.tzinfo is None:
            value = value.replace(tzinfo=dt.timezone.utc)
        return value.astimezone(dt.timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
    except (AttributeError, ValueError, TypeError, OverflowError, OSError):
        return None


def number(value):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if math.isfinite(value) and value >= 0:
            return value
    return None


def obj(value):
    return value if isinstance(value, dict) else {}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def provider_for(model):
    """Model vendor when the source does not identify a serving provider."""
    m = model.lower().split("/")[-1]
    for prefix, vendor in (("claude", "anthropic"), ("gpt-", "openai"),
                           ("o1", "openai"), ("o3", "openai"), ("o4", "openai"),
                           ("muse-", "meta"), ("llama", "meta"),
                           ("deepseek", "deepseek"), ("gemini", "google"),
                           ("glm", "zai"), ("kimi", "moonshot"), ("mimo", "xiaomi")):
        if m.startswith(prefix):
            return vendor
    # An aggregator id such as "thinkingmachines/inkling:free" names its vendor.
    return model.split("/")[0].lower() if "/" in model else "unknown"


def route_for(provider, model, billing=None, cost=None):
    if model.endswith(("-free", ":free")) or billing == "free":
        return "free"
    if billing == "go" or provider in ("opencode-go", "openai-codex"):
        return "subscription"
    if billing in ("balance", "credits", "pay-as-you-go") or (cost is not None and cost > 0):
        return "metered"
    return "unknown"


def row(harness, session, message, ts, host, model=None, provider=None, cwd=None):
    result = dict.fromkeys(COLUMNS)
    model = model if isinstance(model, str) and model else "unknown"
    provider = provider if isinstance(provider, str) and provider else provider_for(model)
    result.update(ts=timestamp(ts), host=host, harness=harness,
                  session_id=str(session), message_id=str(message), cwd=cwd,
                  model=model, provider=provider, route=route_for(provider, model), outcome="unknown")
    return result


def usage(row, values):
    # Missing optional counters are zero only when a usage object exists.
    for field, value in zip(TOKEN_FIELDS, values):
        n = number(value)
        row[field] = int(n) if n is not None else 0


def outcome(value):
    if value in ("ok", "stop", "end_turn", "tool_use", "toolUse", "length", "max_tokens"):
        return "ok"
    if value in (429, "429"):
        return "429"
    if value in ("error", "aborted", "cancelled", "stall"):
        return "stall" if value == "stall" else "error"
    return "unknown"


def records(path, stats, markers=()):
    """Stream a bounded snapshot, never log malformed input or exception text."""
    try:
        with path.open(errors="replace") as stream:
            size = os.fstat(stream.fileno()).st_size
            while stream.tell() < size:
                line = stream.readline()
                if not line:
                    break
                if markers and not any(marker in line for marker in markers):
                    continue
                try:
                    value = json.loads(line)
                except ValueError:
                    stats["malformed_json"] += 1
                    continue
                if isinstance(value, dict):
                    yield value, stream.tell()
                else:
                    stats["invalid_records"] += 1
    except OSError:
        stats["unreadable_files"] += 1


def files(home, patterns, since, stats):
    patterns = (patterns,) if isinstance(patterns, str) else patterns
    paths = sorted({p for pattern in patterns for p in home.glob(pattern)})
    stats["files_found"] = len(paths)
    for path in paths:
        if since and timestamp(path.stat().st_mtime) < since:
            stats["files_before_since"] += 1
            continue
        stats["files_read"] += 1
        yield path


def claude(home, since, host, stats):
    # Subagent transcripts live below the session directory and carry real calls.
    for path in files(home, (".claude/projects/*/*.jsonl",
                             ".claude/projects/*/*/subagents/**/*.jsonl"), since, stats):
        for d, offset in records(path, stats, ('"usage"',)):
            m = obj(d.get("message"))
            u = obj(m.get("usage"))
            if d.get("type") != "assistant" or not u:
                continue
            r = row("claude", d.get("sessionId") or path.stem,
                    m.get("id") or d.get("uuid") or f"offset:{offset}",
                    d.get("timestamp"), host, m.get("model"), cwd=d.get("cwd"))
            usage(r, [u.get(k) for k in ("input_tokens", "output_tokens",
                      "cache_read_input_tokens", "cache_creation_input_tokens", "reasoning_tokens")])
            # A Claude harness does not prove Anthropic billing (proxies exist).
            r["outcome"] = outcome(m.get("stop_reason"))
            yield r


def snapshot(rl):
    result = {}
    for key in ("primary", "secondary"):
        w = obj(rl.get(key))
        if w:
            result[key] = {k: number(w.get(k)) for k in
                           ("used_percent", "window_minutes", "resets_at")}
    for key in ("plan_type", "limit_id"):
        if isinstance(rl.get(key), str):
            result[key] = rl[key]
    return json.dumps(result, sort_keys=True) if result else None


def codex(home, since, host, stats):
    for path in files(home, ".codex/sessions/*/*/*/rollout-*.jsonl", since, stats):
        session, cwd, model, previous = path.stem, None, None, None
        for d, offset in records(path, stats, ('"session_meta"', '"turn_context"', '"token_count"')):
            p = obj(d.get("payload"))
            if d.get("type") == "session_meta":
                session, cwd, model = p.get("id") or p.get("session_id") or session, p.get("cwd"), p.get("model")
            elif d.get("type") == "turn_context":
                model, cwd = p.get("model") or model, p.get("cwd") or cwd
            elif d.get("type") == "event_msg" and p.get("type") == "token_count":
                info = obj(p.get("info"))
                u = obj(info.get("last_token_usage"))
                if not u:
                    stats["snapshot_only_events"] += 1
                    continue
                total = obj(info.get("total_token_usage"))
                signature = digest([total, u]) if total else None
                if signature and signature == previous:
                    stats["repeated_usage_events"] += 1
                    continue
                previous = signature
                r = row("codex", session, d.get("ordinal", f"offset:{offset}"),
                        d.get("timestamp"), host, model, "openai", cwd)
                cached = number(u.get("cached_input_tokens")) or 0
                written = number(u.get("cache_write_input_tokens")) or 0
                inp = number(u.get("input_tokens")) or 0
                out = number(u.get("output_tokens")) or 0
                reasoning = number(u.get("reasoning_output_tokens")) or 0
                if info.get("last_usage_includes_reasoning") is False:
                    out += reasoning
                usage(r, [max(0, inp - cached - written), out, cached, written, reasoning])
                rl = obj(p.get("rate_limits"))
                r["window_snapshot"] = snapshot(rl)
                r["route"] = "subscription" if rl.get("plan_type") else "unknown"
                yield r


def omp(home, since, host, stats):
    for path in files(home, ".omp/agent/sessions/*/*.jsonl", since, stats):
        session, cwd, model, provider = path.stem, None, None, None
        for d, offset in records(path, stats, ('"session"', '"model_change"', '"assistant"')):
            if d.get("type") == "session":
                session, cwd = d.get("id") or session, d.get("cwd")
            elif d.get("type") == "model_change":
                changed = d.get("model")
                if isinstance(changed, str):
                    provider, sep, model = changed.partition("/")
                    if not sep:
                        model, provider = changed, None
            elif d.get("type") == "message":
                m = obj(d.get("message"))
                if m.get("role") != "assistant":
                    continue
                r = row("omp", session, m.get("responseId") or d.get("id") or f"offset:{offset}",
                        m.get("completedAt") or d.get("timestamp") or m.get("timestamp"),
                        host, m.get("model") or model, m.get("provider") or provider, cwd)
                u = obj(m.get("usage"))
                if u:
                    usage(r, [u.get(k) for k in ("input", "output", "cacheRead", "cacheWrite", "reasoningTokens")])
                    r["list_cost_usd"] = number(obj(u.get("cost")).get("total"))
                r["latency_s"] = number(m.get("duration"))
                if r["latency_s"] is not None:
                    r["latency_s"] /= 1000
                r["outcome"] = outcome(m.get("errorStatus") if m.get("errorStatus") == 429
                                       else m.get("stopReason"))
                # OMP cost is a catalog estimate, not proof of metered billing.
                yield r


def opencode(home, since, host, stats):
    path = home / ".local/share/opencode/opencode.db"
    stats["files_found"] = int(path.exists())
    if not path.exists():
        return
    conn = None
    try:
        conn = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
        required = {"message": {"id", "session_id", "time_created", "data"},
                    "session": {"id", "directory"}}
        for table, fields in required.items():
            actual = {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}
            if not fields <= actual:
                stats["schema_mismatch"] += 1
                return
        stats["files_read"] += 1
        newest = conn.execute("SELECT max(time_created) FROM message").fetchone()[0]
        stats["newest_source_ts"] = timestamp(newest) if newest is not None else None
        cutoff = dt.datetime.fromisoformat(since.replace("Z", "+00:00")).timestamp() * 1000 if since else 0
        query = """SELECT m.id, m.session_id, m.time_created, m.data, s.directory
                   FROM message m LEFT JOIN session s ON m.session_id=s.id
                   WHERE m.time_created >= ? ORDER BY m.time_created, m.id"""
        for mid, sid, created, raw, cwd in conn.execute(query, (cutoff,)):
            try:
                m = obj(json.loads(raw))
            except (ValueError, TypeError):
                stats["malformed_json"] += 1
                continue
            if m.get("role") != "assistant":
                continue
            if not isinstance(m.get("tokens"), dict):
                stats["unsupported_messages"] += 1
                continue
            r = row("opencode", sid, mid, created, host, m.get("modelID"), m.get("providerID"), cwd)
            u, t = m["tokens"], obj(m.get("time"))
            cache = obj(u.get("cache"))
            reasoning = number(u.get("reasoning")) or 0
            usage(r, [u.get("input"), (number(u.get("output")) or 0) + reasoning,
                      cache.get("read"), cache.get("write"), reasoning])
            r["list_cost_usd"] = number(m.get("cost"))
            # OpenCode's zero catalog cost does not establish a free route.
            r["outcome"] = "error" if m.get("error") else outcome(m.get("finish"))
            start, end = number(t.get("created")), number(t.get("completed"))
            if start is not None and end is not None and end >= start:
                r["ts"], r["latency_s"] = timestamp(end), (end - start) / 1000
            yield r
    except sqlite3.Error:
        stats["database_errors"] += 1
    finally:
        if conn is not None:
            conn.close()


def direct(home, since, host, stats):
    path = home / ".local/state/capacity-watch/calls-direct.jsonl"
    stats["files_found"] = int(path.exists())
    if not path.exists():
        return
    stats["files_read"] += 1
    for d, offset in records(path, stats):
        r = row(d.get("harness") or "direct-api", d.get("session_id") or "job:" + digest(d.get("job")),
                d.get("message_id") or f"offset:{offset}", d.get("ts"), host,
                d.get("model"), d.get("provider"), d.get("cwd"))
        u = obj(d.get("usage"))
        go = obj(u.get("opencode"))
        tokens = obj(go.get("tokens"))
        if tokens:
            usage(r, [tokens.get("input"), tokens.get("output"), tokens.get("cache_read"),
                      (number(tokens.get("cache_write_5m")) or 0) + (number(tokens.get("cache_write_1h")) or 0),
                      tokens.get("reasoning")])
        elif u:
            cached = number(obj(u.get("prompt_tokens_details")).get("cached_tokens")) or number(u.get("cache_read_input_tokens")) or 0
            inp = number(u.get("prompt_tokens"))
            usage(r, [max(0, inp - cached) if inp is not None else u.get("input_tokens"),
                      u.get("completion_tokens", u.get("output_tokens")), cached,
                      u.get("cache_creation_input_tokens"),
                      obj(u.get("completion_tokens_details")).get("reasoning_tokens")])
        r["list_cost_usd"] = number(go.get("list_cost", u.get("cost")))
        r["allowance_usd"] = number(go.get("allowance"))
        r["route"] = route_for(r["provider"], r["model"], go.get("billing_source"), r["list_cost_usd"])
        r["latency_s"], r["outcome"] = number(d.get("latency_s")), outcome(d.get("outcome"))
        yield r


ADAPTERS = {"claude": claude, "codex": codex, "omp": omp, "opencode": opencode, "direct-api": direct}


def ingest(conn, home, since=None, host=None):
    host = host or socket.gethostname()
    summaries = {}
    key = ("harness", "session_id", "message_id")
    # Streaming Claude fragments share a message id. Merge their final counters,
    # never add repeated fragments. Re-ingesting the same source is a no-op.
    updates = []
    for c in COLUMNS:
        if c in key or c in ("host", "ts"):
            continue
        if c in TOKEN_FIELDS:
            updates.append(f"{c}=CASE WHEN calls.{c} IS NULL THEN excluded.{c} "
                           f"WHEN excluded.{c} IS NULL THEN calls.{c} ELSE MAX(calls.{c},excluded.{c}) END")
        else:
            updates.append(f"{c}=COALESCE(excluded.{c},calls.{c})")
    sql = (f"INSERT INTO calls ({','.join(COLUMNS)}) VALUES ({','.join('?' for _ in COLUMNS)}) "
           f"ON CONFLICT ({','.join(key)}) DO UPDATE SET {','.join(updates)}")
    for name, adapter in ADAPTERS.items():
        stats = collections.Counter()
        before = conn.execute("SELECT count(*) FROM calls").fetchone()[0]
        with conn:
            for r in adapter(home, since, host, stats):
                stats["candidate_rows"] += 1
                if not r["ts"]:
                    stats["invalid_timestamps"] += 1
                    continue
                if since and r["ts"] < since:
                    stats["rows_before_since"] += 1
                    continue
                conn.execute(sql, [r[c] for c in COLUMNS])
                stats["accepted_records"] += 1
        stats["inserted_rows"] = conn.execute("SELECT count(*) FROM calls").fetchone()[0] - before
        if not stats["accepted_records"]:
            newest = stats.get("newest_source_ts")
            stats["zero_rows_reason"] = ("store absent" if not stats["files_found"] else
                                         "schema differs" if stats["schema_mismatch"] else
                                         f"newest source record ({newest}) predates --since"
                                         if newest and since and newest < since else
                                         "no eligible assistant usage in the requested time range; see counters")
        summaries[name] = dict(stats)
    counts = dict(conn.execute("SELECT harness,count(*) FROM calls GROUP BY harness"))
    return {"since": since, "host": host, "adapters": summaries, "rows_by_harness": counts,
            "total_rows": sum(counts.values())}


def report(conn, since, by):
    group = "substr(ts,1,10)" if by == "day" else by
    fields = [f"SUM(COALESCE({f},0)) AS {f}" for f in TOKEN_FIELDS]
    fields += ["SUM(COALESCE(tokens_in,0)+COALESCE(tokens_out,0)+COALESCE(tokens_cache_read,0)+COALESCE(tokens_cache_write,0)) AS tokens_total",
               "SUM(list_cost_usd) AS list_cost_usd", "COUNT(list_cost_usd) AS cost_known_calls",
               "SUM(allowance_usd) AS allowance_usd", "COUNT(allowance_usd) AS allowance_known_calls",
               "COUNT(tokens_in) AS usage_known_calls"]
    cur = conn.execute(f"SELECT {group} AS {by}, COUNT(*) AS calls,{','.join(fields)} "
                       f"FROM calls WHERE ts>=? GROUP BY {group} ORDER BY {group}", (since,))
    return [dict(zip([c[0] for c in cur.description], r)) for r in cur]


def in_pool(r, pool):
    if pool == "codex":
        return r["harness"] == "codex" and r["route"] == "subscription"
    if pool == "opencode-go":
        return r["provider"] == "opencode-go" and r["route"] == "subscription"
    # Claude JSONL lacks billing evidence: this is an explicit candidate estimate.
    return r["provider"] == "anthropic" and r["harness"] == "claude"


RESET_JITTER_S = 900  # One window's resets_at drifts by seconds between snapshots.
MIN_INSTANCE_PERCENT = 5  # Integer percents make smaller instances pure rounding noise.


def epoch(iso):
    return dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp()


def window_instances(points):
    """Merge keys of one window whose reset times differ only by jitter."""
    series = collections.defaultdict(list)
    for (name, minutes, reset), observations in points.items():
        series[(name, minutes)].append((epoch(reset), reset, observations))
    for (name, minutes), items in sorted(series.items(), key=lambda x: str(x[0])):
        current = None
        for seconds, reset, observations in sorted(items, key=lambda x: x[0]):
            if current is None or seconds - current["start"] > RESET_JITTER_S:
                if current is not None:
                    yield name, minutes, current["reset"], current["observations"]
                current = {"start": seconds, "reset": reset, "observations": {}}
            for t, pct in observations.items():
                current["observations"][t] = max(pct, current["observations"].get(t, 0))
        if current is not None:
            yield name, minutes, current["reset"], current["observations"]


def reconcile(conn, pool, since, readings, expect=None):
    """Tokens per window-percent. `tokens_uncached` excludes cache reads, the
    measure the 2026-11-07 Codex anchor used; `tokens_all` includes them."""
    expect = expect or {}
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute("SELECT * FROM calls WHERE ts>=? ORDER BY ts", (since,))]
    rows = [r for r in rows if in_pool(r, pool)]
    times, all_sum, uncached_sum = [], [0], [0]
    for r in rows:
        times.append(r["ts"])
        all_sum.append(all_sum[-1] + sum(r[k] or 0 for k in TOKEN_FIELDS[:4]))
        uncached_sum.append(uncached_sum[-1] + sum(r[k] or 0 for k in
                                                   ("tokens_in", "tokens_out", "tokens_cache_write")))
    points = collections.defaultdict(dict)
    if pool == "codex":
        # Concurrent sessions write snapshots out of order, so within one fixed
        # window a lower percent is stale and never moves the baseline.
        monotone = True
        for r in rows:
            snap = obj(json.loads(r["window_snapshot"] or "{}"))
            limit = snap.get("limit_id")
            for name, w in snap.items():
                if not isinstance(w, dict):
                    continue
                if isinstance(limit, str) and limit != "codex":
                    name = f"{limit}.{name}"
                reset, pct = timestamp(w.get("resets_at")), number(w.get("used_percent"))
                if reset and pct is not None and pct <= 100 and reset > r["ts"]:
                    key = (name, w.get("window_minutes"), reset)
                    points[key][r["ts"]] = max(pct, points[key].get(r["ts"], 0))
    else:
        # One probe writes readings in order, so a decrease is real (rolling windows).
        monotone = False
        for d, _ in records(readings, collections.Counter()):
            if d.get("name") != pool or d.get("status") != "ok":
                continue
            t = timestamp(d.get("observed_at") or d.get("probed_at"))
            if not t or t < since:
                continue
            for name, w in obj(d.get("windows")).items():
                w = obj(w)
                reset, fraction = timestamp(w.get("resets_at")), number(w.get("used_fraction"))
                if w.get("rolled_over") or not reset or reset <= t or fraction is None or fraction > 1:
                    continue
                key = (name, w.get("window_minutes"), reset)
                points[key][t] = max(fraction * 100, points[key].get(t, 0))
    summaries = {}
    for name, minutes, reset, observations in window_instances(points):
        label = f"{name}:{minutes}" if minutes else name
        s = summaries.setdefault(label, dict(
            window=name, window_minutes=minutes, observations=0, samples=0,
            tokens_all=0, tokens_uncached=0, percent_delta=0.0, decreases_skipped=0,
            no_token_samples=0, saturated_samples=0, instances=[]))
        s["observations"] += len(observations)
        anchor, inst = None, dict(resets_at=reset, first=None, last=None,
                                  percent_delta=0.0, tokens_uncached=0, tokens_all=0)
        for t, pct in sorted(observations.items()):
            if anchor is None:
                anchor, inst["first"] = (t, pct), t
                continue
            if pct < anchor[1]:
                s["decreases_skipped"] += 1
                if not monotone:
                    anchor = (t, pct)
                continue
            delta = pct - anchor[1]
            if delta <= 1e-9:
                continue  # Keep the baseline through rounded-percent plateaus.
            start, end = bisect.bisect_right(times, anchor[0]), bisect.bisect_right(times, t)
            tokens_all = all_sum[end] - all_sum[start]
            tokens_uncached = uncached_sum[end] - uncached_sum[start]
            s["samples"] += 1
            s["no_token_samples"] += int(tokens_all == 0)
            s["saturated_samples"] += int(pct >= 100)
            for target in (s, inst):
                target["tokens_all"] += tokens_all
                target["tokens_uncached"] += tokens_uncached
                target["percent_delta"] += delta
            inst["last"] = t
            anchor = (t, pct)
        if inst["percent_delta"]:
            inst["percent_delta"] = round(inst["percent_delta"], 8)
            inst["uncached_tokens_per_percent"] = round(inst["tokens_uncached"] / inst["percent_delta"], 3)
            s["instances"].append(inst)
    verdicts = []
    for label, s in summaries.items():
        s["percent_delta"] = round(s["percent_delta"], 8)
        p = s["percent_delta"]
        s["uncached_tokens_per_percent"] = round(s["tokens_uncached"] / p, 3) if p else None
        s["all_tokens_per_percent"] = round(s["tokens_all"] / p, 3) if p else None
        ratio, check = s["uncached_tokens_per_percent"], {"verdict": "unverified"}
        if label in expect and ratio:
            error = ratio / expect[label] - 1
            check = {"basis": "expected uncached tokens per percent", "expected": expect[label],
                     "relative_error": round(error, 4),
                     "verdict": "pass" if abs(error) <= 0.10 else "fail"}
        else:
            big = [i for i in s["instances"] if i["percent_delta"] >= MIN_INSTANCE_PERCENT]
            if len(big) >= 2 and ratio:
                worst = max(abs(i["uncached_tokens_per_percent"] / ratio - 1) for i in big)
                check = {"basis": f"agreement of {len(big)} window instances with the pooled ratio",
                         "max_relative_deviation": round(worst, 4),
                         "verdict": "pass" if worst <= 0.10 else "fail"}
            else:
                check["reason"] = (f"fewer than 2 window instances with at least {MIN_INSTANCE_PERCENT} "
                                   "percent movement, and no --expect value")
        s["gate"] = check
        verdicts.append(check["verdict"])
    gate = ("fail" if "fail" in verdicts else "pass" if verdicts and all(v == "pass" for v in verdicts)
            else "partial" if "pass" in verdicts else "unverified")
    return {"pool": pool, "since": since, "candidate_calls": len(rows),
            "candidate_tokens_all": all_sum[-1], "candidate_tokens_uncached": uncached_sum[-1],
            "windows": list(summaries.values()),
            "status": "measured" if any(s["samples"] for s in summaries.values()) else "insufficient_samples",
            "gate_within_10_percent": gate,
            "limits": ("Local calls only; account-wide quota may include other hosts or cloud tasks. "
                       "Provider percents are integers, so small deltas are rounding noise. "
                       "Stale (out-of-order) Codex snapshots and resets are excluded. "
                       "Claude billing is inferred from native Anthropic model ids.")}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="command", required=True)
    ing = sub.add_parser("ingest")
    ing.add_argument("--since", help="ISO date/time; naive values are UTC")
    ing.add_argument("--host", default=socket.gethostname())
    rep = sub.add_parser("report")
    rep.add_argument("--days", type=int, default=14)
    rep.add_argument("--by", choices=("provider", "model", "harness", "day"), default="provider")
    rec = sub.add_parser("reconcile")
    rec.add_argument("--pool", choices=("codex", "opencode-go", "claude"), required=True)
    rec.add_argument("--days", type=int, default=7)
    rec.add_argument("--expect", action="append", default=[], metavar="WINDOW=TOKENS",
                     help="expected uncached tokens per percent, e.g. primary:300=4460")
    a = ap.parse_args()
    expect = {}
    for item in getattr(a, "expect", []):
        label, _, value = item.partition("=")
        try:
            expect[label] = float(value)
        except ValueError:
            ap.error("--expect takes WINDOW=NUMBER")
        if not label or expect[label] <= 0:
            ap.error("--expect takes WINDOW=NUMBER with a positive number")
    if hasattr(a, "days") and a.days <= 0:
        ap.error("--days must be positive")
    since = timestamp(a.since) if a.command == "ingest" else timestamp(
        (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=a.days)).timestamp())
    if a.command == "ingest" and a.since and not since:
        ap.error("--since must be an ISO date/time")
    path = Path(os.environ.get("CAPACITY_LEDGER", str(STATE / "ledger.sqlite"))).expanduser()
    try:
        if a.command == "ingest":
            path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(path)
            conn.executescript(SCHEMA)
        else:
            conn = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
        try:
            if a.command == "ingest":
                result = ingest(conn, Path.home(), since, a.host)
            elif a.command == "report":
                result = {"since": since, "by": a.by, "rows": report(conn, since, a.by)}
            else:
                result = reconcile(conn, a.pool, since, STATE / "readings.jsonl", expect)
        finally:
            conn.close()
    except (OSError, sqlite3.Error) as exc:
        print(json.dumps({"error": type(exc).__name__, "detail": "cannot access ledger; ingest first and check local permissions/schema"}))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
