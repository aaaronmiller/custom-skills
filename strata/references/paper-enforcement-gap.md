---
date: 2026-08-03
ver: 1.0.0
author: ice-ninja
tags: [strata, spec-driven, validation, enforcement-gap, methodology]
---

# The Enforcement Gap: Why Written Methodology Rules Do Not Constrain Agent Behavior

## Abstract

Spec-driven development methodologies encode their discipline as written rules.
We report an audit of one such implementation — STRATA, a six-artifact
methodology derived from Ahuja's 2026 three-layer critique — against the source
article's claims. Of twenty testable claims, eighteen were present in the
methodology text and only four were mechanically enforced. Two of the four
enforced checks were structurally incapable of detecting the violations they
existed to prevent: a technology denylist omitting the workspace's primary
language, and an eval-binding check validating tag syntax rather than
resolution. We term this the *enforcement gap*: the distance between a rule
being written and a rule being able to fail. We describe five mechanical checks
that close it, report a measured before/after against a real corpus, and
document a false-positive class introduced during remediation that would have
made the tooling worse than absent. The central finding is that methodologies
degrade not by having wrong rules but by having correct rules with no
instrument, and that this degradation is invisible precisely because the
unenforced rule remains visible in the text.

## 1. Introduction

Ahuja (2026) argues that spec-driven development and vibe coding fail for a
shared reason: both compress three distinct concerns — intent, specification,
and implementation — into a single artifact. Spec-driven fuses them by
over-specification, burying intent inside the spec and pre-locking architecture.
Vibe refuses to specify, letting the model resolve all three live without
contract or memory. The prescription is separation of concerns applied one layer
up, to the documents used to instruct code-writing machines.

STRATA implements this prescription as six artifacts with distinct authorship,
six rules, a validator, and a continuity ledger addressing the gap Ahuja names
but does not close: spec-driven development solves structure at creation and has
no answer for continuity across time.

This paper does not evaluate whether the prescription is correct. It evaluates
whether an implementation that believes it follows the prescription actually
does, and reports that belief and behavior diverged in a way neither code review
nor documentation review would surface.

## 2. Method

We extracted twenty testable claims from the source article, each phrased as an
assertion about what a compliant implementation must do. Examples: *non-
functional requirements reside in the intent layer because they drive
architecture*; *evaluations are stored outside the build tree so agents cannot
game them*; *upstream change enters at the intent layer only*.

Each claim was checked at three levels:

1. **Present in prose** — the methodology text states the rule.
2. **Gated in procedure** — a named phase or gate references it.
3. **Mechanically enforced** — a validator fails on violation.

We then executed the validator against a corpus produced by a conventional
SpecKit-only pipeline, and against synthetic trees constructed to violate each
rule individually.

## 3. Results

### 3.1 Claim coverage

Eighteen of twenty claims appeared somewhere in the methodology. Two were absent
entirely: the fidelity-gap argument (that specifications must reach a depth most
teams never write) and the drifted-spec-lies-with-confidence framing.

Coverage stratified sharply by enforcement level:

| Level | Count |
|---|---|
| Mechanically enforced | 4 |
| Procedural gate only | 1 |
| Prose only | 13 |
| Absent | 2 |

Thirteen rules existed exclusively as text. A reader of the methodology would
encounter them as requirements; an agent violating them would encounter nothing.

### 3.2 Two enforced checks that could not fire

Enforcement count overstates enforcement quality. Two of the four mechanical
checks were structurally unable to detect their target violations.

**Denylist coverage.** The separation rule — no technology tokens in the
human-authored layers — was enforced by a 56-token denylist covering common web
and infrastructure names. It omitted the workspace's primary language and its
entire observability stack. Executed against a requirements document naming
three technologies, it reported zero violations. The rule described as failing
the build could not perceive the most probable violation in its own environment.

**Binding versus resolution.** The eval-binding rule requires each specification
clause to carry an identifier bound to an evaluation stored outside the build
tree. Separation of storage is load-bearing: it is the mechanism preventing an
implementing agent from reading and optimizing against its own test. The check
validated only that a syntactically well-formed tag appeared on the line. A tag
referencing a nonexistent evaluation passed. An evaluation directory located
*inside* the tree — the precise configuration the rule forbids — also passed,
while presenting as compliant.

### 3.3 Absence of temporal checking

The methodology's distinguishing contribution is continuity. Its validator
operated exclusively at authoring time and performed no comparison between
artifacts. A specification clause unsupported by any architectural decision, and
an architectural decision citing a clause since deleted, were both undetectable.
An anti-drift methodology contained no drift detection.

## 4. Remediation

Five checks were added. Each is executable and was verified both to fire on a
constructed violation and to remain silent on a compliant tree.

1. **Denylist expansion and extensibility.** Coverage tripled; a sidecar token
   file merges automatically. Generic lists systematically miss domain-specific
   leakage, so the mechanism for domain extension matters more than list size.
2. **Eval resolution.** Tags must resolve to a manifest located outside the
   tree. An in-tree evaluation directory raises a distinct diagnostic naming why
   it is worse than absence.
3. **Testability lint.** Clauses containing non-evaluable language are flagged
   against a phrase list. The litmus is the source article's: a clause not
   convertible to pass/fail is intent or noise.
4. **Fidelity floor.** Specifications below a clause threshold are flagged as
   headlines rather than contracts. This instruments the fidelity-gap argument,
   previously cited and unmeasured.
5. **Bidirectional drift.** Specification clauses uncited by any decision, and
   citations to nonexistent clauses, are both reported.

### 4.1 Measured effect

Against a corpus produced by a SpecKit-only pipeline:

| | Prior validator | Revised validator |
|---|---|---|
| Layer-separation violations detected | 0 | 3 |
| Non-evaluable clauses detected | not checked | 1 |
| False positives | — | 0 |

The prior validator reported the corpus clean. It contained three technology
tokens in a layer that forbids them.

### 4.2 A false-positive class introduced during remediation

The first revision reported ten violations, seven located in the derived
architecture document — the layer where technology choices are correct by
design. These were false positives produced by applying a layer-specific rule
without layer awareness.

This failure mode deserves emphasis because it is more dangerous than the gap it
replaced. An under-enforcing check produces unwarranted confidence. An
over-reporting check produces disuse, and a disabled check enforces nothing at
all. Remediation added filename-based layer inference, restricting separation
enforcement to human-authored artifacts. A second observed defect: the clause
regex recognized only the methodology's native identifier format and was blind
to the `FR-`/`NFR-` convention emitted by mainstream tooling, silently skipping
two checks on external corpora.

## 5. Discussion

### 5.1 Why the gap is invisible

An unenforced rule is not missing. It remains in the methodology text, is read
during onboarding, is cited in review, and is sincerely believed. Its absence
manifests only as violations that are never reported — an absence of signal
indistinguishable from compliance.

This explains why the gap survives review. Reviewing the methodology finds the
rule present. Reviewing the validator finds a check present. Only executing the
check against a known-dirty document reveals that the two are not connected. The
audit that found these defects was adversarial by construction: it assumed the
implementation did not do what it claimed.

### 5.2 Relationship to the source argument

Ahuja reports that his own load-bearing document drifted for months while he was
the person publicly arguing for separation, and concludes that separation
depending on vigilance decays while separation failing the build holds.

Our findings extend this. Failing the build is necessary but insufficient. The
mechanism must be able to perceive the violation class present in its
environment. A build-failing check with inadequate coverage produces the same
outcome as vigilance — undetected drift — while additionally producing false
confidence that the problem is handled.

The pattern is self-similar across layers. Ahuja's critique is that
specifications fuse concerns they claim to separate. Our finding is that
validators enforcing separation may fail to enforce what they claim to enforce.
In both cases the artifact's stated properties diverge from its behavior, and in
both cases the divergence is invisible from inside the artifact.

### 5.3 Limitations

Findings derive from a single implementation audited by its author, and the
remediation was verified by the same party — self-review is not independent
verification. The denylist and phrase-list approaches are heuristics that cannot
achieve full recall; they raise the floor rather than closing the class. The
fidelity threshold is a heuristic floor, not a measure of specification
completeness, and no evidence is offered that clause count correlates with
determinism. The measured comparison covers one corpus.

## 6. Conclusion

An implementation may faithfully reproduce a methodology's structure while
enforcing almost none of its rules, and the discrepancy is undetectable from
either the methodology text or the validator source read in isolation. Of twenty
claims, thirteen existed as prose alone and two of four enforced checks could
not detect their target violations.

The operational recommendation is narrow and testable: for every rule a
methodology claims to enforce, construct a document that violates it and confirm
the tooling fails. A check never observed failing has not been shown to work. In
this audit, the single most consequential defect was found by that procedure and
by no other.

## References

Ahuja, K. V. (2026). *Spec-Driven Development Isn't Broken. It will collapse.*
Activated Thinker, May 2026.

Jones, N. B. (2026). *Prompting Just Split Into 4 Skills.* February 2026.

Shapiro, D. (2026). *Five-level autonomy model for agentic development.*
January 2026.
