#!/usr/bin/env python3
"""Phase 7: three-way join → status vector per project.

Joins: session intent (intents table) + spec lineage (canonical_prd_path)
+ repo reality (git history). Produces status_vectors rows.

Critical rule: proposer (Phase 6) and verifier (Phase 7) must be
different processes. This script is the verifier.

Usage:
    python scripts/07_three_way_join.py --db ~/.intent-archaeology/state.db
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.metric_vector import StatusVector, COMPONENTS, assert_no_anti_metric


def _grep(pattern: str, repo: str, fixed: bool = False) -> list[str]:
    """Return files matching. Empty list on any failure; never raises."""
    flags = ["-rl", "-F" if fixed else "-E", "-i", "--binary-files=without-match"]
    includes = ["--include=*.py", "--include=*.ts", "--include=*.tsx", "--include=*.js",
                "--include=*.jsx", "--include=*.go", "--include=*.rs", "--include=*.rb",
                "--include=*.java", "--include=*.kt", "--include=*.swift",
                "--include=*.ex", "--include=*.svelte", "--include=*.vue"]
    excludes = ["--exclude-dir=node_modules", "--exclude-dir=.git",
                "--exclude-dir=target", "--exclude-dir=dist", "--exclude-dir=build",
                "--exclude-dir=vendor", "--exclude-dir=.venv"]
    try:
        r = subprocess.run(["grep", *flags, pattern, repo, *includes, *excludes],
                           capture_output=True, text=True, timeout=20)
        return [l for l in r.stdout.splitlines() if l.strip()]
    except Exception:
        return []


# Suffixes stripped so an intent's wording matches the code's wording. Ordered
# longest-first because 'ations' must be tried before 'ation' and 's'.
_SUFFIXES = ("ations", "ation", "ising", "izing", "ings", "ing", "ers", "er",
             "ed", "es", "s")


def _stem(word: str) -> str:
    """Crude suffix stripper. limiting -> limit, limiter -> limit, caches -> cache."""
    for suf in _SUFFIXES:
        if word.endswith(suf) and len(word) - len(suf) >= 3:
            base = word[:-len(suf)]
            # restore a dropped 'e': caches -> cach -> cache
            if suf in ("es", "ing", "ed") and base.endswith(("ch", "sh", "s", "z", "v")):
                base += "e"
            return base
    return word


def _identifiers(feature_text: str) -> list[str]:
    """Content words from an intent, as the identifiers a coder would have used.

    'add rate limiting to the auth endpoint' yields rate, limiting, auth,
    endpoint. Those become identifier patterns like rate_limit, rateLimit,
    RateLimit, which is what actually appears in code, rather than the prose.
    """
    stop = {"add", "make", "use", "the", "and", "for", "with", "that", "this",
            "should", "must", "never", "always", "into", "from", "when", "then",
            "some", "more", "also", "just", "like", "need", "want", "have"}
    words = [w for w in re.findall(r"[a-zA-Z][a-zA-Z0-9]{2,}", feature_text.lower())
             if w not in stop]
    # Four-letter words are kept deliberately. auth, rate, user, cart, sync and
    # role are among the most common identifier stems in real code, and an
    # earlier version that required five characters missed every one of them.
    return words[:8]


def repo_has_feature(repo_path: str, feature_text: str) -> tuple[str, dict]:
    """Decide whether a repo implements an intent. Returns (verdict, evidence).

    Verdict is 'yes', 'partial', or 'no'. Evidence names what was found, so the
    judgement is inspectable rather than a bare label.

    Three signals, weighted by how much they actually prove:

      Symbol match. The intent's content words joined as an identifier
      (rate_limit, rateLimit, RateLimit) appearing in source. Far stronger than
      a bare keyword, because prose words appear everywhere and identifiers do
      not.

      Test correspondence. A test file whose name or contents reference the same
      identifiers. This is the only signal that demonstrates the feature works
      rather than merely exists, so it is what separates 'yes' from 'partial'.

      History. `git log -S` for the identifier shows when the concept entered the
      codebase, and catches features that exist but were named differently from
      the intent text.

    Keyword-grep alone is not used, because any word longer than four characters
    matches almost any repository and produces a confident yes for everything.
    """
    words = _identifiers(feature_text)
    if not words or len(feature_text) < 5:
        return "no", {"reason": "intent text too vague to check"}

    core = [_stem(w) for w in words[:4]]
    variants = set()
    for i in range(len(core)):
        for j in range(i + 1, min(i + 3, len(core) + 1)):
            parts = core[i:j]
            if len(parts) < 2:
                continue
            variants.add("_".join(parts))
            variants.add(parts[0] + "".join(p.capitalize() for p in parts[1:]))
            variants.add("".join(p.capitalize() for p in parts))
    # Single words only when distinctive enough that a bare match means something.
    variants |= {w for w in core if len(w) > 6}
    variants = {v for v in variants if len(v) > 5}

    if not variants:
        return "no", {"reason": "no usable identifier derived", "words": core}

    # Stems match any suffix, so the stem 'rate_limit' finds rate_limit,
    # rate_limiter, rate_limiting and RateLimiterConfig. Prose and code almost
    # never agree on inflection: an intent says "add rate limiting" and the code
    # defines RateLimiter. Matching on stems is what closes that gap.
    pattern = "|".join(re.escape(v) + r"\w*" for v in sorted(variants))
    hits = _grep(pattern, repo_path)
    if not hits:
        hist = []
        try:
            for v in sorted(variants)[:3]:
                r = subprocess.run(["git", "-C", repo_path, "log", "-S", v,
                                    "--oneline", "-3"],
                                   capture_output=True, text=True, timeout=15)
                if r.returncode == 0 and r.stdout.strip():
                    hist.extend(r.stdout.strip().splitlines())
        except Exception:
            pass
        if hist:
            return "partial", {"symbol_hits": 0, "history": hist[:3],
                               "note": "concept appears in history but not in current code"}
        return "no", {"symbol_hits": 0, "identifiers": sorted(variants)[:5]}

    tests = [h for h in hits
             if re.search(r"(^|/)(tests?|spec|__tests__)/|(_test|_spec|\.test|\.spec)\.",
                          h, re.I)]
    evidence = {"symbol_hits": len(hits), "files": hits[:5],
                "identifiers": sorted(variants)[:5], "test_files": tests[:3]}
    return ("yes" if tests else "partial"), evidence


def compute_vector(project: dict, intents: list[dict], tranche_id: int) -> StatusVector:
    """Compute status vector for one project."""
    vec = StatusVector(project_id=project["id"], tranche_id=tranche_id)
    for it in intents:
        # Order matters. An intent the user explicitly cut is abandoned no matter
        # what the repo contains, and an intent a later instruction replaced is
        # superseded no matter what the repo contains. Checking the repo first
        # would report deliberate decisions as build failures, which is the exact
        # error the status vector exists to prevent.
        if it["type"] in ("scope-cut", "scope.cut"):
            vec.abandoned += 1
            continue
        if it.get("superseded_by"):
            vec.superseded += 1
            continue

        repo_state, evidence = repo_has_feature(project["path"], it["summary"])
        it["repo_evidence"] = evidence

        if repo_state == "yes":
            # Built and covered by a test. The only category with demonstrated
            # behaviour rather than merely present code.
            vec.completed += 1
        elif repo_state == "partial":
            # Code exists but nothing demonstrates it works, or the concept is in
            # history but not current source. Drift lives here: if the intent was
            # a correction and the code still matches what was corrected away,
            # that is drift rather than progress.
            if it["type"].startswith("correction"):
                vec.drifted += 1
            else:
                vec.in_progress += 1
        else:
            vec.not_begun += 1
    return vec.normalize()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", required=True)
    ap.add_argument("--tranche", type=int, help="Limit to a specific tranche_id")
    args = ap.parse_args()

    with sqlite3.connect(args.db) as conn:
        where = "WHERE lifecycle NOT IN ('proposed', NULL)"
        projects = conn.execute(
            f"SELECT id, name, path, era, lifecycle FROM projects {where}"
        ).fetchall()
        if not projects:
            print("WARN: no projects with confirmed lifecycle. Run 04_derive_lifecycle.py first.", file=sys.stderr)
            return 1

        # Use latest tranche if not specified
        if args.tranche:
            tranche_id = args.tranche
        else:
            row = conn.execute(
                "SELECT id FROM tranches WHERE status = 'completed' ORDER BY completed_at DESC LIMIT 1"
            ).fetchone()
            if not row:
                print("WARN: no completed tranches. Run 05_extract_prompts.py first.", file=sys.stderr)
                return 1
            tranche_id = row[0]

        for pid, name, path, era, lifecycle in projects:
            intents = conn.execute(
                "SELECT id, type, summary FROM intents WHERE project_id = ? AND tranche_id = ?",
                (pid, tranche_id),
            ).fetchall()
            if not intents:
                print(f"  {name}: no intents, skipping", file=sys.stderr)
                continue
            intent_dicts = [{"id": r[0], "type": r[1], "summary": r[2]} for r in intents]
            project_dict = {"id": pid, "path": path, "era": era, "lifecycle": lifecycle}
            vec = compute_vector(project_dict, intent_dicts, tranche_id)
            # Anti-metric check
            assert_no_anti_metric(vec.to_dict())
            conn.execute(
                """INSERT OR REPLACE INTO status_vectors
                   (project_id, tranche_id, completed, in_progress, drifted,
                    superseded, abandoned, not_begun)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (vec.project_id, vec.tranche_id, vec.completed, vec.in_progress,
                 vec.drifted, vec.superseded, vec.abandoned, vec.not_begun),
            )
            print(f"  {name}: {vec.summary_line()}", file=sys.stderr)
        conn.commit()
    print(f"OK: status vectors computed (tranche {tranche_id})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
