---
title: Optional Jev semantic review
version: "2.5.1"
tags: [spec-prep, jev, validation]
---

# Optional Jev semantic review

Read when Jev review is requested or a bounded semantic check could improve preparation. This reference owns the Jev procedure; no earlier reference covered it. It does not add a mandatory service or approval gate. The agent still executes the selected Spec Kit workflows and records their actual results.

## Availability and fallback

Jev is optional in every deployment. Use it only when the user has not disabled it and an eligible adapter/tool, network access, credentials and authority for the selected external send already exist. Hosted Claude Code or OpenAI agents may lack any of these; inspect available capabilities without assuming access or inspecting secret values. Do not provision Jev as part of ordinary preparation.

When disabled, unavailable or unsuccessful, record the Jev review as `not_run` with a short reason. Preserve any attempted provider call's actual failure in its adapter receipt; `not_run` means no usable Jev semantic verdict was obtained, not that no attempt occurred. Continue deterministic validation and the required agent-mediated semantic review against the same sources and rubric. Attribute the review to the actual reviewer, and label self-review accurately. A separately required independent review is not satisfied by self-review, and a required gate never becomes optional because Jev is absent. Do not retry unavailable access repeatedly, switch providers, request new credentials or incur spend solely to obtain optional advice. If the user separately requests configuring Jev, treat that as its own scoped task.

Jev evaluates supplied state with typed questions. It does not write specifications or replacement prose. Keep exact comparisons and arithmetic in code; the vendor documents limitations with numeric precision, dates, indirection and irrelevant context. Use it for an atomic evidence judgment with an explicit abstention option, then review the cited excerpt yourself. Confidence is a routing signal, not proof of correctness. A stronger model or the human resolves a substantive ambiguity without inventing product scope.

## Where it helps

| Stage | Useful semantic question, with a named excerpt | Deterministic work stays outside Jev |
|---|---|---|
| Intake, before specify/plan | Does this acceptance condition express an observable outcome? Does this design excerpt support this stated constraint? | Intake hashes, files, JSON/schema, read order |
| Generated output | Does this one requirement preserve this source obligation? Is a documented constraint contradicted by this decision? | ID existence, source hashes, clause/eval tags, artifact paths |
| Task generation | Does this task's proposed acceptance exercise the linked requirement? Is a recovery procedure adequate for this named failure? | Task format, dependency cycles, missing paths/gates |
| Governance | Does this plan decision conflict with this quoted principle? | Exact constitution heading set, instruction-file references, receipt checks |
| Implementation, when already authorized | Does this captured acceptance evidence support this one claim? | Actual tests, checksums, numerical boundaries, authorization, checked task state |

Avoid a full-document “approve everything” question, repeated calls on every edit, or use as a constitution/permission oracle. Use the smallest excerpt that can decide each question. Jev checks within one request are independent; a question cannot rely on another answer. When prerequisites or tools fail, record that failure and use the normal deterministic/reviewer workflow. Never label another model's reasoning a Jev verdict.

## Keep the target explicit

For a skill change, `--target skill --root /absolute/path/to/the/skill` must point to the folder containing SKILL.md. Application specs are examples, not the edit target. For project preparation, use `--target project` and the actual build root. A recommendation never edits either root. Review any proposed upstream semantic change against intent, then regenerate the affected plan/tasks/contracts, rerun gates and refresh the preparation receipt after the final writes. Operational ledgers with two path aliases must agree; do not refresh hashes in order to hide drift.

## Typed provider adapter

`scripts/spec-prep-jev.py` builds a request from an explicit packet, performs no discovery, and defaults to an offline preview. Sources must be UTF-8 files resolving inside the chosen root. The packet chooses excerpts by line range; the receipt fingerprints the complete source files. Requests/responses are capped at 64 KiB and rejected rather than silently truncated. Do not include secrets, private URLs, evaluator-only fixtures or unnecessary project data. Preview the exact request before any approved external send.

Packet example (for a skill with at least two lines in SKILL.md):

```json
{
  "schemaVersion": 1,
  "sources": [
    {"id": "boundary", "path": "SKILL.md", "startLine": 1, "endLine": 2}
  ],
  "checks": [
    {"id": "observable", "criterion": "The described result is an observable deliverable.", "sourceIds": ["boundary"]}
  ]
}
```

Use actual relevant line ranges and criteria for the review; the example demonstrates the packet shape only. Given a reviewed packet at `/tmp/spec-prep-review.json`, this previews the installed canonical skill without a network request:

```bash
python3 scripts/spec-prep-jev.py --root /home/cheta/code/custom-skills/spec-prep --target skill --stage intake --packet /tmp/spec-prep-review.json --request-out /tmp/spec-prep-jev-request.json
```

A separate invocation with `--allow-network` authorizes one request to OpenCode's typed System One API. The adapter reads an existing OPENCODE_API_KEY or OPENCODE_ZEN_API_KEY, then literal OPENCODE_API_KEY/OPENCODE_ZEN_API_KEY assignments in the existing `~/.cuddle-bucket`, then the `opencode.key` entry from the existing OpenCode auth store. The credential file is parsed as data and never executed. It never logs keys, repairs auth, changes provider configuration, follows redirects, retries, or switches to a paid model. The request uses `state` and `questions`, not chat `messages`, and identifies its client truthfully as `spec-prep/2.5.1`. Python’s default urllib user agent was rejected with Cloudflare error 1010 during verification; a truthful application user agent and the documented curl request both succeeded. Error receipts distinguish that edge rejection from expired credentials without logging provider messages or keys. It pins the requested free ID `jev-1.13-free`; confirm availability before depending on it. OpenCode's current endpoint is `https://opencode.ai/inference/systemone/v1/systemone`. A generic `opencode run` chat session is not the typed decision contract. If the requested CLI path is unavailable, disclose that and use this same-provider API adapter only within the authorized scope.

The adapter returns `supported`, `needs_review` or `abstain` per question, validates IDs/types/distributions/confidence, and records requested/resolved model plus request/source fingerprints. Low confidence, abstention, stale source, malformed response and transport/auth failures cannot become a pass. Status `advisory` means only that the selected semantic checks returned supported advice; `gateEffect` is always `none`, and a reviewer still adjudicates it. `--response` validates recorded/synthetic data offline and explicitly does not establish provider execution. Existing output paths are never overwritten.

No live quality claim is justified by offline transport tests. Record actual provider results separately from semantic review, and retain the original blind response before giving additional context. Use the existing divergence-resolution procedure rather than an unbounded model loop. Jev changes no launch authority, task checkbox or required deterministic gate.

## Sources and local verification

Checked 2026-10-21: [TypeSafe System One API](https://docs.typesafe.ai/api/system-one), [Choice response contract](https://docs.typesafe.ai/primitives/choice), [documented Jev limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13), [OpenCode model endpoints](https://opencode.ai/v2/docs/console/models/). These establish wire format and model availability declarations; local credential/endpoint success must still be measured.

Run the adapter and validator regressions with:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s spec-prep/tests -v
```
