# Description Field Research Findings

> Research conducted across 15+ authoritative sources (Anthropic docs, Hermes Agent docs,
> GitHub issues, community guides, agent-skills specification) to understand how
> skill descriptions actually work.

## How Descriptions Work in the System Prompt

The model does NOT see descriptions in a vacuum. Hermes injects a structured
`skills_list()` block into the system prompt:

```json
[{name, description, category}, ...]
```

The model has context that these are skills — it knows what it's looking at.
However, it uses the description text to decide WHICH skill to load for the
current task. Descriptions are the routing signal.

## Level 1: The Preamble (always loaded)

The system prompt tells the model:
- "Here are the available skills"
- Each has a name, description, and category
- Load the full skill body when it matches the current task

Only the name + description are always in context. The full SKILL.md body loads
on-demand. (Source: Anthropic Agent Skills docs, Hermes Skills System docs)

## Level 2: The Trigger Mechanism

The model reads descriptions and decides: "Does any description match what
I'm being asked to do right now?" This is semantic matching, not regex — but
descriptions are the ONLY signal the model has.

A confirmed Hermes bug (#13944) demonstrates this: descriptions were truncated
to 60 chars in the system prompt, which broke skill routing entirely. The fix
raised the limit to 1024 chars. This confirms descriptions ARE the routing
signal and longer descriptions with triggers are functionally necessary.

## Level 3: When "Use When" Matters vs When It Doesn't

**Skills tend to UNDER-trigger, not over-trigger.** Every source confirms this.
The #1 support issue across all platforms is "my skill never fires."
Write slightly aggressive descriptions.

### Skills that DO need "Use when:"

Those with GENERIC names where the model can't infer the trigger from the name alone:

| Skill Name | Domain | Risk Without Triggers |
|-----------|--------|----------------------|
| `service-troubleshooting` | Generic | Could apply to any debugging task |
| `code-review` | Generic | Could overlap with systematic-debugging |
| `web-scraping` | Generic | Model may not know when to use this method |
| `ci-cd-workflow-repair` | Generic | Might not fire on CI failure prompts |

These benefit from: `Use when: specific situation. Triggers: "phrase", "phrase".`

### Skills that DON'T need "Use when:"

Those with DISTINCTIVE names that the model already understands:

| Skill Name | Why It Works | Example Description |
|-----------|-------------|-------------------|
| `axolotl` | Known ML tool. Name IS trigger. | `Axolotl: YAML LLM fine-tuning (LoRA, DPO, GRPO).` |
| `vllm` | Known inference engine. | `vLLM: high-throughput LLM serving.` |
| `notion` | Known product. | `Notion API: pages, databases, blocks.` |
| `linear` | Known product. | `Linear: manage issues via GraphQL.` |
| `gsap-core` | Known library. | `Official GSAP skill for the core API.` |

These work because:
- The name itself triggers matching ("use axolotl")
- The model knows what these tools are from training
- The description tells WHAT it does, the name tells WHEN

### Skills Deserving EXTENSIVE triggers

High-priority skills where MAXIMUM recall matters:

| Skill | Example | Trigger Count |
|-------|---------|--------------|
| `deliberative-refinement` | `Use when: thinking through problems... Triggers: "decide", "evaluate"...` | 30+ |
| `humanize-writing` | `AUTOMATIC ACTIVATION: Use whenever generating prose...` | 20+ |

These benefit from every possible trigger phrase. They should fire aggressively.

## Level 4: The Hermes Bundled Skill Pattern

Hermes bundled skills use short descriptions without "Use when:":

```
Delegate coding to Claude Code CLI (features, PRs).
vLLM: high-throughput LLM serving, OpenAI API, quantization.
Notion API + ntn CLI: pages, databases, markdown, Workers.
```

These work because:
1. The names are distinctive (model knows Claude Code, vLLM, Notion)
2. The system prompt provides skill context
3. The descriptions tell WHAT clearly
4. They have no overlap with other skills

## Level 5: Optimized Approach

| Skill Type | Description Strategy | Token Budget |
|-----------|-------------------|-------------|
| Distinctive name, well-known tool | `Tool: what it does.` | ~15-25 tokens |
| Generic name, broad domain | `Use when: X, Y. Triggers: "a", "b".` | ~30-60 tokens |
| High-priority S-tier | Extensive trigger list | ~60-180 tokens |
| Edge-case / low-utility | Minimal | ~15-25 tokens |
| Bundled (can't edit) | Leave as-is | Varies |

Do not chase a hard token budget across all skills. Prioritize EFFECTIVE TRIGGER
COVERAGE per skill. The right amount of description is: enough for the model to
reliably activate it, and not a single token more.

## Sources

- Anthropic Claude Code Skills docs: https://docs.anthropic.com/en/docs/claude-code/skills
- Hermes Agent Skills System: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills
- Hermes Bug #13944 (60-char truncation): https://github.com/NousResearch/hermes-agent/issues/13944
- Hermes Skill Authoring guide: https://hermes-agent.nousresearch.com/docs/developer-guide/creating-skills
- Agent Skills specification: https://agentskills.io
- Anthropic Skills best practices: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices
- ClaudSkills frontmatter guide: https://claudskills.com/learn/skill-md-frontmatter-reference/
- Claude Code Skills guide: https://claudecodeguides.com/skill-md-file-frontmatter-fields-explained/
