#!/usr/bin/env python3
"""strata-validate.py

Enforces the STRATA rules against an artifact tree. Exits non-zero on any
violation so it can gate a build. This is deliberately a hard failure, not a
warning: separation that only warns is separation that decays.

Usage:
    python3 strata-validate.py <path-to-strata-project-dir>
    python3 strata-validate.py --audit <file> [<file>...]   # any spec artifacts
    python3 strata-validate.py --explain                    # what each check means

Checks:
  1. Separation   - no technology tokens in intent.md or spec.md
  2. Eval binding - every SPEC- clause carries [EVAL-...] AND that eval resolves
                    to a manifest stored OUTSIDE the build tree
  3. Testability  - no spec clause written in non-evaluable language
  4. Fidelity     - spec is thick enough to drive deterministic behavior
  5. Drift        - every spec clause is cited by context; no dangling citations
  6. Continuity   - ledger/ledger.md and ledger/standing.md exist and are real
  7. Honesty      - substrate.md declares a level S0..S5
  8. Authorship   - context.md exists (system-derived layer present)

Why 2 checks the manifest and not just the tag: an eval tag that resolves to
nothing is a spec clause that lies with confidence. Checking only the tag makes
`[EVAL-FAKE-1]` pass, which is the exact failure the eval layer exists to stop.
Evals live outside the tree so the implementing agent cannot read or game them.

--audit runs the file-level checks (1, 3, 4) against arbitrary spec documents,
including SpecKit/OpenSpec/Kiro output that has no STRATA tree. Use it to
measure an existing corpus before migrating it.

The technology denylist is a curated heuristic, not a language model. It cannot
catch every leak. Extend it per domain: drop a `tech-tokens.txt` (one token per
line, `#` for comments) beside the artifacts or in the project root and it is
merged automatically. A denylist that never fires is not a passing build; it is
an unarmed check.
"""

import re
import sys
from pathlib import Path

# Curated denylist. Word-boundary, case-insensitive. A hit in intent.md or
# spec.md means an implementation concern leaked into a layer it does not own.
TECH_TOKENS = [
    # web frameworks / runtimes
    "react", "svelte", "vue", "angular", "next.js", "nextjs", "nuxt",
    "node.js", "nodejs", "express", "hono", "fastify", "django", "flask",
    "rails", "spring boot", "fastapi", "htmx", "jquery",
    # languages / runtimes -- the most common leak, and absent before 2.0
    "python", "typescript", "javascript", "rust", "golang", " java ",
    "kotlin", "swiftui", "ruby", "php", "bash script", "powershell",
    # datastores
    "postgres", "postgresql", "mysql", "mariadb", "sqlite", "mongodb",
    "dynamodb", "redis", "kafka", "rabbitmq", "duckdb",
    "pgvector", "qdrant", "pinecone", "elasticsearch", "kuzudb", "neo4j",
    # infra / hosting
    "graphql", "grpc", "kubernetes", "docker", "terraform",
    "cloudflare workers", "vercel", "netlify", "aws lambda", "s3 bucket",
    "ec2", "gcp", "azure", "systemd", "nginx",
    # frontend / viz / styling
    "tailwind", "bootstrap", "echarts", "chart.js", "chartjs", "plotly",
    "d3.js", "recharts", "highcharts", "matplotlib",
    # observability -- named in this workspace's own leaked requirements
    "grafana", "prometheus", "datadog", "opentelemetry", "sentry",
    # test tooling
    "pytest", "jest", "vitest", "playwright", "cypress", "junit",
    # architecture shapes the user should not be choosing
    "microservice", "monolith", "serverless function", "message queue",
]

# Phrases that cannot be converted into a pass/fail evaluation. A spec clause
# containing one is intent or noise wearing a spec's clothing.
NON_EVALUABLE = [
    "user-friendly", "user friendly", "intuitive", "seamless", "robust",
    "scalable", "flexible", "easy to use", "as needed", "as appropriate",
    "etc.", "and so on", "where possible", "if necessary", "reasonable",
    "good performance", "fast enough", "modern", "clean", "elegant",
    "best practice", "industry standard", "properly", "correctly handle",
]

# A spec thin enough to be a headline rather than a contract. The article's
# Symphony reference point is ~1,400 lines of exhaustive coverage; this is not
# that bar, it is the floor below which the spec cannot drive determinism.
MIN_SPEC_CLAUSES = 8

# SPEC- is STRATA's own form. FR-/NFR- are what SpecKit, OpenSpec and Kiro
# emit, and --audit has to see those or it cannot measure an existing corpus.
SPEC_CLAUSE_RE = re.compile(r"^[ \t]*[-*]?[ \t]*\**((?:SPEC|FR|NFR)-\d+)\b", re.MULTILINE)
EVAL_TAG_RE = re.compile(r"\[(EVAL-[A-Za-z0-9_-]+)\]")
LEVEL_RE = re.compile(r"^[ \t]*S[0-5]\b", re.MULTILINE)
CITATION_RE = re.compile(r"\b((?:SPEC|FR|NFR)-\d+)\b")


def load_extra_tokens(*dirs: Path) -> list[str]:
    """Merge a domain denylist if one is present. Keeps the check armed."""
    extra: list[str] = []
    for d in dirs:
        f = d / "tech-tokens.txt"
        if f.is_file():
            for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.split("#", 1)[0].strip().lower()
                if line:
                    extra.append(line)
    return extra


def tech_hits(text: str, tokens: list[str]) -> list[str]:
    low = text.lower()
    hits = []
    for token in tokens:
        pat = r"(?<![a-z0-9])" + re.escape(token.strip()) + r"(?![a-z0-9])"
        if re.search(pat, low):
            hits.append(token.strip())
    return hits


def spec_clauses(text: str) -> list[tuple[str, str]]:
    """Return (clause_id, full_line) for every SPEC- clause."""
    out = []
    for m in SPEC_CLAUSE_RE.finditer(text):
        start = text.rfind("\n", 0, m.start()) + 1
        end = text.find("\n", m.start())
        out.append((m.group(1), text[start: end if end != -1 else len(text)]))
    return out


def check_separation(text: str, label: str, tokens: list[str], errors: list):
    for hit in tech_hits(text, tokens):
        errors.append(
            f"[separation] technology token '{hit}' found in {label}; "
            f"implementation concerns belong in the derived context layer, not {label}"
        )


def check_testability(clauses: list[tuple[str, str]], label: str, errors: list):
    for cid, line in clauses:
        low = line.lower()
        for phrase in NON_EVALUABLE:
            if phrase in low:
                errors.append(
                    f"[testability] {cid} in {label} contains non-evaluable language "
                    f"'{phrase}'; a clause that cannot become a pass/fail eval is "
                    f"intent or noise, not spec"
                )
                break


def check_fidelity(clauses: list[tuple[str, str]], label: str, errors: list):
    if len(clauses) < MIN_SPEC_CLAUSES:
        errors.append(
            f"[fidelity] {label} declares only {len(clauses)} SPEC- clause(s); "
            f"below {MIN_SPEC_CLAUSES} a specification is a headline, not a contract. "
            f"Either the scope is smaller than a project or the spec is underwritten"
        )


def check_eval_resolution(clauses, spec_label, root: Path, errors: list):
    """Every eval tag must resolve to a manifest stored OUTSIDE the build tree."""
    tagged, untagged = {}, []
    for cid, line in clauses:
        m = EVAL_TAG_RE.search(line)
        if m:
            tagged[cid] = m.group(1)
        else:
            untagged.append((cid, line.strip()[:60]))

    for cid, snippet in untagged:
        errors.append(f"[eval-binding] {cid} has no [EVAL-...] tag: '{snippet}'")

    if not tagged:
        return

    # Evals live outside the tree so the implementing agent cannot game them.
    candidates = [
        root.parent / "evals" / "evals.md",
        root.parent / "evals" / "evals.json",
        root.parent / f"{root.name}-evals.md",
    ]
    manifest = next((c for c in candidates if c.is_file()), None)

    inside = root / "evals"
    if manifest is None:
        where = " or ".join(str(c) for c in candidates)
        extra = ""
        if inside.exists():
            extra = (f" An evals directory exists INSIDE the tree at {inside}; "
                     f"that is worse than missing, because the implementing agent "
                     f"can read it and optimize against the test.")
        errors.append(
            f"[eval-binding] {len(tagged)} clause(s) carry eval tags but no eval "
            f"manifest was found outside the build tree (looked for {where})."
            f"{extra} An eval tag that resolves to nothing is a clause that lies "
            f"with confidence"
        )
        return

    body = manifest.read_text(encoding="utf-8", errors="replace")
    for cid, eid in sorted(tagged.items()):
        if eid not in body:
            errors.append(
                f"[eval-binding] {cid} cites {eid}, which does not exist in "
                f"{manifest.name}; the binding is dangling"
            )


def check_drift(clauses, context_text: str | None, errors: list):
    """Spec and context must stay in contact. Silence in either direction is drift."""
    if context_text is None:
        return
    cited = set(CITATION_RE.findall(context_text))
    declared = {cid for cid, _ in clauses}

    for cid in sorted(declared - cited):
        errors.append(
            f"[drift] {cid} is declared in spec but cited by no decision in the "
            f"context layer; either the architecture does not support it or the "
            f"clause is dead"
        )
    for cid in sorted(cited - declared):
        errors.append(
            f"[drift] context cites {cid}, which no longer exists in spec; "
            f"a drifted citation lies with confidence"
        )


def report(errors: list, passed_msg: str) -> int:
    if errors:
        print(f"STRATA validation FAILED with {len(errors)} violation(s):\n")
        for e in errors:
            print(f"  - {e}")
        print("\nFix every violation before the build proceeds.")
        return 1
    print(passed_msg)
    return 0


# Which layer a file belongs to, inferred from its name. This matters: the
# derived layer is SUPPOSED to name technologies. Flagging design.md or plan.md
# for containing "python" would be a false positive, and a check that cries wolf
# gets switched off, which is worse than no check at all.
HUMAN_LAYER = ("intent", "spec", "requirements", "prd", "srs")
DERIVED_LAYER = ("context", "design", "plan", "architecture", "adr", "research",
                 "data-model", "quickstart", "tasks")


def infer_layer(name: str) -> str:
    stem = name.lower().removesuffix(".md")
    for k in DERIVED_LAYER:
        if k in stem:
            return "derived"
    for k in HUMAN_LAYER:
        if k in stem:
            return "human"
    return "unknown"


def audit_files(paths: list[str]) -> int:
    """File-level checks against arbitrary spec artifacts, STRATA tree or not."""
    errors: list[str] = []
    notes: list[str] = []
    seen_any = False
    for p in paths:
        f = Path(p)
        if not f.is_file():
            print(f"error: not a file: {f}", file=sys.stderr)
            return 2
        seen_any = True
        text = f.read_text(encoding="utf-8", errors="replace")
        layer = infer_layer(f.name)
        tokens = TECH_TOKENS + load_extra_tokens(f.parent, f.parent.parent)

        if layer == "human":
            check_separation(text, f.name, tokens, errors)
        elif layer == "derived":
            n = len(tech_hits(text, tokens))
            notes.append(f"{f.name}: derived layer, {n} technology token(s) — expected here, not a violation")
        else:
            n = len(tech_hits(text, tokens))
            notes.append(f"{f.name}: layer could not be inferred from filename; "
                         f"{n} technology token(s) present, separation NOT checked")

        clauses = spec_clauses(text)
        if clauses and layer != "derived":
            check_testability(clauses, f.name, errors)
            check_fidelity(clauses, f.name, errors)

    if not seen_any:
        return 2
    if notes:
        print("Notes:")
        for n in notes:
            print(f"  · {n}")
        print()
    return report(errors, "AUDIT PASSED: no layer leakage, no non-evaluable clauses.")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    if args[0] == "--explain":
        print(__doc__)
        return 0
    if args[0] == "--audit":
        if len(args) < 2:
            print("usage: strata-validate.py --audit <file> [<file>...]", file=sys.stderr)
            return 2
        return audit_files(args[1:])

    root = Path(args[0]).resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2

    errors: list[str] = []
    intent = root / "intent.md"
    spec = root / "spec.md"
    context = root / "context.md"
    substrate = root / "substrate.md"
    ledger = root / "ledger" / "ledger.md"
    standing = root / "ledger" / "standing.md"

    tokens = TECH_TOKENS + load_extra_tokens(root, root.parent)

    intent_text = spec_text = context_text = None
    for path, label in ((intent, "intent.md"), (spec, "spec.md")):
        if not path.exists():
            errors.append(f"[structure] missing required artifact: {label}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        check_separation(text, label, tokens, errors)
        if label == "intent.md":
            intent_text = text
        else:
            spec_text = text

    if not context.exists():
        errors.append("[authorship] missing context.md; the system-derived implementation layer is required")
    else:
        context_text = context.read_text(encoding="utf-8", errors="replace")

    if spec_text is not None:
        clauses = spec_clauses(spec_text)
        check_testability(clauses, "spec.md", errors)
        check_fidelity(clauses, "spec.md", errors)
        check_eval_resolution(clauses, "spec.md", root, errors)
        check_drift(clauses, context_text, errors)

    for f, label in ((ledger, "ledger/ledger.md"), (standing, "ledger/standing.md")):
        if not f.exists():
            errors.append(f"[continuity] missing {label}; continuity is not optional")
        elif len(f.read_text(encoding="utf-8", errors="replace").strip()) < 40:
            errors.append(f"[continuity] {label} is effectively empty; the spine must carry real content")

    if not substrate.exists():
        errors.append("[honesty] missing substrate.md; a declared substrate level is required")
    else:
        st = substrate.read_text(encoding="utf-8", errors="replace")
        seg = st.split("## Declared level", 1)
        if len(seg) < 2 or not LEVEL_RE.search(seg[1][:120]):
            errors.append("[honesty] substrate.md does not declare a level S0..S5 under '## Declared level'")

    return report(
        errors,
        "STRATA validation PASSED: layers separated, clauses evaluable and bound to "
        "external evals, spec in contact with context, continuity present, level declared.",
    )


if __name__ == "__main__":
    raise SystemExit(main())
