#!/usr/bin/env python3
"""strata-validate.py

Enforces the STRATA rules against an artifact tree. Exits non-zero on any
violation so it can gate a build. This is deliberately a hard failure, not a
warning: separation that only warns is separation that decays.

Usage:
    python3 strata-validate.py <project-dir> [--evals PATH] [--no-harvest] [--trace]
    python3 strata-validate.py --audit <file> [<file>...] [--no-harvest]
    python3 strata-validate.py --depth <source-file> [...] --against <output-file> [...]
    python3 strata-validate.py --explain

    <project-dir> holds intent.md, spec.md (or requirements.md), context.md
    (or design.md), substrate.md and ledger/. Eval store: --evals PATH, else
    $STRATA_EVALS, else ../evals/evals.md|json, ../<slug>-evals.md, or
    ~/.strata/evals/<slug>/evals.md. The store must sit outside the git
    repository that contains the project, or the implementing agent can read it.

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

Self-arming denylist (v2.1): technology tokens are harvested from the derived
layer (context/design/plan files, or any file whose frontmatter says
`layer: derived`): backtick spans, CamelCase names and letter+digit names such
as WebGPU, IndexedDB or SAM2. Whatever the architecture names is, by
definition, a technology for this project, so a hit in intent or spec is a
leak even when the static list has never heard of it. Platform and device
names users legitimately mention (iPhone, Android, macOS) are allowed; extend
with `layer-allow.txt` beside the artifacts. Disable with --no-harvest.

Layer inference: a `layer: human|derived` frontmatter field wins; otherwise
the filename decides; unknown files are reported, not silently passed.

--depth compares requirement-like statements (lines with SHALL, MUST, SHOULD
or an ID such as FR-001) in source material against generated artifacts and
fails when the output keeps fewer than 90%: a drop is lost content, not
successful summarization.

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
    # browser platform APIs (v2.1)
    "indexeddb", "localstorage", "sessionstorage", "webgpu", "webgl", "webgl2",
    "webassembly", "wasm", "service worker", "web worker", "websocket", "webrtc",
    "offscreencanvas", "getusermedia", "pwa manifest",
    # ML and AI runtimes / models (v2.1)
    "onnx", "onnx runtime", "pytorch", "tensorflow", "tflite", "mediapipe",
    "transformers.js", "hugging face", "huggingface", "llama.cpp", "ollama",
    "openai api", "anthropic api", "langchain", "llamaindex", "segment anything",
    # mobile and desktop shells (v2.1)
    "react native", "flutter", "capacitor", "expo", "electron", "tauri", "swift",
    # build tools, runtimes, hosting (v2.1)
    "bun", "deno", "vite", "webpack", "esbuild", "pnpm", "npm", "yarn",
    "cloudflare", "cloudflare pages", "r2 bucket", "supabase", "firebase",
    "turso", "neon", "fly.io", "heroku", "github actions",
    # ui kits (v2.1)
    "shadcn", "material ui", "chakra", "bits ui", "radix",
]

# Names users legitimately say in intent (platforms, devices). Never flagged.
ALLOW_TOKENS = {
    "iphone", "ipad", "ios", "ipados", "android", "macos", "windows", "linux",
    "chromeos", "wifi", "bluetooth", "youtube", "github", "markdown", "pdf",
    "jpeg", "png", "webp", "heic", "heif", "csv", "json", "wcag", "gdpr", "hipaa",
}

# Tokens that look technical but are STRATA's own vocabulary.
STRATA_VOCAB_RE = re.compile(r"^(?:SPEC|FR|NFR|EVAL|CTX|US|SC|WP|OI|S[0-5])(?:-\d+)?$")

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


def tech_hits(text: str, tokens: list[str], allow: set[str] | None = None) -> list[str]:
    low = text.lower()
    hits = []
    allow = allow or set()
    for token in dict.fromkeys(tokens):
        if token.strip() in allow:
            continue
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


def strip_prior_art(text: str) -> str:
    out, skip_level = [], None
    for line in text.splitlines():
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            if skip_level is not None and level <= skip_level:
                skip_level = None
            if skip_level is None and re.search(r"prior art", m.group(2), re.I):
                skip_level = level
                continue
        if skip_level is None:
            out.append(line)
    return "\n".join(out)


def check_separation(text: str, label: str, tokens: list[str], errors: list,
                     harvested: list[str] | None = None, allow: set[str] | None = None):
    # Strip frontmatter: tags are metadata, not content.
    body = re.sub(r"\A---\s*\n.*?\n---", " ", text, count=1, flags=re.S)
    # Prior art describes the world, not a choice: naming competitors there is
    # required by the method, so that section is exempt (v2.1).
    body = strip_prior_art(body)
    # The project's own name (from the H1) is never a leak.
    title = re.search(r"^#\s+(.+)$", body, re.M)
    own = set(re.findall(r"[A-Za-z0-9]+", title.group(1).lower())) if title else set()
    allow = (allow or set()) | own
    static_hits = set(tech_hits(body, tokens, allow))
    for hit in sorted(static_hits):
        errors.append(
            f"[separation] technology token '{hit}' found in {label}; "
            f"implementation concerns belong in the derived context layer, not {label}"
        )
    for hit in tech_hits(body, harvested or [], allow):
        if hit in static_hits:
            continue
        errors.append(
            f"[separation] '{hit}' is named by this project's derived layer and also "
            f"appears in {label}; move it to context, or add it to layer-allow.txt "
            f"if it is a genuine user-facing constraint"
        )


def _phrase_hit(phrase: str, low: str) -> bool:
    # Word boundaries so "clean" does not fire inside "cleanup" (v2.1 fix).
    return re.search(r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])", low) is not None


def check_testability(clauses: list[tuple[str, str]], label: str, errors: list):
    for cid, line in clauses:
        low = line.lower()
        for phrase in NON_EVALUABLE:
            if _phrase_hit(phrase, low):
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


def _git_toplevel(path: Path) -> Path | None:
    """Repository root containing path, found without invoking git."""
    for d in [path, *path.parents]:
        if (d / ".git").exists():
            return d
    return None


def find_eval_manifest(root: Path, override: str | None) -> Path | None:
    import os
    candidates: list[Path] = []
    for raw in (override, os.environ.get("STRATA_EVALS")):
        if raw:
            p = Path(raw).expanduser()
            candidates += [p] if p.suffix in (".md", ".json") else [p / "evals.md", p / "evals.json"]
    candidates += [
        root.parent / "evals" / "evals.md",
        root.parent / "evals" / "evals.json",
        root.parent / f"{root.name}-evals.md",
        Path.home() / ".strata" / "evals" / root.name / "evals.md",
        Path.home() / ".strata" / "evals" / root.name / "evals.json",
    ]
    return next((c.resolve() for c in candidates if c.is_file()), None)


def check_eval_resolution(clauses, spec_label, root: Path, errors: list,
                          override: str | None = None):
    """Every eval tag must resolve to a manifest the implementing agent cannot see."""
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

    manifest = find_eval_manifest(root, override)
    if manifest is None:
        extra = ""
        inside = root / "evals"
        if inside.is_dir() and any(inside.iterdir()):
            extra = (f" An evals directory with content exists INSIDE the tree at {inside};"
                     f" that is worse than missing, because the implementing agent can"
                     f" read it and optimize against the test.")
        errors.append(
            f"[eval-binding] {len(tagged)} clause(s) carry eval tags but no eval manifest "
            f"was found (use --evals PATH or $STRATA_EVALS, or place it at "
            f"~/.strata/evals/{root.name}/evals.md).{extra} An eval tag that resolves "
            f"to nothing is a clause that lies with confidence"
        )
        return

    repo = _git_toplevel(root.resolve()) or root.resolve()
    if repo is not None and repo in [manifest, *manifest.parents]:
        errors.append(
            f"[eval-binding] eval manifest {manifest} is inside the repository {repo} "
            f"that the implementing agent works in; move it outside (for example "
            f"~/.strata/evals/{root.name}/) so the agent cannot read the tests it is graded on"
        )

    body = manifest.read_text(encoding="utf-8", errors="replace")
    for cid, eid in sorted(tagged.items()):
        if not re.search(r"(?<![A-Za-z0-9_-])" + re.escape(eid) + r"(?![A-Za-z0-9_-])", body):
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


FRONTMATTER_LAYER_RE = re.compile(r"\A---\s*\n(?:.*\n)*?layer:\s*(human|derived)\s*\n(?:.*\n)*?---", re.IGNORECASE)
BACKTICK_RE = re.compile(r"`([^`\n]{2,60})`")
CAMEL_RE = re.compile(r"\b[A-Za-z]*[a-z][A-Z][A-Za-z0-9.]*\b")
ALNUM_RE = re.compile(r"\b[A-Z][A-Za-z]*\d[A-Za-z0-9.]*\b")


def load_allow(*dirs: Path) -> set[str]:
    allow = set(ALLOW_TOKENS)
    for d in dirs:
        f = d / "layer-allow.txt"
        if f.is_file():
            for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.split("#", 1)[0].strip().lower()
                if line:
                    allow.add(line)
    return allow


def harvest_tokens(texts: list[str], allow: set[str]) -> list[str]:
    """Technology names the derived layer itself uses. Self-arms the denylist."""
    found: set[str] = set()
    for text in texts:
        body = re.sub(r"```.*?```", " ", text, flags=re.S)  # code blocks are noisy
        # Backtick spans only when they look like identifiers (package-ish or
        # cased); plain words in backticks are field names, not technologies.
        cands = [m.group(1) for m in BACKTICK_RE.finditer(body)
                 if (" " not in m.group(1).strip()
                     or (m.group(1).strip().count(" ") == 1 and re.search(r"\d", m.group(1))))
                 and re.search(r"[A-Z0-9@.]|[a-z]-[a-z]", m.group(1))
                 and not re.fullmatch(r"[A-Z]?[a-z]+", m.group(1))]
        cands += CAMEL_RE.findall(body) + ALNUM_RE.findall(body)
        for c in cands:
            c = c.strip().strip(".,:;()[]")
            # keep only name-like spans: no spaces beyond two words, has a letter
            if not re.search(r"[A-Za-z]", c) or len(c) < 3 or c.count(" ") > 1:
                continue
            if any(ch in c for ch in "/=<>{}$"):
                continue
            if STRATA_VOCAB_RE.match(c) or c.lower() in allow or c.lower().rstrip("s") in allow:
                continue
            if re.fullmatch(r"[\d.]+[A-Za-z]{0,3}", c):  # versions, sizes: 2.1, 16px
                continue
            found.add(c.lower())
    return sorted(found)


def declared_layer(text: str) -> str | None:
    m = FRONTMATTER_LAYER_RE.match(text)
    return m.group(1).lower() if m else None


# Which layer a file belongs to, inferred from its name. This matters: the
# derived layer is SUPPOSED to name technologies. Flagging design.md or plan.md
# for containing "python" would be a false positive, and a check that cries wolf
# gets switched off, which is worse than no check at all.
HUMAN_LAYER = ("intent", "spec", "requirements", "prd", "srs")
DERIVED_LAYER = ("context", "design", "plan", "architecture", "adr", "research",
                 "data-model", "quickstart", "tasks", "pipeline", "plays", "experience")


def infer_layer(name: str, text: str = "") -> str:
    explicit = declared_layer(text) if text else None
    if explicit:
        return explicit
    stem = name.lower().removesuffix(".md")
    for k in DERIVED_LAYER:
        if k in stem:
            return "derived"
    for k in HUMAN_LAYER:
        if k in stem:
            return "human"
    return "unknown"


def _harvest_for(paths: list[Path], allow: set[str], enabled: bool) -> list[str]:
    if not enabled:
        return []
    texts = []
    for f in paths:
        if f.is_file():
            t = f.read_text(encoding="utf-8", errors="replace")
            if infer_layer(f.name, t) == "derived":
                texts.append(t)
    return harvest_tokens(texts, allow)


def audit_files(paths: list[str], harvest: bool = True) -> int:
    """File-level checks against arbitrary spec artifacts, STRATA tree or not."""
    errors: list[str] = []
    notes: list[str] = []
    files = [Path(p) for p in paths]
    for f in files:
        if not f.is_file():
            print(f"error: not a file: {f}", file=sys.stderr)
            return 2
    if not files:
        return 2
    dirs = {f.parent for f in files} | {f.parent.parent for f in files}
    allow = load_allow(*dirs)
    tokens = TECH_TOKENS + load_extra_tokens(*dirs)
    # Harvest from every derived file in the same folders, not only those passed.
    siblings = sorted({g for f in files for g in f.parent.glob("*.md")})
    harvested = _harvest_for(siblings, allow, harvest)
    if harvest:
        notes.append(f"self-armed denylist: {len(harvested)} token(s) harvested from the derived layer")

    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")
        layer = infer_layer(f.name, text)
        if layer == "human":
            check_separation(text, f.name, tokens, errors, harvested, allow)
        elif layer == "derived":
            n = len(tech_hits(text, tokens, allow))
            notes.append(f"{f.name}: derived layer, {n} static technology token(s) (expected here)")
        else:
            n = len(tech_hits(text, tokens, allow))
            notes.append(f"{f.name}: layer unknown (add `layer: human|derived` to its frontmatter); "
                         f"{n} technology token(s) present, separation NOT checked")

        clauses = spec_clauses(text)
        if clauses and layer != "derived":
            check_testability(clauses, f.name, errors)
            check_fidelity(clauses, f.name, errors)

    if notes:
        print("Notes:")
        for n in notes:
            print(f"  - {n}")
        print()
    return report(errors, "AUDIT PASSED: no layer leakage, no non-evaluable clauses.")


REQ_LINE_RE = re.compile(r"\b(SHALL|MUST|SHOULD)\b|\b(?:SPEC|FR|NFR)-\d+\b")


def count_requirement_lines(text: str) -> int:
    return sum(1 for line in text.splitlines() if REQ_LINE_RE.search(line))


def depth_check(sources: list[str], outputs: list[str], tolerance: float = 0.9) -> int:
    """Phase 5b mechanical support: did requirement-like content survive?"""
    def total(paths):
        n = 0
        for p in paths:
            f = Path(p)
            if not f.is_file():
                print(f"error: not a file: {f}", file=sys.stderr)
                raise SystemExit(2)
            n += count_requirement_lines(f.read_text(encoding="utf-8", errors="replace"))
        return n
    src, out = total(sources), total(outputs)
    print(f"requirement-like lines: source {src}, output {out}")
    if src and out < tolerance * src:
        print(f"DEPTH FAILED: output keeps {out / src:.0%} of source requirement lines "
              f"(floor {tolerance:.0%}). Name every dropped section and regenerate with "
              f"depth-preservation directives.")
        return 1
    print("DEPTH PASSED")
    return 0


def print_trace(clauses, context_text: str | None, spec_text: str):
    """Spec clause -> intent section -> context citations, as a markdown table."""
    print("\n| Clause | Eval | Traces to | Cited in context |")
    print("|---|---|---|---|")
    ctx = context_text or ""
    for cid, line in clauses:
        ev = EVAL_TAG_RE.search(line)
        block_start = spec_text.find(line)
        block = spec_text[block_start: block_start + 600]
        tr = re.search(r"Traces to:\s*([^\n]+)", block)
        cites = len(re.findall(r"\b" + re.escape(cid) + r"\b", ctx))
        print(f"| {cid} | {ev.group(1) if ev else '-'} | {tr.group(1).strip() if tr else '-'} | {cites} |")


def _first_existing(root: Path, *names: str) -> Path | None:
    return next((root / n for n in names if (root / n).exists()), None)


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    if args[0] == "--explain":
        print(__doc__)
        return 0
    harvest = "--no-harvest" not in args
    args = [a for a in args if a != "--no-harvest"]
    if args[0] == "--audit":
        if len(args) < 2:
            print("usage: strata-validate.py --audit <file> [<file>...]", file=sys.stderr)
            return 2
        return audit_files(args[1:], harvest)
    if args[0] == "--depth":
        if "--against" not in args:
            print("usage: strata-validate.py --depth <src>... --against <out>...", file=sys.stderr)
            return 2
        i = args.index("--against")
        return depth_check(args[1:i], args[i + 1:])

    trace = "--trace" in args
    args = [a for a in args if a != "--trace"]
    evals_override = None
    if "--evals" in args:
        i = args.index("--evals")
        if i + 1 >= len(args):
            print("error: --evals needs a path", file=sys.stderr)
            return 2
        evals_override = args[i + 1]
        del args[i:i + 2]

    root = Path(args[0]).resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2

    errors: list[str] = []
    intent = root / "intent.md"
    spec = _first_existing(root, "spec.md", "requirements.md")
    context = _first_existing(root, "context.md", "plan.md", "design.md")
    substrate = root / "substrate.md"
    ledger = root / "ledger" / "ledger.md"
    standing = root / "ledger" / "standing.md"

    allow = load_allow(root, root.parent)
    tokens = TECH_TOKENS + load_extra_tokens(root, root.parent)
    derived_files = sorted(root.glob("*.md")) + sorted((root / "plays").glob("*.md"))
    harvested = _harvest_for(derived_files, allow, harvest)

    spec_text = context_text = None
    if not intent.exists():
        errors.append("[structure] missing required artifact: intent.md")
    else:
        check_separation(intent.read_text(encoding="utf-8", errors="replace"),
                         "intent.md", tokens, errors, harvested, allow)
    if spec is None:
        errors.append("[structure] missing required artifact: spec.md (or requirements.md)")
    else:
        spec_text = spec.read_text(encoding="utf-8", errors="replace")
        check_separation(spec_text, spec.name, tokens, errors, harvested, allow)

    if context is None:
        errors.append("[authorship] missing context.md (or plan.md or design.md); the system-derived implementation layer is required")
    else:
        context_text = context.read_text(encoding="utf-8", errors="replace")

    clauses = []
    if spec_text is not None:
        clauses = spec_clauses(spec_text)
        check_testability(clauses, spec.name, errors)
        check_fidelity(clauses, spec.name, errors)
        check_eval_resolution(clauses, spec.name, root, errors, evals_override)
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

    if harvest:
        print(f"self-armed denylist: {len(harvested)} token(s) harvested from the derived layer")
    if trace and spec_text is not None:
        print_trace(clauses, context_text, spec_text)
        print()

    return report(
        errors,
        "STRATA validation PASSED: layers separated, clauses evaluable and bound to "
        "external evals, spec in contact with context, continuity present, level declared.",
    )


if __name__ == "__main__":
    raise SystemExit(main())
