#!/usr/bin/env python3
"""free-catalog: list every zero-cost or contributor-tier model we can reach,
grade it against the approved quality floor, and flag what changed.

Sources (read only, nothing is spent):
  opencode-zen   GET https://opencode.ai/zen/v1/models  (key: OPENCODE_ZEN_API_KEY or OPENCODE_API_KEY)
  openrouter     GET https://openrouter.ai/api/v1/models (no key)
  kilo           `kilo models --verbose` when the kilo CLI is installed; this
                 also lists opencode-go, nvidia, chutes and other providers the
                 CLI knows, with their per-token cost
Quality: ARDF priors scores (max over effort levels) from
  /home/cheta/code/ardf/ardf/data/current-comparison.csv

A model is
  capable      scored at or above the floor (the lowest max score among the
               approved free lanes, see APPROVED)
  below-floor  scored under the floor; never route Living Documents or intent
               work to it (operator rule: no low-tier models)
  unscored     no ARDF score yet (stealth and new models); trial before use

Data-sharing tiers (contributor, stealth, free tiers that train on prompts)
are wanted, not penalised (operator direction 2026-11-06). They still receive
only redacted text, never credentials or private exports.

Usage:
  free-catalog.py --out DIR      write DIR/catalog-<UTC date>.json and DIR/latest.md,
                                 and diff against DIR/catalog-previous.json
"""
import argparse
import csv
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import urllib.request

ARDF_CSV = "/home/cheta/code/ardf/ardf/data/current-comparison.csv"
APPROVED = ["deepseek-v4.1-flash", "glm-5.3-flash"]  # crouton-alpha is approved but unscored
UA = {"User-Agent": "capacity-watch/1.0"}
SHARING = re.compile(r"contributor|stealth|alpha|cloaked|big-pickle|iceman|glyph", re.I)


def norm(model_id):
    m = model_id.split("/")[-1].lower()
    m = re.sub(r"(:free|-free|:batch|-contributor)$", "", m)
    m = m.replace("-contributor", "")
    return re.sub(r"[^a-z0-9]", "", m)


def ardf_scores(path=ARDF_CSV):
    best = {}
    try:
        with open(path) as fh:
            for r in csv.DictReader(fh):
                ident = r["identity"].split("@")[0]
                try:
                    s = float(r.get("priors_score") or r.get("ardf_score") or "nan")
                except ValueError:
                    continue
                if s == s and s > best.get(ident, (-1, ""))[0]:
                    best[ident] = (s, r["name"])
    except OSError:
        pass
    return best


def score_for(model_id, scores):
    n = norm(model_id)
    if len(n) < 4:
        return None
    # Exact match first; then the longest scored name the model id extends
    # (glm-5.3-flash-free -> glm53flash); only then a scored variant of a bare
    # id. kimi-k3 must not inherit kimi-k3.1's score.
    if n in scores:
        k = n
    else:
        under = [k for k in scores if n.startswith(k) and len(k) >= 4]
        over = [k for k in scores if k.startswith(n)]
        if under:
            k = max(under, key=len)
        elif over:
            k = min(over, key=len)
        else:
            return None
    return {"ardf_identity": k, "score": round(scores[k][0], 2)}


NOT_CHAT = re.compile(r"whisper|tts|orpheus|voice|flux|embed|rerank|guard|safety|image|video|"
                      r"detector|bevformer|sparsedrive|streampetr|cosmos|paligemma|lyria|"
                      r"speaker|diffusion|allam", re.I)
# Credential each route needs, by environment variable or auth store entry.
ACCESS = {"opencode/": "OPENCODE_ZEN_API_KEY", "opencode-go/": "OPENCODE_GO_API_KEY",
          "openrouter/": "OPENROUTER_API_KEY", "nvidia/": "NVIDIA_API_KEY",
          "chutes/": "CHUTES_API_KEY", "groq/": "GROQ_API_KEY", "cerebras/": "CEREBRAS_API_KEY",
          "ollama-cloud/": "OLLAMA_API_KEY", "google/": "GEMINI_API_KEY", "kilo/": "kilo login"}


def access(route):
    for prefix, need in ACCESS.items():
        if route.startswith(prefix):
            if need == "kilo login":
                return os.path.exists(os.path.expanduser("~/.local/share/kilo/auth.json"))
            return bool(os.environ.get(need))
    return False


def get(url, headers=None):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def from_zen():
    key = os.environ.get("OPENCODE_ZEN_API_KEY") or os.environ.get("OPENCODE_API_KEY")
    if not key:
        return [], "no OPENCODE_ZEN_API_KEY"
    d = get("https://opencode.ai/zen/v1/models", {"Authorization": "Bearer " + key})
    return [{"route": "opencode/" + m["id"], "cost_in": 0 if m["id"].endswith("-free") else None,
             "cost_out": 0 if m["id"].endswith("-free") else None, "context": None}
            for m in d.get("data", [])], None


def from_openrouter():
    d = get("https://openrouter.ai/api/v1/models")
    out = []
    for m in d.get("data", []):
        p = m.get("pricing") or {}
        try:
            ci, co = float(p.get("prompt", "nan")) * 1e6, float(p.get("completion", "nan")) * 1e6
        except ValueError:
            continue
        out.append({"route": "openrouter/" + m["id"], "cost_in": round(ci, 4), "cost_out": round(co, 4),
                    "context": m.get("context_length")})
    return out, None


def from_kilo():
    exe = shutil.which("kilo")
    if not exe:
        return [], "kilo CLI not installed"
    txt = subprocess.run([exe, "models", "--verbose"], capture_output=True, text=True,
                         timeout=120).stdout
    txt = re.sub(r"\x1b\[[0-9;]*m", "", txt)
    out = []
    for block in re.split(r"\n(?=[a-z0-9-]+/[^\n{]+\n\{)", "\n" + txt):
        head, _, js = block.strip().partition("\n")
        try:
            d = json.loads(js)
        except ValueError:
            continue
        c = d.get("cost") or {}
        out.append({"route": head.strip(), "cost_in": c.get("input"), "cost_out": c.get("output"),
                    "context": (d.get("limit") or {}).get("context")})
    return out, None


def keep(m):
    r = m["route"]
    if NOT_CHAT.search(r):
        return False
    zero = m["cost_in"] == 0 and m["cost_out"] == 0
    return zero or "contributor" in r or r.endswith("-free") or r.endswith(":free") \
        or r.startswith("opencode-go/")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    scores = ardf_scores()
    floor = min((score_for(m, scores) or {"score": 99})["score"] for m in APPROVED)
    rows, notes = {}, {}
    for name, fn in (("opencode-zen", from_zen), ("openrouter", from_openrouter), ("kilo", from_kilo)):
        try:
            got, why = fn()
        except Exception as e:  # one source failing must not hide the rest
            got, why = [], f"{type(e).__name__}"
        if why:
            notes[name] = why
        for m in got:
            if keep(m):
                rows.setdefault(m["route"], m)
    for m in rows.values():
        s = score_for(m["route"], scores)
        m.update(s or {})
        m["tier"] = ("unscored" if not s else "capable" if s["score"] >= floor else "below-floor")
        m["subscription"] = m["route"].startswith("opencode-go/")
        m["data_sharing"] = bool(SHARING.search(m["route"]))
        m["have_access"] = access(m["route"])
    stamp = dt.datetime.now(dt.timezone.utc)
    cat = {"generated_at": stamp.strftime("%Y-%m-%dT%H:%M:%SZ"), "floor": floor,
           "approved": APPROVED, "source_notes": notes,
           "models": sorted(rows.values(), key=lambda m: (-(m.get("score") or 0), m["route"]))}
    prev_path = os.path.join(a.out, "catalog-previous.json")
    prev = set()
    if os.path.exists(prev_path):
        with open(prev_path) as fh:
            prev = {m["route"] for m in json.load(fh).get("models", [])}
    now = {m["route"] for m in cat["models"]}
    cat["added"] = sorted(now - prev) if prev else []
    cat["removed"] = sorted(prev - now) if prev else []
    path = os.path.join(a.out, f"catalog-{stamp:%Y-%m-%d}.json")
    with open(path, "w") as fh:
        json.dump(cat, fh, indent=1)
    shutil.copyfile(path, prev_path)
    with open(os.path.join(a.out, "latest.md"), "w") as fh:
        fh.write(f"# Free and contributor models, {cat['generated_at']}\n\n")
        fh.write(f"Quality floor: ARDF {floor} (lowest approved free lane). "
                 f"Sources skipped: {notes or 'none'}.\n\n")
        for tier in ("capable", "unscored", "below-floor"):
            ms = [m for m in cat["models"] if m["tier"] == tier]
            fh.write(f"## {tier} ({len(ms)})\n\n")
            for m in ms:
                tag = []
                if m["subscription"]:
                    tag.append("Go plan")
                if m["data_sharing"]:
                    tag.append("data-sharing")
                if not m["have_access"]:
                    tag.append("NO-CREDENTIAL")
                fh.write(f"- {m['route']}  score {m.get('score', '-')}  "
                         f"ctx {m.get('context') or '-'}  {' '.join(tag)}\n")
            fh.write("\n")
        if cat["added"] or cat["removed"]:
            fh.write(f"## Changed since last run\n\nAdded: {cat['added']}\n\nRemoved: {cat['removed']}\n")
    print(json.dumps({"path": path, "models": len(cat["models"]), "floor": floor,
                      "by_tier": {t: sum(m["tier"] == t for m in cat["models"])
                                  for t in ("capable", "unscored", "below-floor")},
                      "added": len(cat["added"]), "notes": notes}))


if __name__ == "__main__":
    main()
