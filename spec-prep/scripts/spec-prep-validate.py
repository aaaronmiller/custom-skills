#!/usr/bin/env python3
"""spec-prep-validate.py: run the nine spec-prep validation checks.

Usage:
    python3 spec-prep-validate.py ARTIFACT_DIR [--operation OP] [--build-root DIR]
                                  [--evals PATH] [--source-map FILE[#heading]]
                                  [--continuity external] [--no-harvest] [--trace] [--json]
    python3 spec-prep-validate.py --audit FILE [FILE ...] [--no-harvest] [--json]
    python3 spec-prep-validate.py --help

ARTIFACT_DIR holds intent.md, the specification (spec.md, else requirements.md),
the derived layer (context.md, plan.md or design.md) and, for standalone and
native preparation, substrate.md plus ledger/ledger.md and ledger/standing.md
(flat ledger.md and standing.md are accepted aliases). For native preparation
pass the feature root (specs/<feature>) and --build-root.

--operation   standalone (default), native-preparation or input-handoff.
              input-handoff records continuity and honesty as not_run: an input
              handoff carries no ledger or substrate.
--build-root  The implementation checkout. The eval store must sit outside it,
              and ledger, standing and substrate are also looked up there.
              Without it the boundary is the buildRoot of the delivery.json
              workstream containing ARTIFACT_DIR, else the Git top level, else
              the nearest .specify/ or AGENTS.md+specs/ project, else
              ARTIFACT_DIR (its parent when ARTIFACT_DIR is inputs/).
--evals       Eval store (evals.md or evals.json). Default: $SPECPREP_EVALS, then
              ../evals/evals.md, ../evals/evals.json, ../<slug>-evals.md,
              ~/.spec-prep/evals/<slug>/evals.md and evals.json. <slug> is the
              project directory name: the build root's name, else the parent of
              inputs/ or of specs/<feature>, else ARTIFACT_DIR's name.
--source-map  Source-disposition map, FILE or FILE#fragment. Default: the
              intent.md section whose heading contains "source disposition",
              else traceability.md, else source-disposition.md in ARTIFACT_DIR.
              A fragment matches a heading's GitHub slug, ignoring a leading
              section number ('#prior-art' names '## 10. Prior art').
--continuity external
              Continuity lives in an external system (for example a Living
              Documents dossier); the continuity check records not_run and the
              receipt cites that system's evidence instead.
--no-harvest  Use only the static and project token lists for separation.
--trace       Print the clause, eval, intent trace and derived-citation table.
--json        Print a machine-readable result for preparation.json evidence.
--audit       Run separation, testability and identity on arbitrary files, such as
              Spec Kit, OpenSpec or Kiro output with no spec-prep tree.

Checks (a failed check exits 1; not_run never fails; usage errors exit 2):
  separation    no technology token in intent or specification (SKILL.md rule 1)
  eval-binding  every clause carries an EVAL-ID defined in an eval store that
                sits outside the build root
  testability   no clause uses non-evaluable language
  identity      the specification declares at least one clause; IDs are unique.
                Accepted clause prefixes: SPEC-, REQ-, FR-, NFR- (then digits).
  drift         derived layer cites every clause and no undeclared one; every
                supporting file is declared in the source-disposition map
  continuity    ledger and standing exist, carry content, and aliases agree
  honesty       substrate.md declares S0..S5 under "## Declared level"
  authorship    the derived layer exists and a source-disposition map exists
  prior-art     a done, directed or waived prior-art record exists

Token files, read from ARTIFACT_DIR and its parent directory:
  tech-tokens.txt   extra technology tokens, one per line, '#' starts a comment.
  layer-allow.txt   tokens allowed in intent or spec, one per line, each followed
                    by '# <justification>'. An entry without a justification
                    fails the separation check.

The checks are mechanical. They establish the identities, references, paths and
lexical conditions they inspect; semantic fidelity, evaluator isolation and
runtime feasibility need separate evidence.
"""

import json
import os
import re
import sys
from pathlib import Path

CHECKS = ["separation", "eval-binding", "testability", "identity", "drift",
          "continuity", "honesty", "authorship", "prior-art"]
OPERATIONS = ("standalone", "native-preparation", "input-handoff")

# Curated denylist. Whole-word, case-insensitive. A hit in intent or spec means
# an implementation concern leaked into a layer it does not own.
TECH_TOKENS = [
    # web frameworks and runtimes
    "react", "svelte", "vue", "angular", "next.js", "nextjs", "nuxt",
    "node.js", "nodejs", "express", "hono", "fastify", "django", "flask",
    "rails", "spring boot", "fastapi", "htmx", "jquery",
    # languages
    "python", "typescript", "javascript", "rust", "golang", "java",
    "kotlin", "swiftui", "ruby", "php", "bash script", "powershell",
    # datastores
    "postgres", "postgresql", "mysql", "mariadb", "sqlite", "mongodb",
    "dynamodb", "redis", "kafka", "rabbitmq", "duckdb",
    "pgvector", "qdrant", "pinecone", "elasticsearch", "kuzudb", "neo4j",
    # infrastructure and hosting
    "graphql", "grpc", "kubernetes", "docker", "terraform",
    "cloudflare workers", "vercel", "netlify", "aws lambda", "s3 bucket",
    "ec2", "gcp", "azure", "systemd", "nginx",
    # frontend, visualization and styling
    "tailwind", "bootstrap", "echarts", "chart.js", "chartjs", "plotly",
    "d3.js", "recharts", "highcharts", "matplotlib",
    # observability
    "grafana", "prometheus", "datadog", "opentelemetry", "sentry",
    # test tooling
    "pytest", "jest", "vitest", "playwright", "cypress", "junit",
    # architecture shapes the human layer should not choose
    "microservice", "monolith", "serverless function", "message queue",
    # browser platform APIs
    "indexeddb", "localstorage", "sessionstorage", "webgpu", "webgl", "webgl2",
    "webassembly", "wasm", "service worker", "web worker", "websocket", "webrtc",
    "offscreencanvas", "getusermedia", "pwa manifest",
    # ML and AI runtimes
    "onnx", "onnx runtime", "pytorch", "tensorflow", "tflite", "mediapipe",
    "transformers.js", "hugging face", "huggingface", "llama.cpp", "ollama",
    "openai api", "anthropic api", "langchain", "llamaindex", "segment anything",
    # mobile and desktop shells
    "react native", "flutter", "capacitor", "expo", "electron", "tauri", "swift",
    # build tools, runtimes and hosting
    "bun", "deno", "vite", "webpack", "esbuild", "pnpm", "npm", "yarn",
    "cloudflare", "cloudflare pages", "r2 bucket", "supabase", "firebase",
    "turso", "neon", "fly.io", "heroku", "github actions",
    # UI kits
    "shadcn", "material ui", "chakra", "bits ui", "radix",
]

# Platform, device and format names users legitimately state in intent.
ALLOW_TOKENS = {
    "iphone", "ipad", "ios", "ipados", "android", "macos", "windows", "linux",
    "chromeos", "wifi", "bluetooth", "youtube", "github", "markdown", "pdf",
    "jpeg", "png", "webp", "heic", "heif", "csv", "json", "wcag", "gdpr", "hipaa",
}

# Identifiers that look technical but are spec-prep or Spec Kit vocabulary.
VOCAB_RE = re.compile(r"^(?:SPEC|REQ|FR|NFR|EVAL|CTX|US|SC|WP|OI|S[0-5])(?:-\d+)?$|^US\d+$")

# Phrases that cannot become a pass/fail evaluation.
NON_EVALUABLE = [
    "user-friendly", "user friendly", "intuitive", "seamless", "robust",
    "scalable", "flexible", "easy to use", "as needed", "as appropriate",
    "etc.", "and so on", "where possible", "if necessary", "reasonable",
    "good performance", "fast enough", "modern", "clean", "elegant",
    "best practice", "industry standard", "properly", "correctly handle",
]

# Accepted clause prefixes. SPEC- is the spec-prep form; REQ- is a common requirements.md
# form; FR-/NFR- are what Spec Kit, OpenSpec and Kiro emit.
CLAUSE_PREFIXES = ("SPEC", "REQ", "FR", "NFR")
_CLAUSE_ID = r"((?:" + "|".join(CLAUSE_PREFIXES) + r")-\d+)"
SPEC_CLAUSE_RE = re.compile(r"^[ \t]*(?:[-*|][ \t]*)?\**" + _CLAUSE_ID + r"\b", re.M)
EVAL_TAG_RE = re.compile(r"\[(EVAL-[A-Za-z0-9_-]+)\]")
EVAL_ID_RE = re.compile(r"\bEVAL-[A-Za-z0-9_-]+")
CITATION_RE = re.compile(r"\b" + _CLAUSE_ID + r"\b")
LEVEL_RE = re.compile(r"^[ \t]*(?:[-*][ \t]*)?\**S[0-5]\b", re.M)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$", re.M)
FRONTMATTER_RE = re.compile(r"\A---\s*\n.*?\n---[ \t]*\n?", re.S)
LAYER_RE = re.compile(r"\A---\s*\n(?:.*\n)*?layer:\s*(human|derived)\s*\n(?:.*\n)*?---", re.I)
BACKTICK_RE = re.compile(r"`([^`\n]{2,60})`")
CAMEL_RE = re.compile(r"\b[A-Za-z]*[a-z][A-Z][A-Za-z0-9.]*\b")
ALNUM_RE = re.compile(r"\b[A-Z][A-Za-z]*\d[A-Za-z0-9.]*\b")
DISPOSITION_RE = re.compile(r"(?i)\b(preserv|incorporat|chang|defer|reject|unavailable|supersed|duplicat|unresolved)")
PRIOR_ART_STATUS_RE = re.compile(
    r"(?im)prior[ -]art(?:[ -](?:gate|status|record))?[*`]*[ \t]*[:=|][ \t]*[*`]*[ \t]*"
    r"(done|directed|waived)\b[*`]*[ \t]*[|:;,.)-]*[ \t]*(.*)$")
SUPPORTING_DIRS = ("data", "references", "sources", "fixtures", "appendices")

# Layer by name: a whole path segment (the file stem or a directory such as plays/) that
# equals one of these words or starts or ends with it at a '-', '_' or '.' boundary.
# DERIVED_LAYER is the list in SKILL.md rule 1; any other file declares `layer: derived`.
HUMAN_LAYER = ("intent", "spec", "specification", "requirements", "prd", "srs")
DERIVED_LAYER = ("context", "plan", "design", "research", "data-model", "quickstart",
                 "tasks", "experience", "plays")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def strip_frontmatter(text: str) -> str:
    return FRONTMATTER_RE.sub("", text, count=1)


class Result:
    """Per-check status and findings, in the receipt gate vocabulary."""

    def __init__(self, names):
        self.status = {n: "passed" for n in names}
        self.findings = {n: [] for n in names}

    def fail(self, check: str, message: str):
        self.status[check] = "failed"
        self.findings[check].append(message)

    def skip(self, check: str, reason: str):
        if self.status[check] != "failed":
            self.status[check] = "not_run"
            self.findings[check] = [reason]

    def note(self, check: str, message: str):
        self.findings[check].append(message)

    @property
    def failed(self):
        return [n for n, s in self.status.items() if s == "failed"]


# ---------- token lists ----------

def token_file_lines(path: Path):
    for raw in read(path).splitlines():
        token, _, comment = raw.partition("#")
        token = token.strip().lower()
        if token:
            yield token, comment.strip()


def load_extra_tokens(dirs) -> list[str]:
    extra = []
    for d in dirs:
        f = d / "tech-tokens.txt"
        if f.is_file():
            extra += [t for t, _ in token_file_lines(f)]
    return extra


def load_allow(dirs, result: Result | None = None) -> set[str]:
    allow = set(ALLOW_TOKENS)
    for d in dirs:
        f = d / "layer-allow.txt"
        if f.is_file():
            for token, why in token_file_lines(f):
                allow.add(token)
                if result is not None and not re.search(r"\w{2,}", why):
                    result.fail("separation", f"layer-allow.txt entry '{token}' in {d} has no "
                                              "justification; write '<token>  # <source and reason>'")
    return allow


def tech_hits(text: str, tokens, allow) -> list[str]:
    low, hits = text.lower(), []
    for token in dict.fromkeys(t.strip() for t in tokens if t.strip()):
        if token in allow:
            continue
        if re.search(r"(?<![a-z0-9])" + re.escape(token) + r"(?![a-z0-9])", low):
            hits.append(token)
    return hits


def declared_layer(text: str) -> str | None:
    m = LAYER_RE.match(text)
    return m.group(1).lower() if m else None


def _segment_has(segment: str, words) -> bool:
    return any(re.search(r"(?:^|[-_.])" + re.escape(w) + r"(?:$|[-_.])", segment) for w in words)


def infer_layer(name: str, text: str = "") -> str:
    """Layer of a file from its frontmatter, else from whole path segments of name (a
    relative label such as 'plan.md' or 'plays/deploy.md'), never substrings. The file stem
    decides first; directory segments decide only when the stem names no layer."""
    explicit = declared_layer(text) if text else None
    if explicit:
        return explicit
    parts = [p.lower() for p in Path(name).parts]
    if not parts:
        return "unknown"
    for segment in (parts[-1].removesuffix(".md"), *reversed(parts[:-1])):
        if _segment_has(segment, DERIVED_LAYER):
            return "derived"
        if _segment_has(segment, HUMAN_LAYER):
            return "human"
    return "unknown"


def harvest_tokens(texts, allow) -> list[str]:
    """Technology names the derived layer uses arm the separation check."""
    found = set()
    for text in texts:
        body = re.sub(r"```.*?```", " ", text, flags=re.S)
        cands = [m.group(1) for m in BACKTICK_RE.finditer(body)
                 if (" " not in m.group(1).strip()
                     or (m.group(1).strip().count(" ") == 1 and re.search(r"\d", m.group(1))))
                 and re.search(r"[A-Z0-9@.]|[a-z]-[a-z]", m.group(1))
                 and not re.fullmatch(r"[A-Z]?[a-z]+", m.group(1))]
        cands += CAMEL_RE.findall(body) + ALNUM_RE.findall(body)
        for c in cands:
            c = c.strip().strip(".,:;()[]")
            if not re.search(r"[A-Za-z]", c) or len(c) < 3 or c.count(" ") > 1:
                continue
            if any(ch in c for ch in "/=<>{}$#"):
                continue
            if VOCAB_RE.match(c) or c.lower() in allow or c.lower().rstrip("s") in allow:
                continue
            if re.fullmatch(r"[\d.]+[A-Za-z]{0,3}", c):
                continue
            found.add(c.lower())
    return sorted(found)


def layer_label(path: Path, base: Path | None = None) -> str:
    """Path of a file relative to base (default: its parent directory and name), for
    whole-segment layer inference."""
    if base is not None and path.is_relative_to(base):
        return path.relative_to(base).as_posix()
    return f"{path.parent.name}/{path.name}" if path.parent.name else path.name


def harvest_for(paths, allow, enabled: bool, base: Path | None = None) -> list[str]:
    if not enabled:
        return []
    texts = []
    for f in paths:
        if f.is_file():
            t = read(f)
            if infer_layer(layer_label(f, base), t) == "derived":
                texts.append(t)
    return harvest_tokens(texts, allow)


# ---------- markdown helpers ----------

def gh_slug(heading: str) -> str:
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def heading_matches(heading: str, fragment: str) -> bool:
    """A link fragment names a heading by its GitHub slug, ignoring a leading section number
    on either side: '#prior-art' and '#10-prior-art' both name '## 10. Prior art'.
    spec-prep-delivery.py uses the same rule."""
    frag = fragment.strip().lower()
    unnumbered = re.sub(r"^\d+(?:\.\d+)*\.?\s+", "", heading.strip())
    return frag in (gh_slug(heading), gh_slug(unnumbered)) or \
        re.sub(r"^\d+-", "", frag) == gh_slug(unnumbered)


def section(text: str, pattern: str | None = None, slug: str | None = None) -> str | None:
    """Body of the first heading matching pattern (or link fragment, see heading_matches),
    up to the next heading of equal or higher level."""
    heads = list(HEADING_RE.finditer(text))
    for i, m in enumerate(heads):
        hit = heading_matches(m.group(2), slug) if slug is not None else re.search(pattern, m.group(2), re.I)
        if hit:
            level = len(m.group(1))
            end = next((h.start() for h in heads[i + 1:] if len(h.group(1)) <= level), len(text))
            return text[m.end():end]
    return None


def strip_sections(text: str, pattern: str) -> str:
    out, skip = [], None
    for line in text.splitlines():
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            if skip is not None and level <= skip:
                skip = None
            if skip is None and re.search(pattern, m.group(2), re.I):
                skip = level
                continue
        if skip is None:
            out.append(line)
    return "\n".join(out)


def has_content(body: str | None) -> bool:
    """True when a section holds more than template scaffolding."""
    if not body:
        return False
    lines = body.splitlines()
    for i, line in enumerate(lines):
        s = line.strip()
        if not s or re.fullmatch(r"\|?[\s:|-]+\|?", s):
            continue
        if i + 1 < len(lines) and re.fullmatch(r"\|?[\s:|-]*-{3,}[\s:|-]*\|?", lines[i + 1].strip()):
            continue  # table header row
        if re.fullmatch(r"[|\s.]*(?:\.\.\.|…)[|\s.]*", s) or re.fullmatch(r"\|[\s|.…]*\|", s):
            continue  # placeholder row
        if re.fullmatch(r"\[[^\]]*\]", s):
            continue  # bracketed template instruction
        if re.search(r"\w{2,}", s):
            return True
    return False


def spec_clauses(text: str):
    """(clause ID, clause block) pairs; a block stops at a blank line, bullet or heading."""
    out = []
    for match in SPEC_CLAUSE_RE.finditer(text):
        start = text.rfind("\n", 0, match.start()) + 1
        lines = text[start:].splitlines()
        block = [lines[0]]
        for line in lines[1:]:
            if not line.strip() or SPEC_CLAUSE_RE.match(line) or \
                    re.match(r"^\s*(?:#{1,6}\s|[-*]\s|\d+[.)]\s|\||>)", line):
                break
            block.append(line)
        out.append((match.group(1), "\n".join(block)))
    return out


def first_existing(dirs, *names):
    for d in dirs:
        for n in names:
            if d is not None and (d / n).is_file():
                return d / n
    return None


# ---------- the nine checks ----------

def check_separation(text, label, tokens, harvested, allow, result: Result):
    body = strip_frontmatter(text)
    body = strip_sections(body, r"prior art")
    title = re.search(r"^#\s+(.+)$", body, re.M)
    own = set(re.findall(r"[a-z0-9]+", title.group(1).lower())) if title else set()
    allow = allow | own
    static = set(tech_hits(body, tokens, allow))
    for hit in sorted(static):
        result.fail("separation", f"technology token '{hit}' in {label}; move the mechanism to the "
                                  "derived layer, or add a justified layer-allow.txt entry for a user constraint")
    for hit in tech_hits(body, harvested, allow):
        if hit not in static:
            result.fail("separation", f"'{hit}' is named by the derived layer and appears in {label}; "
                                      "move it to the derived layer or justify it in layer-allow.txt")


def check_testability(clauses, label, result: Result):
    for cid, block in clauses:
        low = block.lower()
        for phrase in NON_EVALUABLE:
            if re.search(r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])", low):
                result.fail("testability", f"{cid} in {label} uses non-evaluable language '{phrase}'")
                break


def check_identity(clauses, label, result: Result):
    ids = [cid for cid, _ in clauses]
    for cid in sorted({c for c in ids if ids.count(c) > 1}):
        result.fail("identity", f"duplicate clause ID {cid} in {label}")
    if not clauses:
        result.fail("identity", f"{label} declares no {', '.join(p + '-' for p in CLAUSE_PREFIXES)} clause")


def git_toplevel(path: Path) -> Path | None:
    for d in [path, *path.parents]:
        if (d / ".git").exists():
            return d
    return None


def delivery_build_root(root: Path) -> Path | None:
    """The buildRoot of the delivery.json workstream (in root or an ancestor) containing root."""
    root = root.resolve()
    for d in (root, *root.parents):
        manifest = d / "delivery.json"
        if not manifest.is_file():
            continue
        try:
            streams = json.loads(read(manifest)).get("workstreams", [])
        except (json.JSONDecodeError, AttributeError):
            return None
        for stream in streams if isinstance(streams, list) else []:
            build = stream.get("buildRoot") if isinstance(stream, dict) else None
            if isinstance(build, str) and build and not Path(build).is_absolute():
                candidate = (d / build).resolve()
                if root.is_relative_to(candidate):
                    return candidate
        return None
    return None


def project_slug(root: Path, build_root: Path | None) -> str:
    """The project directory name: the build root's name, else the parent of inputs/ or of
    specs/<feature>, else the artifact directory's own name."""
    root = root.resolve()
    if build_root is not None:
        return build_root.resolve().name
    if root.name == "inputs":
        return root.parent.name
    if root.parent.name == "specs":
        return root.parent.parent.name
    return root.name


def find_eval_store(root: Path, override: str | None, build_root: Path | None = None) -> Path | None:
    raw = override or os.environ.get("SPECPREP_EVALS")
    if raw:
        p = Path(raw).expanduser()
        cands = [p] if p.suffix in (".md", ".json") else [p / "evals.md", p / "evals.json"]
        return next((c.resolve() for c in cands if c.is_file()), None)
    slug = project_slug(root, build_root)
    cands = [root.parent / "evals" / "evals.md", root.parent / "evals" / "evals.json",
             root.parent / f"{slug}-evals.md",
             Path.home() / ".spec-prep" / "evals" / slug / "evals.md",
             Path.home() / ".spec-prep" / "evals" / slug / "evals.json"]
    return next((c.resolve() for c in cands if c.is_file()), None)


def defined_evals(store: Path, result: Result) -> set[str]:
    body = read(store)
    defined = set()
    if store.suffix == ".json":
        try:
            data = json.loads(body)
        except json.JSONDecodeError as exc:
            result.fail("eval-binding", f"eval store {store.name} is not valid JSON: {exc}")
            return defined

        def collect(value):
            if isinstance(value, dict):
                for key, item in value.items():
                    if re.fullmatch(r"EVAL-[A-Za-z0-9_-]+", key) and item:
                        defined.add(key)
                    if key in ("id", "eval_id") and isinstance(item, str) and \
                            re.fullmatch(r"EVAL-[A-Za-z0-9_-]+", item):
                        defined.add(item)
                    if isinstance(item, (dict, list)):
                        collect(item)
            elif isinstance(value, list):
                for item in value:
                    collect(item)
        collect(data)
        return defined
    for m in re.finditer(r"(?m)^\s*(?:#{1,6}\s+|[-*]\s+|\|\s*)?\**(EVAL-[A-Za-z0-9_-]+)\b\**([^\n]*)", body):
        rest = m.group(2)
        if re.match(r"(?i)\s*(?:(?:was|is)\s+)?(?:removed|undefined|missing|tbd|todo|not defined)\b", rest):
            continue
        if re.search(r"\w{2,}", rest.replace("|", " ")):
            defined.add(m.group(1))
    return defined


def check_eval_binding(clauses, label, root, build_root, override, trace_text, result: Result):
    tagged = {}
    for cid, block in clauses:
        m = EVAL_TAG_RE.search(block)
        if m:
            tagged[cid] = m.group(1)
            continue
        mapped = None
        for line in (trace_text or "").splitlines():
            if re.search(r"\b" + re.escape(cid) + r"\b", line):
                e = EVAL_ID_RE.search(line)
                if e:
                    mapped = e.group(0)
                    break
        if mapped:
            tagged[cid] = mapped
        else:
            result.fail("eval-binding", f"{cid} in {label} has no [EVAL-...] tag and no traceability mapping")
    if not tagged:
        return
    inferred = build_root.resolve() if build_root else delivery_build_root(root)
    store = find_eval_store(root, override, inferred)
    if store is None:
        inside = root / "evals"
        extra = f"; an evals directory exists inside the tree at {inside}" if inside.is_dir() else ""
        slug = project_slug(root, inferred)
        result.fail("eval-binding", f"{len(tagged)} clause(s) carry eval IDs but no eval store was found "
                                    f"(pass --evals, set SPECPREP_EVALS, or use ~/.spec-prep/evals/{slug}/evals.md){extra}")
        return
    if build_root is not None and not root.resolve().is_relative_to(build_root.resolve()):
        result.fail("eval-binding", "artifact directory is outside the declared build root")
        return
    # Build-root boundary: --build-root, else the delivery.json workstream, else Git, else
    # the nearest Spec Kit or AGENTS.md project, else the artifact directory.
    repo = inferred or git_toplevel(root.resolve())
    if repo is None:
        repo = next((p for p in (root.resolve(), *root.resolve().parents)
                     if (p / ".specify").is_dir() or
                     ((p / "AGENTS.md").is_file() and (p / "specs").is_dir())),
                    root.resolve().parent if root.name == "inputs" else root.resolve())
    if repo in [store, *store.parents]:
        result.fail("eval-binding", f"eval store {store} is inside the build root {repo}; "
                                    "move it outside, then establish evaluator isolation separately")
    defined = defined_evals(store, result)
    for cid, eid in sorted(tagged.items()):
        if eid not in defined:
            result.fail("eval-binding", f"{cid} cites {eid}, which {store.name} does not define")


def supporting_files(bases):
    seen = []
    for base in bases:
        for d in SUPPORTING_DIRS:
            top = base / d
            if not top.is_dir():
                continue
            for p in sorted(top.rglob("*")):
                rel = p.relative_to(base)
                if p.is_file() and not any(part.startswith(".") for part in rel.parts):
                    seen.append((base, rel))
    return seen


def declared_in(map_text: str, rel: Path) -> bool:
    posix = rel.as_posix()
    if posix in map_text:
        return True
    return any(parent.as_posix() + "/" in map_text for parent in rel.parents if parent.as_posix() != ".")


def check_drift(clauses, citing_text, map_text, bases, result: Result):
    if citing_text is None:
        result.skip("drift", "no derived layer to compare against the specification (see authorship)")
    else:
        cited = set(CITATION_RE.findall(citing_text))
        declared = {cid for cid, _ in clauses}
        for cid in sorted(declared - cited):
            result.fail("drift", f"{cid} is declared in the specification but cited by no derived "
                                 "decision, task or traceability row")
        for cid in sorted(cited - declared):
            result.fail("drift", f"the derived layer cites {cid}, which the specification does not declare")
    files = supporting_files(bases)
    if files and map_text is None:
        result.fail("drift", f"{len(files)} supporting file(s) but no source-disposition map declares them")
        return
    undeclared = [rel.as_posix() for _, rel in files if not declared_in(map_text or "", rel)]
    for rel in undeclared[:20]:
        result.fail("drift", f"supporting file {rel} is not declared in the source-disposition map "
                             "(declare it with path, role and why; never delete it)")
    if len(undeclared) > 20:
        result.fail("drift", f"{len(undeclared) - 20} more undeclared supporting file(s)")


def check_continuity(dirs, result: Result):
    for d in dirs:
        if d is None:
            continue
        for flat, nested in (("ledger.md", "ledger/ledger.md"), ("standing.md", "ledger/standing.md")):
            a, b = d / flat, d / nested
            if a.is_file() and b.is_file() and a.read_bytes() != b.read_bytes():
                result.fail("continuity", f"{flat} and {nested} disagree in {d}; resolve the declared authority")
    for label, names in (("ledger", ("ledger/ledger.md", "ledger.md")),
                         ("standing", ("ledger/standing.md", "standing.md"))):
        f = first_existing(dirs, *names)
        if f is None:
            result.fail("continuity", f"missing {label} ({' or '.join(names)})")
        elif len(strip_frontmatter(read(f)).strip()) < 40:
            result.fail("continuity", f"{f.name} is effectively empty; record real decisions and state")


def check_honesty(dirs, result: Result):
    f = first_existing(dirs, "substrate.md")
    if f is None:
        result.fail("honesty", "missing substrate.md")
        return
    body = section(read(f), r"^declared level$")
    if body is None or not LEVEL_RE.search(body):
        result.fail("honesty", "substrate.md does not declare a level S0..S5 at the start of a line "
                               "under '## Declared level'")


def check_authorship(derived, map_text, map_label, result: Result):
    if derived is None:
        result.fail("authorship", "missing the derived layer (context.md, plan.md or design.md)")
    if map_text is None:
        result.fail("authorship", "no source-disposition map (intent.md 'Source disposition' section, "
                                  "traceability.md or source-disposition.md, or --source-map)")
    elif not DISPOSITION_RE.search(map_text):
        result.fail("authorship", f"source-disposition map {map_label} records no disposition "
                                  "(preserved, incorporated, changed, deferred, rejected, unavailable, "
                                  "superseded, duplicate or unresolved)")


def check_prior_art(intent_text, map_text, root, build_root, result: Result):
    record = section(intent_text, r"prior art") if intent_text else None
    content = has_content(record)
    status = None
    for text in (map_text, intent_text):
        if text:
            m = PRIOR_ART_STATUS_RE.search(text)
            if m:
                status, reason = m.group(1).lower(), m.group(2).strip().strip("|").strip()
                break
    if status is None:
        if not content:
            result.fail("prior-art", "no prior-art record: intent section 'Prior art' is empty and no "
                                     "'prior-art: done|directed|waived' line exists")
        return
    if status == "waived" and not re.search(r"\w{2,}", reason):
        result.fail("prior-art", "prior-art waived without a recorded reason")
    elif status == "directed":
        early = [n for n in ("plan.md", "tasks.md") if (root / n).is_file()]
        if early:
            result.fail("prior-art", f"prior-art survey is only directed, but {', '.join(early)} already "
                                     "exist; plan and tasks wait until the record lands")
    elif status == "done" and not content:
        named = re.findall(r"[\w./-]+\.(?:md|json|txt|csv)", reason)
        bases = [root] + ([build_root] if build_root else [])
        if not any((b / n).is_file() for n in named for b in bases):
            result.fail("prior-art", "prior-art marked done, but intent 'Prior art' is empty and the "
                                     "line names no existing record file")
    result.note("prior-art", f"status: {status}")


# ---------- reporting ----------

def emit(result: Result, header: str, as_json: bool, scope: str) -> int:
    if as_json:
        print(json.dumps({"header": header, "valid": not result.failed,
                          "checks": [{"name": n, "status": result.status[n], "findings": result.findings[n]}
                                     for n in result.status],
                          "scope": scope}, indent=2))
    else:
        print(header)
        for n, s in result.status.items():
            print(f"  {n:<13} {s}")
            for f in result.findings[n]:
                print(f"      - {f}")
        verdict = "FAILED" if result.failed else "PASSED"
        print(f"\nRESULT: {verdict} ({len(result.failed)} of {len(result.status)} checks failed). {scope}")
    return 1 if result.failed else 0


SCOPE = ("Mechanical checks only: semantic fidelity, evaluator isolation and runtime "
         "feasibility are not established by this command.")


def validate(root: Path, operation="standalone", build_root=None, evals=None, source_map=None,
             continuity_external=False, harvest=True):
    result = Result(CHECKS)
    dirs = [root] + ([build_root] if build_root and build_root != root else [])
    intent = root / "intent.md"
    spec = first_existing([root], "spec.md", "requirements.md")
    derived = first_existing([root], "context.md", "plan.md", "design.md")

    allow = load_allow([root, root.parent], result)
    tokens = TECH_TOKENS + load_extra_tokens([root, root.parent])
    derived_files = sorted(root.glob("*.md")) + sorted((root / "plays").glob("*.md"))
    harvested = harvest_for(derived_files, allow, harvest, root)
    if harvest:
        result.note("separation", f"{len(harvested)} token(s) harvested from the derived layer")

    intent_text = read(intent) if intent.is_file() else None
    if intent_text is None:
        result.fail("separation", "missing intent.md")
    else:
        check_separation(intent_text, "intent.md", tokens, harvested, allow, result)

    spec_text = read(spec) if spec else None
    clauses = []
    if spec_text is None:
        result.fail("identity", "missing spec.md (or requirements.md)")
    else:
        check_separation(spec_text, spec.name, tokens, harvested, allow, result)
        clauses = spec_clauses(strip_frontmatter(spec_text))
        check_testability(clauses, spec.name, result)
        check_identity(clauses, spec.name, result)

    map_text, map_label = None, None
    if source_map:
        path, _, frag = source_map.partition("#")
        p = (root / path) if not Path(path).is_absolute() else Path(path)
        if p.is_file():
            text = read(p)
            map_text = section(text, slug=frag) if frag else text
            map_label = source_map
    elif intent_text is not None and section(intent_text, r"source[ -]disposition") is not None:
        map_text, map_label = section(intent_text, r"source[ -]disposition"), "intent.md#source-disposition"
    else:
        for name in ("traceability.md", "source-disposition.md"):
            if (root / name).is_file():
                map_text, map_label = read(root / name), name
                break

    trace = root / "traceability.md"
    trace_text = read(trace) if trace.is_file() else None
    if spec_text is not None:
        check_eval_binding(clauses, spec.name, root, build_root, evals, trace_text, result)
    else:
        result.skip("eval-binding", "no specification")

    citing = [read(f) for f in (derived, root / "tasks.md", trace) if f is not None and f.is_file()]
    if spec_text is not None:
        check_drift(clauses, "\n".join(citing) if derived is not None else None,
                    map_text, dirs, result)
    else:
        result.skip("drift", "no specification")

    if operation == "input-handoff":
        result.skip("continuity", "not required for an input handoff")
        result.skip("honesty", "not required for an input handoff")
    else:
        if continuity_external:
            result.skip("continuity", "continuity declared external; cite that system's evidence in the receipt")
        else:
            check_continuity(dirs, result)
        check_honesty(dirs, result)

    check_authorship(derived, map_text, map_label, result)
    check_prior_art(intent_text, map_text, root, build_root, result)
    return result, clauses, spec_text, "\n".join(citing)


def audit(paths, harvest=True):
    result = Result(["separation", "testability", "identity"])
    files = [Path(p) for p in paths]
    for f in files:
        if not f.is_file():
            print(f"error: not a file: {f}", file=sys.stderr)
            return None
    dirs = sorted({f.parent for f in files} | {f.parent.parent for f in files})
    allow = load_allow(dirs, result)
    tokens = TECH_TOKENS + load_extra_tokens(dirs)
    siblings = sorted({g for f in files for g in f.parent.glob("*.md")})
    harvested = harvest_for(siblings, allow, harvest)
    for f in files:
        text = read(f)
        layer = infer_layer(layer_label(f), text)
        if layer == "human":
            check_separation(text, f.name, tokens, harvested, allow, result)
        else:
            result.note("separation", f"{f.name}: layer {layer}; separation not checked "
                                      "(declare 'layer: human' in its frontmatter to check it)")
        clauses = spec_clauses(strip_frontmatter(text))
        if clauses and layer != "derived":
            check_testability(clauses, f.name, result)
            check_identity(clauses, f.name, result)
    return result


def print_trace(clauses, citing_text, spec_text):
    print("\n| Clause | Eval | Traces to | Derived citations |")
    print("|---|---|---|---|")
    for cid, block in clauses:
        ev = EVAL_TAG_RE.search(block)
        start = spec_text.find(block) + len(block)
        nxt = SPEC_CLAUSE_RE.search(spec_text, start)
        tail = spec_text[start:nxt.start() if nxt else len(spec_text)]
        tr = re.search(r"Traces to:\s*([^\n]+)", block + tail)
        cites = len(re.findall(r"\b" + re.escape(cid) + r"\b", citing_text or ""))
        print(f"| {cid} | {ev.group(1) if ev else '-'} | {tr.group(1).strip() if tr else '-'} | {cites} |")


def take(args, flag):
    if flag not in args:
        return None
    i = args.index(flag)
    if i + 1 >= len(args) or args[i + 1].startswith("--"):
        raise SystemExit(f"error: {flag} needs a value")
    value = args[i + 1]
    del args[i:i + 2]
    return value


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if args else 2
    harvest = "--no-harvest" not in args
    as_json = "--json" in args
    trace = "--trace" in args
    args = [a for a in args if a not in ("--no-harvest", "--json", "--trace")]
    if args[0] == "--audit":
        if len(args) < 2:
            print("usage: spec-prep-validate.py --audit FILE [FILE ...]", file=sys.stderr)
            return 2
        result = audit(args[1:], harvest)
        if result is None:
            return 2
        return emit(result, f"spec-prep audit: {len(args) - 1} file(s)", as_json, SCOPE)
    try:
        operation = take(args, "--operation") or "standalone"
        build = take(args, "--build-root")
        evals = take(args, "--evals")
        source_map = take(args, "--source-map")
        continuity = take(args, "--continuity")
    except SystemExit as exc:
        print(exc, file=sys.stderr)
        return 2
    if operation not in OPERATIONS:
        print(f"error: --operation must be one of {', '.join(OPERATIONS)}", file=sys.stderr)
        return 2
    if continuity not in (None, "external"):
        print("error: --continuity accepts only 'external'", file=sys.stderr)
        return 2
    if len(args) != 1 or args[0].startswith("--"):
        print("usage: spec-prep-validate.py ARTIFACT_DIR [options]; see --help", file=sys.stderr)
        return 2
    root = Path(args[0]).resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2
    build_root = Path(build).resolve() if build else None
    if build_root is not None and not build_root.is_dir():
        print(f"error: build root is not a directory: {build_root}", file=sys.stderr)
        return 2
    result, clauses, spec_text, citing = validate(root, operation, build_root, evals, source_map,
                                                  continuity == "external", harvest)
    code = emit(result, f"spec-prep validation: {root} (operation {operation})", as_json, SCOPE)
    if trace and spec_text is not None and not as_json:
        print_trace(clauses, citing, spec_text)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
