#!/usr/bin/env python3
"""quota-probe: read the remaining quota of every LLM route without spending any.

Prints one JSON object per line, one line per provider:
  claude, codex, agy, openrouter, opencode-zen, kilo

Common fields on every line:
  name           provider key
  status         ok | stale | unknown
  used_fraction  0.0 to 1.0 of the binding window, or null
  remaining      remaining count when the provider counts requests, or null
  resets_at      ISO 8601 UTC of the binding window reset, or null
  windows        every window seen, keyed by window name
  source         where the number came from
  observed_at    ISO 8601 UTC of the reading itself
  age_s          seconds between observed_at and now
  confidence     high | medium | low | none
  reason         why a value is missing or estimated (only when relevant)

With --active (verified 2026-11-06), four providers are read from their own
usage endpoints, each token sent only to its issuer and never refreshed here:
  claude       GET api.anthropic.com/api/oauth/usage (five_hour, seven_day)
  codex        GET chatgpt.com/backend-api/wham/usage (5-hour and weekly)
  agy          POST cloudcode-pa v1internal:fetchAvailableModels (per model;
               internal endpoint, may change)
  opencode-go  GET opencode.ai/zen/go/v1/usage (rolling 5-hour, weekly,
               monthly; undocumented)
If an active read fails, the passive reading below answers and the record
carries active_failed with the reason. opencode-go has no passive reading.

Sources without --active, all read only:
  claude      Claude Code stream-json rate_limit_event lines in job logs (passive)
  codex       token_count events in ~/.codex/sessions rollout files (passive)
  agy         ~/.gemini/antigravity-cli logs: activity and quota errors only (passive);
              agy never writes its quota numbers to disk, so used_fraction stays null
  openrouter  GET https://openrouter.ai/api/v1/key (free; spends no request quota),
              cached for --net-max-age seconds; local request counts with --offline
  opencode-zen, kilo
              no quota endpoint; local request and error counts from the
              OpenCode and Kilo SQLite stores, plus Kilo's documented hourly cap

Never prints, logs or copies a credential. The OpenRouter key is read from
OpenCode's auth store only to send it to OpenRouter itself, then discarded.

Usage:
  quota-probe.py                    all providers, one JSON line each
  quota-probe.py --offline          no network at all
  quota-probe.py --only codex,claude
  quota-probe.py --merge A.jsonl B.jsonl
                                    combine readings taken on several hosts:
                                    per provider keep the newest window and the
                                    highest use inside it
  ssh HOST python3 - --offline < quota-probe.py   probe a mesh peer

Standard library only. Exit 0 always unless arguments are wrong; a provider
that cannot be read is reported as status "unknown" with a reason.
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.request

HOME = os.path.expanduser("~")
NOW = time.time()
STATE_DIR = os.path.join(HOME, ".local", "state", "mesh-telemetry")
CACHE = os.path.join(STATE_DIR, "quota-probe-cache.json")

JOB_LOG_GLOBS = [
    "~/work/jobs/*/log.jsonl",
    "~/work/*/logs/*.jsonl",
]
CODEX_SESSIONS = "~/.codex/sessions/**/*.jsonl"
AGY_LOGS = "~/.gemini/antigravity-cli/log/cli-*.log"
OPENCODE_DB = "~/.local/share/opencode/opencode.db"
KILO_DB = "~/.local/share/kilo/kilo.db"
OPENCODE_AUTH = "~/.local/share/opencode/auth.json"

# Documented caps used for estimates (see router-design.md for sources).
OPENROUTER_FREE_RPM = 20
KILO_ANON_PER_HOUR = 200
AGY_WINDOW_S = 5 * 3600


# ----------------------------------------------------------------- helpers

def iso(ts):
    if ts is None:
        return None
    return dt.datetime.fromtimestamp(float(ts), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(s):
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except (AttributeError, ValueError):
        return None


def newest(pattern, n):
    files = glob.glob(os.path.expanduser(pattern), recursive=True)
    files = [f for f in files if os.path.isfile(f)]
    files.sort(key=os.path.getmtime, reverse=True)
    return files[:n]


def base(name, **kw):
    rec = {"name": name, "status": "unknown", "used_fraction": None, "remaining": None,
           "resets_at": None, "windows": {}, "source": None, "observed_at": None,
           "age_s": None, "confidence": "none"}
    rec.update(kw)
    return rec


def stamp(rec, observed_ts):
    rec["observed_at"] = iso(observed_ts)
    rec["age_s"] = int(NOW - observed_ts) if observed_ts else None
    return rec


def ro_db(path):
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=5)


def load_cache():
    try:
        with open(CACHE) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def save_cache(cache):
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        tmp = CACHE + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(cache, fh)
        os.replace(tmp, CACHE)
    except OSError:
        pass


def window(used, resets_ts, minutes=None):
    """One window record. A window whose reset has passed is reported as
    rolled over: use is assumed 0 because the provider resets it fully."""
    w = {"used_fraction": used, "resets_at": iso(resets_ts)}
    if minutes:
        w["window_minutes"] = minutes
    if resets_ts and resets_ts <= NOW:
        w["rolled_over"] = True
        w["used_fraction"] = 0.0
        w["resets_at"] = None
    return w


def binding(rec):
    """Set used_fraction and resets_at from the most used window."""
    ws = [w for w in rec["windows"].values() if w.get("used_fraction") is not None]
    if ws:
        top = max(ws, key=lambda w: w["used_fraction"])
        rec["used_fraction"] = round(top["used_fraction"], 4)
        rec["resets_at"] = top.get("resets_at")
    return rec


def grade(rec, fresh_s, stale_s):
    """Confidence from age for provider-reported numbers."""
    age = rec.get("age_s")
    if age is None:
        return rec
    if age <= fresh_s:
        rec["status"], rec["confidence"] = "ok", "high"
    elif age <= stale_s:
        rec["status"], rec["confidence"] = "ok", "medium"
    else:
        rec["status"], rec["confidence"] = "stale", "low"
    if any(w.get("rolled_over") for w in rec["windows"].values()):
        rec["confidence"] = "medium" if rec["confidence"] == "high" else rec["confidence"]
        rec["reason"] = "a window reset after the last reading; its use is assumed to be 0"
    return rec


# ------------------------------------------------------------------ claude

def probe_claude(_args):
    rec = base("claude", source="Claude Code stream-json rate_limit_event in job logs")
    files = []
    for g in JOB_LOG_GLOBS:
        files += newest(g, 40)
    files = sorted(set(files), key=os.path.getmtime, reverse=True)[:40]
    best = None  # (resetsAt, utilization, mtime, info, file)
    for f in files:
        mtime = os.path.getmtime(f)
        try:
            with open(f, errors="replace") as fh:
                for line in fh:
                    if '"rate_limit_event"' not in line:
                        continue
                    try:
                        info = json.loads(line)["rate_limit_info"]
                        sd = info["unifiedWindows"]["seven_day"]
                        key = (float(sd["resetsAt"]), float(sd["utilization"]), mtime)
                    except (ValueError, KeyError, TypeError):
                        continue
                    if best is None or key > best[:3]:
                        best = key + (info, f)
        except OSError:
            continue
    if best is None:
        rec["reason"] = "no rate_limit_event found in the newest job logs on this host"
        return rec
    _, _, mtime, info, f = best
    for name, w in (info.get("unifiedWindows") or {}).items():
        try:
            rec["windows"][name] = window(float(w["utilization"]), float(w["resetsAt"]))
            rec["windows"][name]["status"] = w.get("status")
        except (KeyError, TypeError, ValueError):
            continue
    rec["overage"] = {"status": info.get("overageStatus"), "in_use": info.get("isUsingOverage")}
    rec["source_file"] = f
    stamp(rec, mtime)
    rec["freshness_note"] = "observed_at is the log file mtime; the event itself has no timestamp"
    binding(rec)
    # Claude events arrive at every turn of every running job, so 30 minutes
    # without one means no Claude job is running, not that the number moved.
    return grade(rec, fresh_s=1800, stale_s=6 * 3600)


# ------------------------------------------------------------------- codex

def probe_codex(_args):
    rec = base("codex", source="token_count.rate_limits in ~/.codex/sessions rollout files")
    found = None
    for f in newest(CODEX_SESSIONS, 25):
        last = None
        try:
            with open(f, errors="replace") as fh:
                for line in fh:
                    if '"rate_limits"' not in line:
                        continue
                    try:
                        d = json.loads(line)
                        rl = (d.get("payload") or {}).get("rate_limits") or {}
                    except ValueError:
                        continue
                    if rl.get("primary") or rl.get("secondary"):
                        last = (parse_iso(d.get("timestamp", "")) or os.path.getmtime(f), rl)
        except OSError:
            continue
        if last and (found is None or last[0] > found[0]):
            found = last + (f,)
    if found is None:
        rec["reason"] = "no Codex rollout with rate_limits windows on this host"
        return rec
    ts, rl, f = found
    for name in ("primary", "secondary"):
        w = rl.get(name)
        if not w:
            continue
        mins = w.get("window_minutes")
        label = {300: "five_hour", 10080: "weekly"}.get(mins, name)
        rec["windows"][label] = window(float(w.get("used_percent", 0)) / 100.0, w.get("resets_at"), mins)
    rec["plan"] = rl.get("plan_type")
    rec["limit_reached"] = rl.get("rate_limit_reached_type")
    cr = rl.get("credits") or {}
    rec["credits"] = {"has_credits": cr.get("has_credits"), "unlimited": cr.get("unlimited")}
    rec["source_file"] = f
    stamp(rec, ts)
    binding(rec)
    # A five-hour window moves fast; an hour-old reading is only indicative.
    return grade(rec, fresh_s=900, stale_s=3 * 3600)


# --------------------------------------------------------------------- agy

AGY_LINE = re.compile(r"^[IWEF](\d{2})(\d{2}) (\d{2}):(\d{2}):(\d{2})")


def agy_ts(line, year):
    m = AGY_LINE.match(line)
    if not m:
        return None
    mo, d, H, M, S = map(int, m.groups())
    try:
        # glog writes local time without a year.
        t = dt.datetime(year, mo, d, H, M, S).timestamp()
    except ValueError:
        return None
    if t > NOW + 86400:  # December log read in January
        t = dt.datetime(year - 1, mo, d, H, M, S).timestamp()
    return t


def probe_agy(_args):
    rec = base("agy", source="~/.gemini/antigravity-cli/log (activity and quota errors only)")
    logs = newest(AGY_LOGS, 10)
    if not logs:
        rec["reason"] = "no agy logs on this host"
        return rec
    year = dt.datetime.now().year
    since = NOW - AGY_WINDOW_S
    calls = errors = refreshes = 0
    last_err = last_any = None
    for f in logs:
        if os.path.getmtime(f) < since:
            continue
        try:
            with open(f, errors="replace") as fh:
                for line in fh:
                    hot = ("streamGenerateContent" in line, "RESOURCE_EXHAUSTED" in line
                           or " 429" in line or "quota exceeded" in line.lower(),
                           "doRefreshQuota: starting" in line)
                    if not any(hot):
                        continue
                    t = agy_ts(line, year)
                    if t is None or t < since:
                        continue
                    last_any = max(last_any or 0, t)
                    calls += hot[0]
                    refreshes += hot[2]
                    if hot[1]:
                        errors += 1
                        last_err = max(last_err or 0, t)
        except OSError:
            continue
    rec["activity_5h"] = {"model_calls": calls, "quota_errors": errors, "quota_refreshes": refreshes,
                          "last_quota_error_at": iso(last_err)}
    rec["windows"]["five_hour"] = {"used_fraction": None, "window_minutes": 300, "resets_at": None}
    if last_err and NOW - last_err < AGY_WINDOW_S:
        # A quota error inside the window is the one hard signal agy leaves on disk.
        rec["status"] = "ok"
        rec["used_fraction"] = 1.0
        rec["confidence"] = "medium"
        rec["resets_at"] = None
        rec["reason"] = ("agy hit a quota error in the last 5 hours; treat as exhausted "
                         "until a later successful call or 5 hours pass")
        stamp(rec, last_err)
        return rec
    rec["reason"] = ("agy fetches quota (v1internal:fetchAvailableModels, quotaInfo.remainingFraction "
                     "and resetTime per model) about every 5 minutes but never writes the numbers to "
                     "disk; activity_5h is a usage proxy only")
    if last_any:
        stamp(rec, last_any)
    return rec


# -------------------------------------------------------------- local DBs

def local_counts(db_path, provider_ids, model_filter=None):
    """Assistant messages per provider from an OpenCode-style store.
    Returns counts for the last minute, hour, UTC day, and error counts."""
    out = {"last_minute": 0, "last_hour": 0, "utc_day": 0, "errors_hour": 0,
           "rate_errors_hour": 0, "last_at": None}
    day0 = int(NOW // 86400 * 86400) * 1000
    with ro_db(db_path) as c:
        rows = c.execute("select time_created, data from message where time_created >= ?",
                         (min(day0, int((NOW - 3600) * 1000)),)).fetchall()
    for t_ms, data in rows:
        try:
            d = json.loads(data)
        except ValueError:
            continue
        if d.get("role") != "assistant" or d.get("providerID") not in provider_ids:
            continue
        if model_filter and not model_filter(d.get("modelID") or ""):
            continue
        t = t_ms / 1000.0
        out["last_at"] = max(out["last_at"] or 0, t)
        if t_ms >= day0:
            out["utc_day"] += 1
        if t >= NOW - 3600:
            out["last_hour"] += 1
            err = d.get("error")
            if err:
                out["errors_hour"] += 1
                s = json.dumps(err).lower()
                if "429" in s or "rate" in s or "quota" in s or "limit" in s:
                    out["rate_errors_hour"] += 1
        if t >= NOW - 60:
            out["last_minute"] += 1
    return out


def next_utc_midnight():
    return (NOW // 86400 + 1) * 86400


# -------------------------------------------------------------- openrouter

def openrouter_key():
    try:
        with open(os.path.expanduser(OPENCODE_AUTH)) as fh:
            k = (json.load(fh).get("openrouter") or {}).get("key")
    except (OSError, ValueError):
        k = None
    return k or os.environ.get("OPENROUTER_API_KEY")


def probe_openrouter(args):
    rec = base("openrouter")
    cache = load_cache()
    cached = cache.get("openrouter")
    data = None
    observed = None
    if cached and NOW - cached.get("ts", 0) <= args.net_max_age:
        data, observed = cached["data"], cached["ts"]
        rec["source"] = "GET /api/v1/key (cached)"
    elif not args.offline:
        key = openrouter_key()
        if key:
            req = urllib.request.Request("https://openrouter.ai/api/v1/key",
                                         headers={"Authorization": "Bearer " + key,
                                                  "User-Agent": "mesh-quota-probe"})
            del key
            try:
                with urllib.request.urlopen(req, timeout=15) as r:
                    raw = json.load(r).get("data") or {}
                # Keep only non-secret numeric fields; never the label or ids.
                data = {k: raw.get(k) for k in ("limit", "limit_remaining", "limit_reset", "usage",
                                                "usage_daily", "usage_weekly", "usage_monthly",
                                                "is_free_tier", "free_model_daily_requests")}
                observed = NOW
                cache["openrouter"] = {"ts": NOW, "data": data}
                save_cache(cache)
                rec["source"] = "GET /api/v1/key"
            except (urllib.error.URLError, OSError, ValueError) as e:
                rec["reason"] = f"/api/v1/key failed: {type(e).__name__} {getattr(e, 'code', '')}".strip()
        else:
            rec["reason"] = "no OpenRouter key in OpenCode's auth store or the environment"
    try:
        loc = local_counts(OPENCODE_DB, {"openrouter"}) if os.path.exists(os.path.expanduser(OPENCODE_DB)) else None
    except sqlite3.Error:
        loc = None
    if loc:
        rec["local_requests"] = loc
        rec["rpm_headroom"] = max(0, OPENROUTER_FREE_RPM - loc["last_minute"])
    if data:
        fm = data.get("free_model_daily_requests") or {}
        if fm.get("limit"):
            used = fm.get("used") or 0
            rec["windows"]["free_daily"] = {"used_fraction": round(used / fm["limit"], 4),
                                            "limit": fm["limit"], "remaining": fm.get("remaining"),
                                            "resets_at": iso(next_utc_midnight())}
            rec["remaining"] = fm.get("remaining")
        if data.get("limit"):
            rec["windows"]["credit_limit"] = {
                "used_fraction": round(1 - (data.get("limit_remaining") or 0) / data["limit"], 4),
                "resets_at": None, "reset_period": data.get("limit_reset")}
        rec["credits_used_usd"] = {"total": data.get("usage"), "today": data.get("usage_daily"),
                                   "week": data.get("usage_weekly")}
        rec["free_tier_account"] = data.get("is_free_tier")
        stamp(rec, observed)
        binding(rec)
        return grade(rec, fresh_s=900, stale_s=6 * 3600)
    if loc:
        # Offline estimate: limit is 1000/day if 10 credits were ever bought, else 50.
        limit = 1000 if (cached and not cached["data"].get("is_free_tier")) else None
        rec["source"] = "local OpenCode store (estimate; misses requests from other clients)"
        rec["remaining"] = max(0, limit - loc["utc_day"]) if limit else None
        rec["windows"]["free_daily"] = {"used_fraction": round(loc["utc_day"] / limit, 4) if limit else None,
                                        "limit": limit, "resets_at": iso(next_utc_midnight())}
        rec["status"], rec["confidence"] = "ok", "low"
        rec["reason"] = rec.get("reason") or "offline; counted local requests only"
        stamp(rec, loc["last_at"] or NOW)
        return binding(rec)
    rec["reason"] = rec.get("reason") or "offline and no local OpenRouter history"
    return rec


# ------------------------------------------------------- free gateways

def probe_free(name, db, provider_ids, hourly_cap, source):
    rec = base(name, source=source)
    try:
        loc = local_counts(db, provider_ids)
    except (FileNotFoundError, sqlite3.Error) as e:
        rec["reason"] = f"cannot read local store: {type(e).__name__}"
        return rec
    rec["local_requests"] = loc
    rec["status"], rec["confidence"] = "ok", "low"
    if hourly_cap:
        rec["remaining"] = max(0, hourly_cap - loc["last_hour"])
        rec["windows"]["hourly_per_ip"] = {"used_fraction": round(loc["last_hour"] / hourly_cap, 4),
                                           "limit": hourly_cap, "resets_at": None, "rolling": True}
        binding(rec)
        rec["reason"] = ("documented anonymous cap is per IP and per hour; this host's local count "
                         "misses other clients behind the same IP")
    else:
        rec["status"], rec["confidence"] = "unknown", "none"
        rec["reason"] = ("no published quota or quota endpoint; route on recent errors "
                         "(rate_errors_hour) and back off on 429")
    if loc["rate_errors_hour"] >= 3:
        rec["status"], rec["confidence"] = "ok", "medium"
        rec["used_fraction"] = 1.0
        rec["reason"] = "3 or more rate-limit errors in the last hour; treat as exhausted for now"
    stamp(rec, loc["last_at"] or NOW)
    return rec


def probe_opencode(_args):
    return probe_free("opencode-zen", OPENCODE_DB, {"opencode"}, None,
                      "local OpenCode store (requests and errors)")


def probe_kilo(_args):
    return probe_free("kilo", KILO_DB, {"kilo"}, KILO_ANON_PER_HOUR,
                      "local Kilo store (requests and errors)")


# ------------------------------------------------------------------ active
# Direct reads of each provider's own usage endpoint, verified 2026-11-06.
# Each token goes only to the provider that issued it. Tokens are never
# refreshed here: an expired token gives status "unknown" and the passive
# probe answers instead. Each call reads usage; none spends request quota.

CLAUDE_CREDS = "~/.claude/.credentials.json"
CODEX_AUTH = "~/.codex/auth.json"
AGY_TOKEN = "~/.gemini/antigravity-cli/antigravity-oauth-token"
UA = "capacity-watch/1.0"


def _http(url, headers, body=None, timeout=20):
    data = json.dumps(body).encode() if body is not None else None
    hdrs = {"User-Agent": UA, **headers}
    if data is not None:
        hdrs["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, None
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as e:
        return None, type(e).__name__


def _load(path):
    with open(os.path.expanduser(path)) as fh:
        return json.load(fh)


def active_claude(_args):
    rec = base("claude", source="GET api.anthropic.com/api/oauth/usage (active)")
    try:
        c = _load(CLAUDE_CREDS)["claudeAiOauth"]
    except (OSError, KeyError, ValueError):
        rec["reason"] = "no Claude Code OAuth credentials on this host"
        return rec
    if float(c.get("expiresAt") or 0) / 1000 < NOW:
        rec["reason"] = "Claude Code token expired; it refreshes on the next claude run"
        return rec
    code, b = _http("https://api.anthropic.com/api/oauth/usage",
                    {"Authorization": "Bearer " + c["accessToken"],
                     "anthropic-beta": "oauth-2025-04-20"})
    if code != 200 or not isinstance(b, dict):
        rec["reason"] = f"usage endpoint returned {code}"
        return rec
    for name in ("five_hour", "seven_day", "seven_day_opus", "seven_day_sonnet"):
        w = b.get(name)
        if isinstance(w, dict) and w.get("utilization") is not None:
            rec["windows"][name] = window(float(w["utilization"]) / 100,
                                          parse_iso(w.get("resets_at") or ""))
    extra = b.get("extra_usage") or {}
    rec["overage"] = {"enabled": extra.get("is_enabled"), "used": extra.get("used_credits")}
    stamp(rec, NOW)
    binding(rec)
    rec["status"], rec["confidence"] = "ok", "high"
    if "five_hour" not in rec["windows"]:
        rec["note"] = "no five-hour window reported: none open, or the plan has none"
    return rec


def active_codex(_args):
    rec = base("codex", source="GET chatgpt.com/backend-api/wham/usage (active)")
    try:
        t = _load(CODEX_AUTH)["tokens"]
    except (OSError, KeyError, ValueError):
        rec["reason"] = "no Codex ChatGPT login on this host"
        return rec
    code, b = _http("https://chatgpt.com/backend-api/wham/usage",
                    {"Authorization": "Bearer " + t["access_token"],
                     "ChatGPT-Account-Id": t.get("account_id", "")})
    if code != 200 or not isinstance(b, dict):
        rec["reason"] = f"usage endpoint returned {code}; a 401 means run codex once to refresh"
        return rec
    rl = b.get("rate_limit") or {}
    for key, name in (("primary_window", "five_hour"), ("secondary_window", "weekly")):
        w = rl.get(key)
        if isinstance(w, dict) and w.get("used_percent") is not None:
            rec["windows"][name] = window(float(w["used_percent"]) / 100, w.get("reset_at"),
                                          int(w.get("limit_window_seconds", 0)) // 60 or None)
    rec["plan"] = b.get("plan_type")
    rec["limit_reached"] = rl.get("limit_reached")
    stamp(rec, NOW)
    binding(rec)
    rec["status"], rec["confidence"] = "ok", "high"
    return rec


def active_agy(_args):
    rec = base("agy", source="POST cloudcode-pa v1internal:fetchAvailableModels (active, unofficial)")
    try:
        tok = _load(AGY_TOKEN)["token"]
    except (OSError, KeyError, ValueError):
        rec["reason"] = "no agy login on this host"
        return rec
    access = tok.get("access_token") if isinstance(tok, dict) else tok
    root = "https://cloudcode-pa.googleapis.com/v1internal:"
    hdr = {"Authorization": "Bearer " + str(access)}
    code, b = _http(root + "loadCodeAssist", hdr, {"metadata": {"ideType": "ANTIGRAVITY"}})
    if code != 200 or not isinstance(b, dict):
        rec["reason"] = f"loadCodeAssist returned {code}; a 401 means run agy once to refresh"
        return rec
    proj = b.get("cloudaicompanionProject")
    if isinstance(proj, dict):
        proj = proj.get("id")
    rec["plan"] = (b.get("paidTier") or b.get("currentTier") or {}).get("name")
    code, m = _http(root + "fetchAvailableModels", hdr, {"project": proj} if proj else {})
    if code != 200 or not isinstance(m, dict):
        rec["reason"] = f"fetchAvailableModels returned {code}"
        return rec
    for name, info in (m.get("models") or {}).items():
        q = (info or {}).get("quotaInfo") or {}
        if "remainingFraction" in q and q.get("resetTime"):
            rec["windows"][name] = window(round(1 - float(q["remainingFraction"]), 4),
                                          parse_iso(q["resetTime"]))
    stamp(rec, NOW)
    binding(rec)
    rec["status"], rec["confidence"] = "ok", "high"
    rec["note"] = "per-model fractions from an internal endpoint; it may change without notice"
    return rec


def active_opencode_go(_args):
    rec = base("opencode-go", source="GET opencode.ai/zen/go/v1/usage (active, unofficial)")
    keys = [os.environ.get("OPENCODE_GO_API_KEY")]
    try:
        keys.append(_load(OPENCODE_AUTH)["opencode-go"]["key"])
    except (OSError, KeyError, ValueError):
        pass
    last = None
    for k in [k for k in keys if k]:
        code, b = _http("https://opencode.ai/zen/go/v1/usage", {"Authorization": "Bearer " + k})
        last = code
        if code == 200 and isinstance(b, dict):
            for name, w in (b.get("usage") or {}).items():
                if isinstance(w, dict) and w.get("percent") is not None:
                    rec["windows"][name] = window(float(w["percent"]) / 100,
                                                  parse_iso(w.get("resetsAt") or ""))
                    rec["windows"][name]["status"] = w.get("status")
            stamp(rec, NOW)
            binding(rec)
            rec["status"], rec["confidence"] = "ok", "high"
            return rec
    rec["reason"] = (f"usage endpoint returned {last}; 401 api_key_expired means replace the key"
                     if last else "no OpenCode Go key in OPENCODE_GO_API_KEY or OpenCode's auth store")
    return rec


ACTIVE = {"claude": active_claude, "codex": active_codex, "agy": active_agy,
          "opencode-go": active_opencode_go}

PROBES = {"claude": probe_claude, "codex": probe_codex, "agy": probe_agy,
          "opencode-go": active_opencode_go,
          "openrouter": probe_openrouter, "opencode-zen": probe_opencode, "kilo": probe_kilo}


# ------------------------------------------------------------------ merge

def merge(paths):
    """Combine readings from several hosts. Subscription accounts are shared,
    so the true use is the highest use in the newest window seen anywhere."""
    best = {}
    for p in paths:
        with open(p) as fh:
            for line in fh:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                n = r.get("name")
                cur = best.get(n)
                key = (r.get("status") != "unknown", r.get("resets_at") or "",
                       r.get("used_fraction") if r.get("used_fraction") is not None else -1,
                       -(r.get("age_s") or 10 ** 9))
                if cur is None or key > cur[0]:
                    r.setdefault("merged_from", p)
                    best[n] = (key, r)
    for _, r in best.values():
        print(json.dumps(r))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--offline", action="store_true", help="no network calls")
    ap.add_argument("--only", help="comma-separated provider names")
    ap.add_argument("--net-max-age", type=int, default=300,
                    help="reuse a cached network reading this many seconds old (default 300)")
    ap.add_argument("--merge", nargs="+", metavar="JSONL", help="merge earlier outputs and exit")
    ap.add_argument("--active", action="store_true",
                    help="read claude, codex, agy and opencode-go from their own usage endpoints, "
                         "falling back to the passive reading when that fails")
    ap.add_argument("--record", metavar="JSONL",
                    help="also append every reading, stamped probed_at, to this file")
    args = ap.parse_args()
    if args.merge:
        merge(args.merge)
        return 0
    names = args.only.split(",") if args.only else list(PROBES)
    for n in names:
        if n not in PROBES:
            ap.error(f"unknown provider {n}")
    out = []
    for n in names:
        rec, why = None, None
        if args.active and not args.offline and n in ACTIVE:
            try:
                rec = ACTIVE[n](args)
            except Exception as e:  # fall back to the passive reading
                rec = base(n, reason=f"active probe error: {type(e).__name__}")
            if rec["status"] == "unknown" and PROBES[n] is not ACTIVE[n]:
                why = rec.get("reason")
                rec = None
        if rec is None:
            try:
                rec = PROBES[n](args)
            except Exception as e:  # one broken source must not hide the others
                rec = base(n, reason=f"probe error: {type(e).__name__}")
            if args.active and n in ACTIVE and PROBES[n] is not ACTIVE[n]:
                rec["active_failed"] = why
        out.append(rec)
        print(json.dumps(rec), flush=True)
    if args.record:
        os.makedirs(os.path.dirname(os.path.expanduser(args.record)), exist_ok=True)
        with open(os.path.expanduser(args.record), "a") as fh:
            stamp_all = iso(NOW)
            for rec in out:
                fh.write(json.dumps({"probed_at": stamp_all, **rec}) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
