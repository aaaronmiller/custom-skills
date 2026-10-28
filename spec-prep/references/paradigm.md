---
date: 2026-05-18 10:00:00 PDT
ver: 1.1.0
author: ice-ninja
model: claude-opus-4-7
updated: 2026-10-26
tags: [spec-prep, paradigm, three-layer, four-crafts, substrate, continuity]
---

# The spec-prep paradigm and attribution

## Sources and authorship

**Kapil Viren Ahuja**, [Spec-Driven Development Isn't Broken. It will collapse.](https://medium.com/activated-thinker/spec-driven-development-isnt-broken-it-will-collapse-c00609f72496), Activated Thinker, May 3, 2026: conceptual source for the three-layer schematic, the allocation of intent/specification crafts to the human and context/prompt crafts to the system, the Substrate Stack and P-CAM. The user supplied the full article transcript after reader/archive retrieval returned only previews or challenges. This reference now incorporates that supplied text; this does not authenticate every empirical assertion in the article.

**STRATA: Spec Collapsed, Vibe Collapsed, and the Layer Nobody Shipped Was Memory**: a Claude-generated article and named methodology synthesized at ice-ninja's request, not a separately authored external paper. The user supplied the originating [Claude conversation](https://claude.ai/chat/efefe910-3b55-4129-bf10-3411bc95bab3) transcript. In it, the user requests a new named paradigm combining the attached article, their create-new-project skill and Spec Kit; the assistant, speaking as “Sliither,” then introduces “STRATA: Separation of Tiers, Retention Across Time, Auditability” and produces the article and packaged skill. This establishes the naming and drafting provenance. The vault copy is dated May 18, 2026, version 1.1.0. Its `model: claude-opus-4-7` is recorded metadata, not an independently verified runtime identifier.

The article was deliberately written in the user's first-person practitioner voice. The transcript's claims about its anecdotes, originality, validation and fidelity are assistant reports, not independently established facts. In particular, the purported fidelity audit includes a failed read step; it is not independent source verification. Credit Ahuja for the conceptual input, ice-ninja for the request and existing skill, Claude for the generated naming/draft, and Spec Kit for the workflow contribution. Do not invent another human evaluator, treat the draft as independent corroboration, or infer empirical results from first-person narrative.

The vault copies are `strata-the-methodology-is-the-memory.md` and the title-named copy under Windows Documents/chetaz. They are provenance sources, not runtime dependencies. STRATA was the former name of spec-prep; it is unrelated to similarly named model-inference software. The user supplied naming confusion with inference software as the rename rationale; inference performance is outside this skill.

Additional credited influences: [Nate B. Jones's four disciplines](https://promptkit.natebjones.com/20260225_hfy_promptkit_1), [Dan Shapiro's autonomy levels](https://www.danshapiro.com/blog/2026/01/the-five-levels-from-spicy-autocomplete-to-the-software-factory/), and [StrongDM's scenario/evaluation approach](https://factory.strongdm.ai/). The supplied article explicitly credits Jones with the four-craft vocabulary and Shapiro with the Dark Factory term/autonomy-model influence. Ahuja claims the human/system split, the three-layer and P-CAM mappings, and his Substrate Stack. STRATA operationalized those ideas; it did not originate that allocation of crafts.

Ahuja subsequently published [IDSD](https://medium.com/activated-thinker/the-method-that-replaces-spec-driven-development-idsd-66e921f6cdf7) and [The Anatomy of Intent](https://medium.com/activated-thinker/the-anatomy-of-intent-ice-in-idsd-built-from-where-spec-driven-breaks-1597e5a16659). Their existence is verified; their full content has not been supplied or reviewed here. Retire the historical claim that he never proposed a fix. Do not claim to implement all of IDSD or ICE without examining their complete contracts.

## Three independent assets, one traceable project

**Intent** records the desired outcomes, constraints, success and failure conditions, personas, stories, scope and unresolved assumptions. It retains human authority even when an agent drafts it. Preserve source statements and distinguish accepted decisions from proposals. Do not reduce intent to the introductory paragraphs of requirements or a task list.

**Requirements/specification** defines observable behavior and measurable acceptance. Quality expectations may originate in intent and also require measurable clauses here. Link those clauses back to intent rather than excluding nonfunctional acceptance. Evaluation identifiers establish traceability, not test adequacy.

**Design/plan** derives mechanisms from accepted intent, the contract, current constraints, available evidence and the existing system. Explain consequential choices and alternatives. Explicit user technology constraints remain authoritative constraints, with provenance and justified layer exceptions; architecture ownership never authorizes ignoring them.

Use the selected output contract: requirements.md/design.md/intent.md for a compact input handoff, or native spec.md/plan.md plus intent.md for completed Spec Kit preparation. Do not duplicate editable authorities to imitate historical filenames. Read the corresponding templates for field-level structure.

## Preserve the original brief: less ceremony, clear intent

The supplied “is spec-driven design obsolete?” conversation records a specific user distinction: capable agents resolving implementation from outcomes are not equivalent to accepting unreviewed code. Do not label outcome-led delegation as careless vibe coding. Let the agent derive ordinary mechanisms; maintain the accepted outcomes, constraints and verification contract.

Select process by uncertainty, behavioral novelty, consequence, coordination, audit needs and expected lifetime, not a line-count cutoff, model brand or context-window capacity. Routine website mechanics do not by themselves justify a large specification tree; custom authorization, payments or unusual behavior may still need explicit contracts in a small codebase. Use the smallest already supported delivery operation that satisfies the request. Keep supporting artifacts conditional and reusable procedures parameterized. An explicitly requested native Spec Kit preparation still completes its agreed stages and gates; proportionality is not permission to stop halfway or auto-implement.

The old assistant replies in that conversation are historical responses, not corroborating research. Do not inherit their unsupported claims that specs cannot drift, particular models eliminate the need for specifications, adoption proves superiority, or one workflow is the only viable option at a given code size.

## Consolidation of the source concepts

This table supersedes this reference's older absolute claims. It adds no new mandatory artifact class; it explains and reconciles the existing roles and gates.

| Important source element | Current operational home | Interpretation retained or qualified |
|---|---|---|
| Intent as its own asset | intent-template.md; source disposition | Preserve purpose, constraints, failure outcomes and stories separately from mechanisms. |
| Two intent domains | intent-template.md; plays-playbook.md | Consumer outcomes inform epics; engineering workflow outcomes inform governance/plays. Both still need observable acceptance; a play is not a substitute for a contract. |
| Four-craft ownership | Sources above; source authority and derivation rules | Jones supplies vocabulary; Ahuja supplies human/system allocation. Agents may draft, but do not silently replace user authority. |
| Evaluable contract | spec-template.md; clause/eval bindings | Require observable acceptance; an ID or lexical lint is not semantic proof. |
| Architecture derived from intent and evidence | context-template.md; Phase 3 | Cite relevant constraints and actual outcomes; disclose missing evidence rather than pretending an empty ledger supplies empirical support. |
| Parameterized reusable plays | plays-playbook.md | Read changing target values; revise the workflow when changed constraints invalidate its procedure or assumptions. |
| Continuity as maintained state | ledger-and-standing.md | Record material decisions/outcomes and refresh current standing before handoff. No guaranteed recovery-time claim. |
| Governance and source authority | constitution-source.md; scoped agent instructions | Retain authorized principles, source distinctions and preparation/implementation boundaries across resets. |
| Capability-dependent scaffolding | Phase 0; plays-playbook.md | Keep model-resolvable mechanisms open when appropriate; retain checkpoints for consequential or uncertain choices. No guaranteed future disappearance of plays. |
| Honest operating capability | substrate-self-location.md | Record fixed/live decisions, evidence and unproven reach. Self-declaration is not certification. |
| Evaluation independence | eval bindings and delivery evidence | Public acceptance can remain visible; genuine held-out tests need actual access isolation, not merely another directory. |
| Independent change of layers | six-rule change propagation | Start a correction at its owning layer; reconcile all affected dependencies and receipts. A pivot is not guaranteed to leave tasks or requirements unchanged. |

## Deliberate adaptations and non-claims

Ahuja's article excludes nonfunctional requirements from spec; here their source expectations remain in intent while measurable obligations also appear in the acceptance contract. The thirty-second recovery example requires a workload/failure boundary and an actual evaluation. This is a deliberate engineering adaptation, not a claim that the source prescribed the same rule.

The source strongly reserves architectural choices for the system. This skill preserves explicit user mandates and legacy constraints while keeping agent-selected mechanisms derived and traceable. Record whether a choice is mandated, provisional, accepted or resolved during implementation; do not pre-lock every choice just to make the plan look complete. A genuinely unresolved dependency prevents only the work that needs it.

Ahuja uses Symphony as a fidelity illustration. A quoted line count is not a universal completeness threshold or a proof of deterministic behavior, and neither document length nor a file's existence demonstrates contract adequacy. This skill applies behavioral coverage, traceability and evidence rather than adopting the article's market figures, anecdotal savings percentages or broad framework-collapse claims as measured facts.

P-CAM is credited conceptual background; this skill does not implement or certify that architecture. Ahuja's Substrate Stack is separate from Shapiro's autonomy taxonomy; see substrate-self-location.md for preserved legacy labels and source-level definitions.

## Continuity and learning

A ledger records why decisions were made and what happened; a standing snapshot records the current resumable position. Verify these against live state after interruption. Where historical records are missing, inspect source/history and disclose reconstruction instead of inventing continuity.

Reuse prior outcomes only when relevant evidence exists and the current task permits access. Separate observed results from causal interpretation and proposed policy. A ledger does not by itself implement a learning engine or prove that a decision will transfer to another project.

## Enforcement limits

Mechanical checks establish the identities, references, paths and structural conditions they actually inspect. Semantic fidelity still requires source-aware review. Project instructions depend on the host loading them; held-out evaluation depends on tool/file access boundaries. Neither a constitution nor an autonomy label is a platform-level security control. Other frameworks also implement continuity; differentiation rests on this combined authority and derivation discipline, not an exclusivity claim.
