---
date: 2026-05-19
ver: 1.0.0
tags: [vault, self-improvement, quality, sleep-time, s-tier, reference]
---

# Vault Content Self-Improvement Engine

## Vision

The vault is not just memory — it contains project plans, PRDs, research notes,
transcripts, tutorials, code, and instructions. During sleep-time, the dream agent
classifies each document by type, compares it against S-tier reference examples,
and iteratively improves it toward that quality target.

A project file dropped into the vault today is measurably better in six months —
better structured, better argued, better referenced. Documents that reach
"optimal" score can be flagged for proactive execution: the agent builds the
project, writes the code, or drafts the paper.

## Architecture

The core loop uses **embedding vector distance as the loss function**, with **rubric-based gap analysis for targeted improvements**. This mirrors how gradient descent trains a model — but applied to document quality.

### Prior Art: FORGE Methodology

This engine builds on the **FORGE** (Feedback-Orchestrated Refinement with Grounded
Evaluation) methodology already present in the user's vault. FORGE defines:

- **V(X, Y, S)**: X evaluation passes, Y branching explorations, S synthesis rounds
- **Profiles**: Lite V(3,1,0), Standard V(8,3,1), Deep V(12,5,2), Exhaustive V(15,5,3)
- **Modes**: CREATE (write → Lite → return), REFINE (analyze → FORGE profile → return)
- **Strategies**: LINEAR (fix/correct/validate), BRANCHING (explore/alternatives)

The improvement loop below maps to FORGE Deep profile when improving high-stakes
documents, and FORGE Lite for routine content.

### Prior Art: Fractal Synthesis Protocol

The **Fractal Synthesis Protocol (FSP)** frames the vault as "shared RAM" for
LLM-human collaboration. Its seven pillars include Adversarial Council Validation
and Self-Referential Improvement — both directly implemented in this engine.
See: `old vault/Fractal Synthesis Protocol...md` in the user's Obsidian vault.

```
Raw vault file (any type)
    │
    ▼
Phase 1: CLASSIFY
    │  Determine document type (8 types) + current quality score
    ▼
Phase 2: LOAD REFERENCE
    │  Fetch S-tier example for that type (Nobel paper, Pulitzer, etc.)
    ▼
Phase 3: EMBED & MEASURE
    │  Embed both documents via ClawMem's embedding server
    │  Calculate cosine distance as "loss" metric
    │  Run rubric scoring for interpretable gap analysis
    ▼
Phase 4: IMPROVE
    │  Generate targeted improvements from rubric gaps
    │  LLM rewrites to move embedding closer to reference
    ▼
Phase 5: RE-EMBED & CHECK
    │  Re-embed improved version
    │  IF distance shrank AND meaning preserved (cosine >0.80 with original):
    │    Accept improvement
    │  ELSE: try different approach or skip
    ▼
Phase 6: ITERATE
    │  Repeat Phases 3-5 until convergence (improvement <0.01/iteration)
    │  Max 10 iterations per document per cycle
    │  Then move to next document
    ▼
Phase 7: FLAG FOR EXECUTION (if optimal)
    │  "This project plan is ready. Proceed to build."
```

### The Loss Function

```
loss = cosine_distance(embed(vault_doc), embed(reference))
improvement_accepted = (new_loss < old_loss) AND (cosine_sim(new_doc, old_doc) > 0.80)
```

The "training signal" is the vector distance to the S-tier reference.
The "gradient" is the LLM's rewrite.
The "loss function" is cosine distance.
The "regularization" is the meaning preservation threshold.

This is NOT fine-tuning a model. This is improving document quality via
iterative LLM rewriting with embedding-based quality measurement. All
compute happens at inference time against frozen embedding + LLM models.

## Document Classification

Documents are classified into one of the following types. Classification uses
the same two-tier system as the intent router: heuristic regex first (file path
patterns, frontmatter tags, content markers), then LLM refinement for ambiguous
cases.

| Type | Examples | S-Tier Reference | Quality Dimensions |
|------|----------|-----------------|-------------------|
| **Project Plan / PRD** | Product specs, architecture docs, implementation plans | Apple design docs, Stripe API docs, FAANG internal specs | Completeness, clarity, timeline realism, dependency mapping, risk identification |
| **Research Note** | Literature surveys, experiment logs, analysis | Nobel-winning papers, Nature/Science articles | Citation quality, argument structure, evidence strength, reproducibility |
| **Instruction / Tutorial** | How-to guides, setup docs, runbooks | Apple Human Interface Guidelines, Stripe docs, Divio-style docs | Step clarity, prerequisites, examples, troubleshooting, beginner-friendliness |
| **Code** | Scripts, libraries, implementations | Well-documented OSS (SQLite source, Redis, etc.) | Readability, docs, error handling, test coverage, API design |
| **Narrative / Writing** | Blog posts, articles, documentation | Pulitzer-winning features, Strunk & White style | Structure, voice, pacing, evidence, hook, conclusion |
| **Raw Transcript** | LLM conversation logs | N/A (extract only) | Not improved — only decisions/patterns extracted |
| **Configuration** | .env, config files, docker-compose | Reference implementations | Completeness, security, documented overrides |
| **Frontmatter-Only** | Index files, stubs | N/A | Minimal — only metadata enriched |

## S-Tier Reference Library

The reference library lives at `wiki/.meta/references/` and contains canonical
examples for each document type. These are curated (not auto-generated) to
ensure quality.

```
wiki/.meta/references/
├── project-plan/
│   └── Stripe-API-design-guide.md      # S-tier spec structure
├── research-note/
│   └── Nobel-2024-physics-summary.md   # S-tier argument structure
├── tutorial/
│   └── Apple-HIG-principles.md         # S-tier instructional clarity
├── code/
│   └── sqlite-src-readme.md            # S-tier code documentation
└── narrative/
    └── Pulitzer-feature-example.md     # S-tier narrative structure
```

References are provided by the user or sourced from public domain / permissive
license works. The system does not fetch copyrighted material without permission.

## Quality Scoring (Hybrid: Vector Distance + Rubric)

Two complementary scoring methods are used together.

### Method 1: Embedding Vector Distance (Overall Quality Signal)

Documents and references are embedded using ClawMem's embedding server.
The cosine distance between them is the "loss function":

```python
import numpy as np

def embedding_loss(doc_embedding, ref_embedding):
    """0.0 = identical to reference, 1.0 = orthogonal, >1.0 = opposite."""
    cos_sim = np.dot(doc_embedding, ref_embedding) / (np.linalg.norm(doc_embedding) * np.linalg.norm(ref_embedding))
    return 1.0 - cos_sim  # 0 = identical, 2 = opposite
```

### Method 2: Rubric Scoring (Interpretable Gap Analysis)

Each document type has a weighted rubric. The rubric generates targeted
improvement suggestions that vector distance alone cannot provide.

```python
quality_dimensions = {
    "completeness": 0.25,        # All sections present
    "clarity": 0.20,             # Language precision
    "timeline_realism": 0.15,    # Feasible milestones
    "dependency_mapping": 0.15,  # Dependencies identified
    "risk_identification": 0.15, # Risks called out
    "execution_ready": 0.10,     # Could a dev act on this?
}

def score_document(doc, reference):
    """Compare document against reference, return 0-100 score and gap analysis."""
    scores = {}
    gaps = []
    for dimension, weight in quality_dimensions.items():
        score = assess_dimension(doc, reference, dimension)
        scores[dimension] = score
        if score < 0.7:
            gaps.append({"dimension": dimension, "score": score, "suggestion": generate_improvement(doc, reference, dimension)})
    overall = sum(scores[d] * weight for d, weight in quality_dimensions.items())
    return overall * 100, gaps
```

### How They Combine

```
embedding_loss = 0.23 (doc is fairly close to the reference already)
rubric_score  = 64/100 (but missing risk assessment and dependency mapping)

→ The improvement prompt includes BOTH signals:
  "The embedding distance is 0.23 (target < 0.15). 
   Specific gaps: risk assessment (score 0.3), dependency mapping (score 0.4).
   Suggested improvements: [rubric-generated suggestions]."
```

## Phases Detail

### Phase 1: Classify

```
WHEN dream agent encounters a file in raw/ or detects a new/modified file
  during a scan of the ClawMem vault,
THE dream agent SHALL classify the document into one of the types above.
THE classifier SHALL use the same two-tier system as the intent router:
  1. Heuristic rules (file path, frontmatter tags, content markers) — instant
  2. LLM refinement for ambiguous cases — using hardware-adaptive model
```

### Phase 2: Load Reference

```
WHEN a document is classified,
THE dream agent SHALL look up the S-tier reference for that type in
  wiki/.meta/references/.
IF no reference exists,
THE dream agent SHALL skip improvement for that type and log the gap.
```

### Phase 3: Compare

```
THE dream agent SHALL score the document against the reference using
  the type-specific rubric.
THE output SHALL be a gap analysis: for each quality dimension that scores
  below 0.7, a specific suggestion for improvement.
```

### Phase 4: Improve

```
THE dream agent SHALL apply improvements incrementally — never a full rewrite.
Each improvement SHALL be:
  - Specific (not "improve clarity" but "add a prerequisites section before step 1")
  - Minimal (change one section at a time)
  - Traceable (changes committed with message describing the improvement)
```

### Phase 5: Re-score

```
AFTER each improvement,
THE dream agent SHALL re-score the document.
IF score < threshold (default 80),
  THE dream agent SHALL loop back to Phase 3 for the next gap.
IF score >= threshold,
  THE dream agent SHALL mark the document as "improved to quality target."
```

### Phase 6: Flag for Execution

```
WHEN a document reaches "optimal" score (>= 90),
THE dream agent MAY flag it for proactive execution.
  - Project plans → agent builds the MVP
  - PRDs → agent implements the feature
  - Research notes → agent drafts the paper
  - Tutorials → agent validates the steps

Flagged documents appear in the morning report:
  "Your project plan for AcmeAuth reached optimal quality.
   Starting implementation as a background task."
```

## Integration with Existing Systems

### Git-Backed Wiki (MemFS-style)

All improvements go through git:

```bash
cd wiki/pages/
git add concepts/project-acme.md
git commit -m "improve: AcmeAuth project plan — added risk assessment section (score 72→81)"
```

Full version history means every improvement is traceable and revertible.

### ClawMem Reindex

After each improvement cycle, the dream agent triggers ClawMem reindex
so the improved document is immediately searchable.

### MemVid Encoding

The monthly MemVid encode captures the state of all documents at that
point — including improvements. Each month's archive is a snapshot of
the vault's quality progression.

## Scheduler Integration

This engine runs as part of the dream agent's time budget allocation:

```
Budget split:
  33% → Intake (process new raw sources)
  33% → Compilation (write wiki pages from observations)
  33% → Improvement (upgrade existing vault documents)
   1% → Lint (health checks)
```

The improvement phase targets the lowest-scoring documents first
(prioritize biggest quality gaps).

## User Stories

### Story 1: Project plan improves over time
User drops `projects/ideas/acme-auth.md` into the vault — rough, 3 paragraphs.
Month 1: Dream agent classifies it as "project plan." Scores it at 34/100.
         Adds a timeline section (34→52).
Month 2: Adds risk assessment (52→68).
Month 3: Adds dependency mapping, references Stripe's API design guide (68→84).
Month 4: Fills remaining clarity gaps (84→92). Flagged as optimal.
         Agent proactively builds the MVP as a background task.
User opens the morning report: "AcmeAuth is live at acmeauth.preview.app"

### Story 2: Research note → publishable draft
User ingests transcript of a research conversation.
Dream agent classifies it as "research note," scores it 28/100.
Over iterative cycles, compares against Nobel paper structure:
  - Adds abstract (28→45)
  - Formalizes methodology section (45→60)
  - Adds literature citations from ClawMem's existing knowledge (60→75)
  - Strengthens conclusion with evidence from results (75→88)
User can publish directly — the structure is peer-review ready.

### Story 3: Agent proactively completes projects
User has a half-baked PRD for a CLI tool in the vault.
Dream agent iteratively improves it over 3 months.
When it hits optimal score, the agent:
  1. Reads the PRD
  2. Scaffolds the project structure
  3. Implements the core features
  4. Writes tests
  5. Opens a PR
User wakes up to "Your CLI tool PRD reached optimal quality.
  Implemented as /home/cheta/code/awesome-cli/. Review when ready."
