# Model Notes (September 2026)

## Table of contents

- GPT-6 Astra (OpenAI)
- Claude Fable 5.1 (Anthropic)
- Loop economics

## GPT-6 Astra (OpenAI)

Frontier computer-use flagship, released 2026-09-03 (`gpt-6-astra`, ~1M context). Prompt for goals, autonomy, and definition-of-done over micromanagement; treat requests as calls to act. Calibrate `reasoning.effort` per role rather than globally. Persist reasoning across rounds via the Responses API instead of re-deriving it. Prefer `strict:true` JSON schemas with rationale and error fields for verdicts. Keep a plan-first scratchpad with TODO tracking and short preambles before tool calls. Source: OpenAI docs, cookbook prompting guide, AI Search demo 2026-09-07.

## Claude Fable 5.1 (Anthropic)

Released 2026-09-01 (`claude-fable-5-1`, 1M context, adaptive thinking always-on). Notable breaks: no forced tool use, thinking blocks are model-bound, history must be append-only. Sweep effort per role including low and medium (medium approximates prior-gen flagship quality cheaper). Scope blocks matter: authorize finishing the whole task and name the request-or-plan as the deliverable. For long loops prefer server-side compaction and keep a 6-item preserve list. Ordering tricks that measure well: docs-first with the query last (about +30%), quote the task before starting, 3–5 examples, XML boundaries. Fan subagents out for parallel distillations of 1–2K tokens. Source: Anthropic prompting docs, context-engineering post.

## Loop economics

Critic rounds multiply cost: a separate-agent critic roughly doubles per-round spend, a different-family judge more. Calibrate spend by role — cheap fast builder, strong careful critic — and cap total budget in the brief (rounds × cost). The AI Search demo spent ~3–10% of weekly quota per task across 3–4 rounds: a realistic planning figure for flagship-model loops.
