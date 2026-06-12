#!/usr/bin/env python3
"""strata-validate.py

Enforces the six STRATA rules against an artifact tree. Exits non-zero on any
violation so it can gate a build. This is deliberately a hard failure, not a
warning: separation that only warns is separation that decays.

Usage:
    python3 strata-validate.py <path-to-strata-project-dir>

Checks:
  1. Separation   - no technology tokens in intent.md or spec.md
  2. Eval binding - every SPEC- clause line carries an [EVAL-...] tag
  3. Continuity   - ledger/ledger.md and ledger/standing.md exist and are non-trivial
  4. Honesty      - substrate.md declares a level S0..S5
  5. Authorship   - context.md exists (system-derived layer present)
  6. Structure    - intent.md and spec.md exist

The technology denylist is intentionally a curated heuristic. It catches the
common offenders that signal a fused layer. Extend TECH_TOKENS for a domain.
"""

import re
import sys
from pathlib import Path

# Curated denylist. Word-boundary, case-insensitive. A hit in intent.md or
# spec.md means an implementation concern leaked into a layer it does not own.
TECH_TOKENS = [
    "react", "svelte", "vue", "angular", "next.js", "nextjs", "nuxt",
    "node.js", "nodejs", "express", "hono", "fastify", "django", "flask",
    "rails", "spring boot", "postgres", "postgresql", "mysql", "mariadb",
    "sqlite", "mongodb", "dynamodb", "redis", "kafka", "rabbitmq",
    "graphql", "grpc", "kubernetes", "docker", "terraform", "cloudflare workers",
    "vercel", "netlify", "aws lambda", "s3 bucket", "ec2", "gcp", "azure",
    "tailwind", "bootstrap", "typescript", "rust", "golang", " java ",
    "kotlin", "swiftui", "microservice", "monolith", "serverless function",
    "pgvector", "qdrant", "pinecone", "elasticsearch", "kuzudb", "neo4j",
]

# [ \t] not \s: \s includes newline, which would let the anchor slide onto a
# blank line and slice an empty clause (a false positive).
SPEC_CLAUSE_RE = re.compile(r"^[ \t]*SPEC-\d+\b", re.MULTILINE)
EVAL_TAG_RE = re.compile(r"\[EVAL-[A-Za-z0-9_-]+\]")
LEVEL_RE = re.compile(r"^[ \t]*S[0-5]\b", re.MULTILINE)


def fail(msg, errors):
    errors.append(msg)


def check_layer_purity(path: Path, label: str, errors):
    if not path.exists():
        fail(f"[structure] missing required artifact: {label}", errors)
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    low = text.lower()
    for token in TECH_TOKENS:
        # word-boundary-ish: require non-alnum or string edge around the token
        pat = r"(?<![a-z0-9])" + re.escape(token.strip()) + r"(?![a-z0-9])"
        if re.search(pat, low):
            fail(
                f"[separation] technology token '{token.strip()}' found in {label}; "
                f"implementation concerns belong in context.md, not {label}",
                errors,
            )
    return text


def main():
    if len(sys.argv) != 2:
        print("usage: python3 strata-validate.py <path-to-strata-project-dir>", file=sys.stderr)
        return 2

    root = Path(sys.argv[1]).resolve()
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

    # Rule 1 + 6: separation and structure for the human-authored layers.
    check_layer_purity(intent, "intent.md", errors)
    spec_text = check_layer_purity(spec, "spec.md", errors)

    # Rule 5: the system-derived layer must be present.
    if not context.exists():
        fail("[authorship] missing context.md; the system-derived implementation layer is required", errors)

    # Rule 2: every spec clause must be eval-bound.
    if spec_text is not None:
        for m in SPEC_CLAUSE_RE.finditer(spec_text):
            line_start = spec_text.rfind("\n", 0, m.start()) + 1
            line_end = spec_text.find("\n", m.start())
            line = spec_text[line_start: line_end if line_end != -1 else len(spec_text)]
            if not EVAL_TAG_RE.search(line):
                clause = line.strip()[:60]
                fail(f"[eval-binding] spec clause without an [EVAL-...] tag: '{clause}'", errors)

    # Rule 3: continuity must exist and not be empty.
    for f, label in ((ledger, "ledger/ledger.md"), (standing, "ledger/standing.md")):
        if not f.exists():
            fail(f"[continuity] missing {label}; continuity is not optional", errors)
        elif len(f.read_text(encoding="utf-8", errors="replace").strip()) < 40:
            fail(f"[continuity] {label} is effectively empty; the spine must carry real content", errors)

    # Rule 4: honesty file must declare a level.
    if not substrate.exists():
        fail("[honesty] missing substrate.md; a declared substrate level is required", errors)
    else:
        st = substrate.read_text(encoding="utf-8", errors="replace")
        seg = st.split("## Declared level", 1)
        if len(seg) < 2 or not LEVEL_RE.search(seg[1][:120]):
            fail("[honesty] substrate.md does not declare a level S0..S5 under '## Declared level'", errors)

    if errors:
        print(f"STRATA validation FAILED with {len(errors)} violation(s):\n")
        for e in errors:
            print(f"  - {e}")
        print("\nFix every violation before the build proceeds.")
        return 1

    print("STRATA validation PASSED: layers separated, clauses eval-bound, continuity present, level declared.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
