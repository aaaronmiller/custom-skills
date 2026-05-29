#!/usr/bin/env python3
"""
Sleep-Time Compute — Dream Agent for the Karpathy Wiki v3.

Implements the dream cycle as specified in DREAM_AGENT_V2.md:
  Phase 0: Budget allocation
  Phase 1: Extract — read new/updated docs from ClawMem or raw/
  Phase 2: Refine — confidence scoring + council escalation
  Phase 3: Compile — write/update wiki pages with YAML frontmatter
  Phase 4: Pattern Detect — repeated tasks → SKILL.md
  Phase 5: Re-index — trigger ClawMem reindex
  Phase 6: Improve — vault quality improvement engine (embedding-guided)

Trigger: systemd idle timer (via scheduler.py)
Budget: idle_seconds × 0.25, capped at 7200s

Inspired by Letta's sleep-time compute pattern:
  https://docs.letta.com/guides/agents/architectures/sleeptime/
Adapted from Hermes GEPA self-evolution loop.
"""

import os
import sys
import json
import time
import hashlib
import re
import subprocess
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, date, timezone
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field, asdict

# ─── Configuration ───────────────────────────────────────────────
AI_WIKI = Path(os.environ.get("AI_WIKI", Path.home() / "ai-wiki"))
RAW_DIR = AI_WIKI / "raw"
WIKI_DIR = AI_WIKI / "pages"
CONCEPTS_DIR = WIKI_DIR / "concepts"
ENTITIES_DIR = WIKI_DIR / "entities"
SOURCES_DIR = WIKI_DIR / "sources"
QUERIES_DIR = WIKI_DIR / "queries"
INDEX_FILE = WIKI_DIR / "index.md"
LOG_FILE = WIKI_DIR / "log.md"
META_DIR = AI_WIKI / ".meta"
SKILL_PATTERNS_FILE = META_DIR / "skill_patterns.json"
INTAKE_LOG_FILE = META_DIR / "intake_log.jsonl"

# Pi skills directory (canonical store for auto-generated skills)
PI_SKILLS_DIR = Path(os.environ.get("PI_SKILLS_DIR", Path.home() / ".pi" / "agent" / "skills"))
# Ante skills directory (when running under Ante)
ANTE_SKILLS_DIR = Path(os.environ.get("ANTE_SKILLS_DIR", Path.home() / ".config" / "ante" / "skills"))
# Internal skill reference directory
WIKI_SKILLS_DIR = META_DIR / "skills"

# ClawMem REST API
CLAWMEM_URL = os.environ.get("CLAWMEM_URL", "http://localhost:7438")
CLAWMEM_COLLECTION = os.environ.get("CLAWMEM_COLLECTION", "wiki")

# Thresholds
SKILL_CREATION_THRESHOLD = int(os.environ.get("SKILL_CREATION_THRESHOLD", "3"))
CONFIDENCE_AUTO = float(os.environ.get("CONFIDENCE_AUTO", "0.8"))
CONFIDENCE_FLAG = float(os.environ.get("CONFIDENCE_FLAG", "0.5"))
CONFIDENCE_REJECT = float(os.environ.get("CONFIDENCE_REJECT", "0.5"))
COUNCIL_RANGE = (float(os.environ.get("COUNCIL_LOW", "0.5")),
                 float(os.environ.get("COUNCIL_HIGH", "0.6")))

# Improvement engine defaults
IMPROVEMENT_BUDGET_RATIO = float(os.environ.get("IMPROVEMENT_BUDGET_RATIO", "0.33"))
MAX_ITERATIONS_PER_DOC = int(os.environ.get("MAX_ITERATIONS_PER_DOC", "10"))
MEANING_PRESERVATION_THRESHOLD = float(os.environ.get("MEANING_PRESERVATION_THRESHOLD", "0.80"))
CONVERGENCE_THRESHOLD = float(os.environ.get("CONVERGENCE_THRESHOLD", "0.01"))

ALL_DIRS = [RAW_DIR, CONCEPTS_DIR, ENTITIES_DIR, SOURCES_DIR, QUERIES_DIR,
            META_DIR, PI_SKILLS_DIR, WIKI_SKILLS_DIR]

# ─── Data Classes ────────────────────────────────────────────────

@dataclass
class Budget:
    total_seconds: float
    intake: float = 0.0
    refine: float = 0.0
    compile: float = 0.0
    improve: float = 0.0
    lint: float = 0.0

@dataclass
class Claim:
    text: str
    source_docid: str
    source_filename: str
    category: str = "note"
    self_consistency: float = 0.0
    source_freshness: float = 0.0
    cross_ref_agreement: float = 0.0
    evidence_count: int = 0
    confidence: float = 0.0
    entities: list = field(default_factory=list)
    concepts: list = field(default_factory=list)

@dataclass
class DreamReport:
    timestamp: str = ""
    duration: float = 0.0
    budget_used: float = 0.0
    sources_scanned: int = 0
    sources_processed: int = 0
    claims_extracted: int = 0
    claims_accepted: int = 0
    claims_flagged: int = 0
    claims_rejected: int = 0
    councils_convened: int = 0
    pages_created: int = 0
    pages_updated: int = 0
    patterns_detected: int = 0
    skills_created: int = 0
    improvements_made: int = 0
    lint_issues: list = field(default_factory=list)
    errors: list = field(default_factory=list)

# ─── Helpers ─────────────────────────────────────────────────────

def ensure_dirs():
    for d in ALL_DIRS:
        d.mkdir(parents=True, exist_ok=True)
    for f, content in [
        (INDEX_FILE, "# Wiki Index\n\nAuto-maintained by dream agent.\n"),
        (LOG_FILE, f"# Wiki Log\n\n## {date.today().isoformat()} | create | Wiki initialized\n"),
    ]:
        if not f.exists():
            f.write_text(content)

def log_action(action: str, detail: str = ""):
    """Append to immutable log.md."""
    entry = f"## {date.today().isoformat()} | {action} | {detail}\n"
    with open(LOG_FILE, "a") as f:
        f.write(entry)

def json_get(url: str, timeout: float = 5.0) -> dict | None:
    """GET JSON from ClawMem REST API."""
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError,
            json.JSONDecodeError, ConnectionRefusedError) as e:
        return None

def json_post(url: str, data: dict, timeout: float = 10.0) -> dict | None:
    """POST JSON to ClawMem REST API."""
    try:
        body = json.dumps(data).encode()
        req = urllib.request.Request(url, data=body,
                                     headers={"Content-Type": "application/json",
                                              "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError,
            json.JSONDecodeError, ConnectionRefusedError) as e:
        return None

def clawmem_available() -> bool:
    """Check if ClawMem REST API is reachable."""
    result = json_get(f"{CLAWMEM_URL}/health", timeout=2.0)
    return result is not None

# ─── Phase 0: Budget Allocation ──────────────────────────────────

def calc_refinement_state() -> float:
    """Estimate how refined the wiki is (0.0 = raw, 1.0 = maximally refined)."""
    total_pages = 0
    pages_with_confidence = 0
    total_confidence = 0.0

    for page_dir in [CONCEPTS_DIR, ENTITIES_DIR, SOURCES_DIR]:
        if page_dir.exists():
            for f in page_dir.glob("*.md"):
                total_pages += 1
                content = f.read_text()
                m = re.search(r'confidence:\s*([\d.]+)', content)
                if m:
                    pages_with_confidence += 1
                    total_confidence += float(m.group(1))

    if total_pages == 0:
        return 0.0

    coverage = pages_with_confidence / total_pages if total_pages > 0 else 0.0
    avg_confidence = total_confidence / pages_with_confidence if pages_with_confidence > 0 else 0.0
    return coverage * avg_confidence

def allocate_budget(idle_seconds: float) -> Budget:
    """
    Phase 0: Allocate time budget based on idle time and wiki refinement state.

    Budget = idle_seconds × 0.25, capped at 7200s.
    Intake ratio decreases as wiki matures.
    """
    total_budget = min(idle_seconds * 0.25, 7200.0)
    b = Budget(total_seconds=total_budget)

    refinement = calc_refinement_state()
    intake_ratio = max(0.33, 0.80 - (0.50 * refinement))

    intake_budget = total_budget * intake_ratio
    refine_budget = total_budget * (1 - intake_ratio)

    # Sub-allocate within refinement budget
    compile_share = 0.40
    improve_share = 0.50
    lint_share = 0.10

    b.intake = intake_budget
    b.refine = refine_budget
    b.compile = refine_budget * compile_share
    b.improve = refine_budget * improve_share
    b.lint = refine_budget * lint_share

    return b

# ─── Phase 1: Extract ────────────────────────────────────────────

def extract_from_clawmem(report: DreamReport, budget: Budget) -> list[Claim]:
    """
    Extract new/updated documents from ClawMem REST API.
    Falls back to raw/ file scanning if ClawMem unavailable.
    """
    start = time.time()
    claims = []

    if clawmem_available():
        try:
            # Get stats to find new docs
            stats = json_get(f"{CLAWMEM_URL}/stats", timeout=5.0)
            if stats:
                # Try to list recent documents
                docs = json_post(f"{CLAWMEM_URL}/search", {
                    "query": "", "limit": 50, "sort": "-created"
                }, timeout=10.0)
                if docs and isinstance(docs, list):
                    report.sources_scanned = len(docs)
                    for doc in docs:
                        if time.time() - start > budget.intake:
                            break
                        docid = doc.get("id") or doc.get("docid", "")
                        if not docid:
                            continue
                        full = json_get(f"{CLAWMEM_URL}/documents/{docid}", timeout=5.0)
                        if full and full.get("content"):
                            c = _extract_claim_from_document(full, docid)
                            if c:
                                claims.append(c)
                    report.sources_processed = len(claims)
        except Exception as e:
            report.errors.append(f"clawmem_extract: {e}")

    # Fallback: scan raw/ for unprocessed files
    if not claims and RAW_DIR.exists():
        report.errors.append("ClawMem unavailable, falling back to raw/ scan")
        return _extract_from_raw(report, budget)

    return claims

def _extract_claim_from_document(doc: dict, docid: str) -> Claim | None:
    """Parse a ClawMem document into a Claim."""
    content = doc.get("content", "")
    if not content or len(content.strip()) < 50:
        return None

    title = doc.get("title", "") or content.split("\n")[0][:80]
    category = doc.get("content_type", "note")

    # Extract entities (uppercase words, 3+ chars)
    entities = list(set(
        w.strip(",.!?;:\"'()[]{}") for w in content.split()
        if len(w.strip(",.!?;:\"'()[]{}")) > 2
        and w.strip(",.!?;:\"'()[]{}")[0].isupper()
        and w.strip(",.!?;:\"'()[]{}") not in ("The", "This", "That", "We", "It", "I")
    ))

    # Extract concepts (tech keywords)
    tech_keywords = {"python", "typescript", "react", "rust", "docker", "postgres",
                     "redis", "kubernetes", "aws", "api", "cli", "git", "mcp",
                     "sqlite", "llm", "rag", "agent", "vector"}
    concepts = [kw for kw in tech_keywords if kw in content.lower()]

    return Claim(
        text=content,
        source_docid=docid,
        source_filename=doc.get("source", f"clawmem-{docid[:8]}"),
        category=category,
        entities=entities,
        concepts=concepts,
    )

def _extract_from_raw(report: DreamReport, budget: Budget) -> list[Claim]:
    """Fallback: scan raw/ for unprocessed files."""
    start = time.time()
    claims = []

    # Find already-processed files
    processed = set()
    if INTAKE_LOG_FILE.exists():
        for line in INTAKE_LOG_FILE.read_text().strip().split("\n"):
            if line:
                try:
                    entry = json.loads(line)
                    processed.add(entry.get("filename", ""))
                except json.JSONDecodeError:
                    pass

    unprocessed = []
    for f in sorted(RAW_DIR.glob("*")):
        if f.is_file() and f.suffix in (".md", ".txt", ".json", ".jsonl"):
            if f.name not in processed:
                unprocessed.append(f)

    report.sources_scanned = len(unprocessed)

    for f in unprocessed:
        if time.time() - start > budget.intake:
            break
        content = f.read_text(encoding="utf-8", errors="replace")
        if len(content.strip()) < 20:
            continue

        # Log intake
        with open(INTAKE_LOG_FILE, "a") as log:
            log.write(json.dumps({"filename": f.name, "size": len(content),
                                   "timestamp": datetime.now().isoformat()}) + "\n")

        c = Claim(
            text=content,
            source_docid=f"raw-{f.stem}",
            source_filename=f.name,
            category="note",
        )
        claims.append(c)

    report.sources_processed = len(claims)
    return claims

# ─── Phase 2: Refine ─────────────────────────────────────────────

def refine_claim(claim: Claim, budget_remaining: float) -> tuple[Claim, bool]:
    """
    Phase 2: Score claim confidence via deliberative refinement.

    Returns (claim, accepted) where accepted is:
      True  → confidence >= CONFIDENCE_AUTO
      False → confidence < CONFIDENCE_AUTO (flagged or rejected)
    """
    # 1. Self-consistency: simple heuristic based on internal contradiction markers
    text = claim.text.lower()
    contradiction_markers = ["however", "but", "on the other hand", "although",
                             "despite", "nevertheless", "alternatively"]
    has_contradiction = any(m in text for m in contradiction_markers)
    consistency_score = 0.6 if has_contradiction else 0.95

    # 2. Source freshness
    age_estimate = _estimate_source_age(claim.source_filename)
    freshness = max(0.0, 1.0 - age_estimate / 365.0)

    # 3. Cross-reference agreement
    agreement = _check_cross_ref_agreement(claim)

    # 4. Evidence count bonus
    evidence_bonus = min(1.0, len(claim.entities) / 5.0)

    # Weighted confidence
    confidence = (
        0.35 * consistency_score +
        0.25 * freshness +
        0.25 * agreement +
        0.15 * evidence_bonus
    )
    claim.confidence = round(confidence, 3)
    claim.self_consistency = consistency_score
    claim.source_freshness = freshness
    claim.cross_ref_agreement = agreement
    claim.evidence_count = len(claim.entities)

    # Decision
    if confidence >= CONFIDENCE_AUTO:
        return claim, True
    elif confidence >= CONFIDENCE_FLAG:
        # Council escalation trigger
        if (COUNCIL_RANGE[0] <= confidence <= COUNCIL_RANGE[1]
                and _contradicts_existing_high_confidence(claim)):
            return claim, _convene_council(claim)
        return claim, False  # Flagged for user review
    else:
        return claim, False  # Rejected

def _estimate_source_age(filename: str) -> float:
    """Estimate source age in days from filename patterns."""
    date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', filename)
    if date_match:
        try:
            y, m, d = int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3))
            source_date = date(y, m, d)
            delta = date.today() - source_date
            return delta.days
        except ValueError:
            pass
    return 90.0  # Default: assume 3 months old

def _check_cross_ref_agreement(claim: Claim) -> float:
    """Check fraction of related wiki pages that don't contradict."""
    related = set()
    for entity in claim.entities:
        slug = entity.lower().replace(" ", "-").replace("_", "-")
        for page_dir in [CONCEPTS_DIR, ENTITIES_DIR]:
            candidate = page_dir / f"{slug}.md"
            if candidate.exists():
                related.add(candidate)

    if not related:
        return 1.0

    contradictions = 0
    for page_file in related:
        content = page_file.read_text().lower()
        claim_lower = claim.text.lower()
        # Simple signal: claim keywords absent from related page
        key_terms = [w for w in claim_lower.split() if len(w) > 5][:5]
        if not any(term in content for term in key_terms):
            contradictions += 1

    return 1.0 - (contradictions / len(related))

def _contradicts_existing_high_confidence(claim: Claim) -> bool:
    """Check if claim contradicts an existing high-confidence wiki page."""
    high_conf_pages = []
    for page_dir in [CONCEPTS_DIR, ENTITIES_DIR]:
        if page_dir.exists():
            for f in page_dir.glob("*.md"):
                content = f.read_text()
                m = re.search(r'confidence:\s*([\d.]+)', content)
                if m and float(m.group(1)) >= 0.8:
                    high_conf_pages.append(f)

    for page_file in high_conf_pages:
        content = page_file.read_text().lower()
        claim_lower = claim.text.lower()
        # Check for strong disagreement signals
        negation_signals = ["does not", "is not", "should not", "wrong", "incorrect",
                            "contradicts", "outdated"]
        if any(s in claim_lower for s in negation_signals):
            return True
    return False

def _convene_council(claim: Claim) -> bool:
    """
    Two-model adversarial deliberation stub.
    In production, this calls two LLMs to argue for/against the claim.
    For now, returns True (conservatively accept) and logs the event.
    """
    log_action("council", f"claim='{claim.text[:60]}...' confidence={claim.confidence}")
    return True

# ─── Phase 3: Compile ────────────────────────────────────────────

def compile_to_wiki(claims: list[Claim], report: DreamReport):
    """
    Phase 3: Write/update wiki pages from accepted claims.
    Creates new pages or updates existing ones with YAML frontmatter and [[wikilinks]].
    """
    for claim in claims:
        page_path, is_new = _find_or_create_page(claim)

        existing_content = page_path.read_text() if page_path.exists() else ""
        yaml_header = _build_frontmatter(claim, page_path, existing_content)

        body = _build_body(claim, existing_content)

        page_path.write_text(f"---\n{yaml_header}---\n\n# {claim.text.split(chr(10))[0][:80]}\n\n{body}")

        if is_new:
            report.pages_created += 1
            log_action("compile", f"created {page_path.relative_to(AI_WIKI)} (conf={claim.confidence})")
        else:
            report.pages_updated += 1
            log_action("improve", f"updated {page_path.relative_to(AI_WIKI)} (conf={claim.confidence})")

def _find_or_create_page(claim: Claim) -> tuple[Path, bool]:
    """Find best existing page or create new one."""
    # Try entities first
    for entity in claim.entities:
        slug = entity.lower().replace(" ", "-").replace("_", "-")
        candidate = ENTITIES_DIR / f"{slug}.md"
        if candidate.exists():
            return candidate, False

    # Try concepts
    for concept in claim.concepts:
        candidate = CONCEPTS_DIR / f"{concept}.md"
        if candidate.exists():
            return candidate, False

    # Create new entity page
    primary = (claim.entities[0] if claim.entities else claim.source_filename.split(".")[0])
    slug = primary.lower().replace(" ", "-").replace("_", "-")

    # Determine best directory
    if claim.concepts:
        target = CONCEPTS_DIR / f"{slug}.md"
    else:
        target = ENTITIES_DIR / f"{slug}.md"

    return target, True

def _build_frontmatter(claim: Claim, page_path: Path, existing: str) -> str:
    """Build YAML frontmatter with provenance."""
    today = date.today().isoformat()

    # Parse existing frontmatter
    existing_ym = {}
    ym_match = re.match(r'^---\n(.*?)\n---', existing, re.DOTALL)
    if ym_match:
        for line in ym_match.group(1).split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                existing_ym[k.strip()] = v.strip()

    sources_str = (f"  - clawmem://{claim.source_docid}\n" if claim.source_docid else "")
    wikilinks = []
    for entity in claim.entities[:5]:
        slug = entity.lower().replace(" ", "-").replace("_", "-")
        wikilinks.append(f"  - entities/{slug}.md")
    for concept in claim.concepts[:5]:
        slug = concept.lower().replace(" ", "-").replace("_", "-")
        if f"concepts/{slug}.md" not in wikilinks:
            wikilinks.append(f"  - concepts/{slug}.md")

    wikilinks_str = "\n".join(wikilinks) if wikilinks else ""

    status = "stable" if claim.confidence >= 0.8 else ("needs_review" if claim.confidence >= 0.5 else "draft")

    lines = [
        f"title: \"{existing_ym.get('title', page_path.stem.replace('-', ' ').title())}\"",
        f"created: \"{existing_ym.get('created', today)}\"",
        f"updated: \"{today}\"",
        f"tags: [{', '.join(claim.concepts[:3])}]" if claim.concepts else "tags: []",
        f"confidence: {claim.confidence}",
        f"status: {status}",
        "sources:",
        sources_str,
        "wikilinks:",
        wikilinks_str,
    ]
    return "\n".join(line for line in lines if line)

def _build_body(claim: Claim, existing: str) -> str:
    """Build wiki page body with key observations and cross-refs."""
    body_parts = []

    # Extract existing body (drop frontmatter)
    existing_body = re.sub(r'^---\n.*?\n---\n', '', existing, flags=re.DOTALL).strip()

    if existing_body:
        body_parts.append(existing_body)
        body_parts.append("\n---\n## Updated\n")
    else:
        body_parts.append("## Summary\n")

    body_parts.append(claim.text.strip()[:500])
    body_parts.append(f"\n\n_Source: `{claim.source_filename}` (confidence: {claim.confidence})_\n")

    if claim.entities:
        body_parts.append("\n### Related Entities\n")
        for e in claim.entities[:10]:
            slug = e.lower().replace(" ", "-").replace("_", "-")
            body_parts.append(f"- [[entities/{slug}|{e}]]\n")

    if claim.concepts:
        body_parts.append("\n### Related Concepts\n")
        for c in claim.concepts[:10]:
            slug = c.lower().replace(" ", "-").replace("_", "-")
            body_parts.append(f"- [[concepts/{slug}|{c.title()}]]\n")

    return "".join(body_parts)

# ─── Phase 4: Pattern Detect ─────────────────────────────────────

def detect_patterns(report: DreamReport, claims: list[Claim]):
    """
    Phase 4: Scan claims for repeated task patterns.
    When 3+ similar task completions detected, auto-create SKILL.md.
    """
    patterns = _load_skill_patterns()
    detected_types = set()

    for claim in claims:
        text = claim.text.lower()
        types_found = []

        if re.search(r'\b(review|pr |pull request|code review)\b', text):
            types_found.append("code-review")
        if re.search(r'\b(deploy|release|ship|publish)\b', text):
            types_found.append("deployment")
        if re.search(r'\b(test|spec|coverage|assert)\b', text):
            types_found.append("testing")
        if re.search(r'\b(debug|bug|error|crash|fix)\b', text):
            types_found.append("debugging")
        if re.search(r'\b(database|migration|schema|query)\b', text):
            types_found.append("database")
        if re.search(r'\b(api|endpoint|route|rest)\b', text):
            types_found.append("api-development")
        if re.search(r'\b(research|paper|arxiv|study)\b', text):
            types_found.append("research")

        for t in types_found:
            found = None
            for p in patterns["patterns"]:
                if p["type"] == t:
                    found = p
                    break
            if found:
                found["count"] += 1
                found["last_seen"] = date.today().isoformat()
                found["sources"].append(claim.source_filename)
            else:
                patterns["patterns"].append({
                    "type": t, "count": 1,
                    "first_seen": date.today().isoformat(),
                    "last_seen": date.today().isoformat(),
                    "sources": [claim.source_filename],
                    "skill_created": False,
                })
            detected_types.add(t)

    report.patterns_detected = len(detected_types)
    _save_skill_patterns(patterns)

    # Check threshold crossings
    for p in patterns["patterns"]:
        if p["count"] >= SKILL_CREATION_THRESHOLD and not p.get("skill_created"):
            _create_skill_from_pattern(p)
            p["skill_created"] = True
            report.skills_created += 1

    _save_skill_patterns(patterns)

def _load_skill_patterns() -> dict:
    if SKILL_PATTERNS_FILE.exists():
        try:
            return json.loads(SKILL_PATTERNS_FILE.read_text())
        except (json.JSONDecodeError, Exception):
            pass
    return {"patterns": [], "skills_created": []}

def _save_skill_patterns(patterns: dict):
    SKILL_PATTERNS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SKILL_PATTERNS_FILE.write_text(json.dumps(patterns, indent=2))

def _create_skill_from_pattern(pattern: dict):
    """Create reusable SKILL.md from repeated pattern. Mirrors existing logic."""
    task_type = pattern["type"]
    count = pattern["count"]

    templates = {
        "code-review": {
            "description": "Review code for quality, bugs, and best practices",
            "trigger": "User asks to review code, PR, or changes",
            "procedure": [
                "1. Read the diff or files being reviewed (use `read` or `bash git diff`)",
                "2. Check for: logic errors, security issues, edge cases, style violations",
                "3. Run tests: `npm test` or `pytest`",
                "4. Report findings grouped by severity",
            ],
            "pitfalls": ["Don't just approve — actually verify tests pass"],
        },
        "deployment": {
            "description": "Deploy code to staging or production environments",
            "trigger": "User asks to deploy, ship, or release",
            "procedure": [
                "1. Check git status — abort if dirty",
                "2. Run the build command: `npm run build`",
                "3. Run the full test suite",
                "4. Deploy using the project's deployment method",
                "5. Verify the deployment with a health check",
            ],
            "pitfalls": ["Never deploy from main without CI passing"],
        },
        "testing": {
            "description": "Write and run tests for code",
            "trigger": "User asks to write tests, add coverage, or verify behavior",
            "procedure": [
                "1. Identify the module/function to test",
                "2. Create test file following project conventions",
                "3. Write tests for: happy path, edge cases, error conditions",
                "4. Run the tests and fix any failures",
            ],
            "pitfalls": ["Don't modify source code to make tests pass — fix the test"],
        },
        "debugging": {
            "description": "Debug errors, crashes, and unexpected behavior",
            "trigger": "User reports a bug, error, or crash",
            "procedure": [
                "1. Reproduce the issue — get the exact error message",
                "2. Check recent changes with `git log --oneline -10`",
                "3. Isolate the failing component",
                "4. Add logging or use debugger to trace execution",
                "5. Fix the root cause, not the symptom",
                "6. Verify the fix and add a regression test",
            ],
            "pitfalls": ["Never commit debug logging or console.log statements"],
        },
        "database": {
            "description": "Work with databases, migrations, and schemas",
            "trigger": "User mentions database, migration, schema, or data",
            "procedure": [
                "1. Check current schema and migration status",
                "2. Plan changes with backward compatibility",
                "3. Write migration scripts",
                "4. Test migration on a copy of production data",
            ],
            "pitfalls": ["Never run destructive migrations without a backup"],
        },
    }

    tmpl = templates.get(task_type, {
        "description": f"Pattern detected: {task_type} (completed {count}x)",
        "trigger": f"User task matches {task_type} pattern",
        "procedure": ["1. Follow standard workflow for this task type"],
        "pitfalls": ["Verify results before declaring completion"],
    })

    skill_content = f"""---
name: auto-{task_type}
description: "{tmpl['description']}"
version: 1.0.0
source: "auto-generated by dream agent from {count} repeated task patterns"
tags: [{task_type}, auto-generated]
---

# {task_type.title().replace('-', ' ')}

Auto-generated skill based on {count} detected task patterns in session history.

## When to Use

{tmpl['trigger']}

## Procedure

{chr(10).join(tmpl['procedure'])}

## Pitfalls

{chr(10).join(f'- {p}' for p in tmpl['pitfalls'])}

## Verification

Tests must pass. The result must be demonstrable.
"""

    # Write to Pi's skills directory
    skill_dir = PI_SKILLS_DIR / f"auto-{task_type}"
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(skill_content)

    # Write wiki reference
    WIKI_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    (WIKI_SKILLS_DIR / f"auto-{task_type}.md").write_text(
        f"# Auto-Generated Skill: {task_type}\n\n"
        f"Created from {count} repeated task patterns.\n"
        f"Skill file at: `{skill_dir / 'SKILL.md'}`\n"
    )

    log_action("skill-created", f"auto-{task_type} ({count} patterns)")
    print(f"  ✓ Created skill: auto-{task_type} ({count} patterns)")

# ─── Phase 5: Re-index ───────────────────────────────────────────

def trigger_reindex(report: DreamReport):
    """
    Phase 5: Trigger ClawMem reindex after wiki writes.
    Falls back to local update if ClawMem unavailable.
    """
    if not clawmem_available():
        return

    try:
        result = json_post(f"{CLAWMEM_URL}/reindex", {"collection": CLAWMEM_COLLECTION},
                           timeout=30.0)
        if result:
            log_action("reindex", f"reindex triggered for {CLAWMEM_COLLECTION}")
    except Exception as e:
        report.errors.append(f"reindex: {e}")

# ─── Phase 6: Improve (Vault Quality Engine) ─────────────────────

def improve_wiki(report: DreamReport, budget: Budget):
    """
    Phase 6: Sleep-time vault improvement using embedding-guided iterative rewriting.

    Full implementation requires:
      - Running ClawMem embedding server (or external API)
      - S-tier reference library at META_DIR/references/
      - LLM endpoint for generating improvements

    This is a scaffolding implementation that:
      1. Identifies lowest-scoring documents by rubric heuristics
      2. Logs improvement candidates
      3. Applies simple structural fixes (missing frontmatter, broken wikilinks)
    """
    start = time.time()
    improved = 0

    candidates = _find_improvement_candidates()
    if not candidates:
        return

    print(f"  📝 {len(candidates)} improvement candidates found")

    for page_path, issues in candidates:
        if time.time() - start > budget.improve:
            break
        if improved >= 5:  # Per-cycle cap
            break

        content = page_path.read_text()

        # Fix missing confidence frontmatter
        if "confidence:" not in content:
            content = content.replace("---\n", "---\nconfidence: 0.5\n# auto-added by dream agent\n", 1)
            page_path.write_text(content)
            improved += 1
            report.improvements_made += 1
            log_action("improve", f"fixed missing confidence in {page_path.name}")
            continue

        # Fix broken update date
        date_match = re.search(r'updated:\s*"([^"]+)"', content)
        if date_match and date_match.group(1) != date.today().isoformat():
            content = content.replace(f'updated: "{date_match.group(1)}"',
                                     f'updated: "{date.today().isoformat()}"')
            page_path.write_text(content)
            improved += 1
            report.improvements_made += 1

    if improved:
        print(f"  ✓ {improved} documents improved")

def _find_improvement_candidates() -> list[tuple[Path, list[str]]]:
    """Find wiki pages that need improvement based on structural issues."""
    candidates = []
    for page_dir in [CONCEPTS_DIR, ENTITIES_DIR]:
        if not page_dir.exists():
            continue
        for f in page_dir.glob("*.md"):
            content = f.read_text()
            issues = []

            if "confidence:" not in content:
                issues.append("missing_confidence")
            if "status:" not in content:
                issues.append("missing_status")
            if "sources:" not in content:
                issues.append("missing_sources")

            # Check for broken wikilinks
            links = re.findall(r'\[\[([^\]]+)\]\]', content)
            for link in links:
                linked_path = link.replace(" ", "-").lower().lstrip("/")
                found = False
                for search_dir in [CONCEPTS_DIR, ENTITIES_DIR, SOURCES_DIR, QUERIES_DIR]:
                    if (search_dir / f"{linked_path}.md").exists():
                        found = True
                        break
                if not found:
                    issues.append(f"broken_link: [[{link}]]")

            if issues:
                candidates.append((f, issues))

    # Sort by priority: most issues first
    candidates.sort(key=lambda x: len(x[1]), reverse=True)
    return candidates

# ─── Lint ─────────────────────────────────────────────────────────

def lint_wiki(report: DreamReport):
    """Check wiki health: orphan pages, broken links, contradictions."""
    issues = {}

    # Check index covers all pages
    index_content = INDEX_FILE.read_text() if INDEX_FILE.exists() else ""
    for page_dir in [CONCEPTS_DIR, ENTITIES_DIR, SOURCES_DIR, QUERIES_DIR]:
        if page_dir.exists():
            for f in page_dir.glob("*.md"):
                if f.stem not in index_content and f.stem != "index":
                    issues.setdefault("orphans", []).append(str(f.relative_to(AI_WIKI)))

    # Check for broken wikilinks
    for page_dir in [CONCEPTS_DIR, ENTITIES_DIR, SOURCES_DIR]:
        if page_dir.exists():
            for f in page_dir.glob("*.md"):
                content = f.read_text()
                links = re.findall(r'\[\[([^\]]+)\]\]', content)
                for link in links:
                    linked_path = link.replace(" ", "-").lower().lstrip("/")
                    found = False
                    for sd in [CONCEPTS_DIR, ENTITIES_DIR, SOURCES_DIR, QUERIES_DIR]:
                        if (sd / f"{linked_path}.md").exists():
                            found = True
                            break
                    if not found:
                        issues.setdefault("broken_links", []).append(f"{f.name} -> [[{link}]]")

    # Check for stale confidence (draft status older than 30 days)
    today = date.today()
    for page_dir in [CONCEPTS_DIR, ENTITIES_DIR]:
        if page_dir.exists():
            for f in page_dir.glob("*.md"):
                content = f.read_text()
                if "status: draft" in content:
                    m = re.search(r'created:\s*"([^"]+)"', content)
                    if m:
                        try:
                            created = date.fromisoformat(m.group(1))
                            if (today - created).days > 30:
                                issues.setdefault("stale", []).append(f"{f.name} (draft for {(today - created).days}d)")
                        except ValueError:
                            pass

    for key, vals in issues.items():
        for v in vals:
            report.lint_issues.append(f"{key}: {v}")

# ─── Git Integration ──────────────────────────────────────────────

def git_commit(message: str, wiki_dir: str | None = None):
    """Commit wiki changes with descriptive message."""
    cwd = wiki_dir or str(AI_WIKI)
    try:
        subprocess.run(["git", "add", "-A"], cwd=cwd, capture_output=True, timeout=10)
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=cwd, capture_output=True, timeout=10
        )
        if result.returncode != 0:  # There are changes
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=cwd, capture_output=True, timeout=30
            )
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        print(f"  ⚠ git commit failed: {e}")
    return False

# ─── Main Dream Cycle ────────────────────────────────────────────

def run_dream_cycle(idle_seconds: float = 600, verbose: bool = True) -> DreamReport:
    """Execute one complete dream cycle across all phases."""
    ensure_dirs()
    start_time = time.time()
    report = DreamReport(timestamp=datetime.now().isoformat())

    if verbose:
        print("🌙 Dream agent waking...")

    # Phase 0: Budget allocation
    budget = allocate_budget(idle_seconds)
    if verbose:
        print(f"  ⏱ Budget: {budget.total_seconds:.0f}s total "
              f"(intake={budget.intake:.0f}s, compile={budget.compile:.0f}s, "
              f"improve={budget.improve:.0f}s, lint={budget.lint:.0f}s)")

    # Phase 1: Extract
    if verbose:
        print(f"  📥 Phase 1: Extract (budget: {budget.intake:.0f}s)")
    claims = extract_from_clawmem(report, budget)
    if verbose:
        print(f"    → {len(claims)} raw claims extracted")

    if not claims:
        if verbose:
            print("  ℹ  No new content to process. Skipping to lint.")
        # Still lint
        lint_wiki(report)
        git_commit(f"cycle: lint — {len(report.lint_issues)} issues found")
        report.duration = round(time.time() - start_time, 2)
        report.budget_used = budget.total_seconds
        if verbose:
            print(f"  ✅ Dream cycle complete ({report.duration}s, 0 claims)")
        return report

    # Phase 2: Refine
    if verbose:
        print(f"  🔍 Phase 2: Refine ({len(claims)} claims)")
    accepted = []
    flagged = []
    for claim in claims:
        refined, is_accepted = refine_claim(claim, budget.refine / len(claims))
        if is_accepted:
            accepted.append(refined)
            report.claims_accepted += 1
        elif refined.confidence >= CONFIDENCE_FLAG:
            flagged.append(refined)
            report.claims_flagged += 1
        else:
            report.claims_rejected += 1

    if verbose:
        print(f"    → {len(accepted)} accepted, {len(flagged)} flagged, {report.claims_rejected} rejected")

    # Phase 3: Compile
    if verbose:
        print(f"  ✍️  Phase 3: Compile ({len(accepted)} claims to wiki)")
    compile_to_wiki(accepted, report)
    if verbose:
        print(f"    → {report.pages_created} created, {report.pages_updated} updated")
    if accepted:
        git_commit(f"compile: {report.pages_created} created, {report.pages_updated} updated — "
                   f"{report.claims_accepted} claims accepted (avg conf)")

    # Phase 4: Pattern Detect
    if verbose:
        print(f"  🧩 Phase 4: Pattern Detect ({len(claims)} claims scanned)")
    detect_patterns(report, claims)
    if report.skills_created:
        git_commit(f"create: {report.skills_created} auto-skills from patterns")

    # Phase 5: Re-index
    if verbose:
        print(f"  🔄 Phase 5: Re-index")
    trigger_reindex(report)

    # Phase 6: Improve
    if budget.improve > 10:
        if verbose:
            print(f"  📈 Phase 6: Improve (budget: {budget.improve:.0f}s)")
        improve_wiki(report, budget)
        if report.improvements_made:
            git_commit(f"improve: {report.improvements_made} documents")

    # Lint
    lint_wiki(report)
    if report.lint_issues:
        if verbose:
            print(f"  ⚠  Lint: {len(report.lint_issues)} issues found")
            for issue in report.lint_issues[:5]:
                print(f"    - {issue}")
            if len(report.lint_issues) > 5:
                print(f"    ... and {len(report.lint_issues) - 5} more")

    report.duration = round(time.time() - start_time, 2)
    report.budget_used = budget.total_seconds - budget.total_seconds  # Track used

    if verbose:
        print(f"  ✅ Dream cycle complete ({report.duration}s)")
        print(f"     Claims: {len(claims)} → {report.claims_accepted} accepted, "
              f"{report.claims_flagged} flagged, {report.claims_rejected} rejected")
        print(f"     Pages: {report.pages_created} created, {report.pages_updated} updated")
        print(f"     Skills: {report.skills_created} created from {report.patterns_detected} patterns")
        if report.improvements_made:
            print(f"     Improvements: {report.improvements_made}")

    # Log the cycle
    log_action("dream-cycle",
               f"claims={len(claims)}/{report.claims_accepted}/{report.claims_flagged}/"
               f"{report.claims_rejected}, pages={report.pages_created}+{report.pages_updated}, "
               f"skills={report.skills_created}, improved={report.improvements_made}, "
               f"lint={len(report.lint_issues)}, duration={report.duration}s")

    return report

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Karpathy Wiki Dream Agent v3")
    parser.add_argument("--idle", type=int, default=600,
                        help="Idle seconds for budget calculation (default: 600)")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output")
    args = parser.parse_args()

    report = run_dream_cycle(idle_seconds=args.idle, verbose=not args.quiet)
    print(json.dumps(asdict(report), indent=2))
