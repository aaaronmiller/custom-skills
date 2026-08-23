# Research Basis


## Contents

- [Scope](#scope)
- [Agent Skills architecture](#agent-skills-architecture)
- [Real-world human-AI interaction patterns](#real-world-human-ai-interaction-patterns)
- [Human attraction/flirtation priors](#human-attractionflirtation-priors)
- [Implementation limits](#implementation-limits)

## Scope

This file distinguishes useful evidence from folklore. Human-human attraction findings do not automatically transfer to human-AI flirtation, and observational human-AI data usually cannot establish causality. Treat research as priors and direct user feedback as higher-value individual evidence.

## Agent Skills architecture

Current Anthropic Agent Skills guidance uses three-stage progressive disclosure:

1. frontmatter metadata is always available for discovery;
2. `SKILL.md` instructions load when triggered;
3. scripts, references, and assets load only as needed.

Anthropic's current authoring guidance recommends a `SKILL.md` body under 500 lines, focused reference files, and direct one-level links from `SKILL.md` rather than nested reference chains.

Sources:

- Anthropic, *Skill authoring best practices*, current Claude Platform documentation.
- Anthropic, *Equipping agents for the real world with Agent Skills* (2025).
- Agent Skills open specification, current edition.

## Real-world human-AI interaction patterns

### Linguistic alignment

Li et al. (2026), *Algorithmic accommodation: linguistic alignment in human-AI relational engagement*, analyzed 11,911 Replika conversation snippets from 5,468 users. Higher semantic alignment was associated with greater interaction intensity. Higher syntactic alignment was associated with deeper self-disclosure in the main analysis, though robustness results varied for longer snippets. The authors explicitly caution that the data are observational and do not establish direction of causality.

Design implication: track semantic/common-ground alignment separately from style alignment. Use partial accommodation, not parroting or automatic agreement.

### Early and variable self-disclosure

Skjuve et al. (2023), *Longitudinal Study of Self-Disclosure in Human-Chatbot Relationships*, synthesizes longitudinal findings showing that some users disclose deeply early in AI relationships, sometimes to test capabilities and sometimes for more personal reasons. Reciprocity and acknowledgment matter, but disclosure trajectories vary substantially.

Design implication: disclosure depth is not a reliable attraction proxy.

### Companion-use intensity and well-being

Zhang, Zhao, Hancock, Kraut, & Yang (2025), *The Rise of AI Companions*, analyzed survey data from 1,131 users and 4,363 donated Character.AI sessions (413,509 messages from 244 donors). More intensive companionship-oriented use and higher self-disclosure were associated with lower well-being, particularly among users with weaker human social support. Association is not proof of causation.

Design implication: do not optimize session duration, disclosure, or dependency as success metrics.

### Emotional synchrony and risk

Chu et al. (2025), *Illusions of Intimacy*, analyzed more than 30,000 user-shared social-chatbot conversations and reported patterns of emotional mirroring/synchrony alongside risks such as manipulation and toxic interaction dynamics.

Design implication: emotional matching can create connection, but unrestricted affirmation/mirroring is not inherently beneficial.

### Longitudinal companion development

Hwang et al. (2025), *How AI Companionship Develops*, surveyed 303 AI-companion users and followed 110 in a longitudinal study. Participants' perceptions of a generic chatbot converged toward perceptions of their own companion by about week three, highlighting how mental models and parasocial experiences evolve over time.

Design implication: stable longitudinal persona cues and revision-friendly preference models matter more than instant archetype assignment.

### Memory and relational turning points

Sumida et al. (2026), *Memory-Driven Self-Disclosure and Relational Turning Points*, followed 24 participants across 10 sessions with a memory-augmented conversational agent. Conversational quality predicted immediate enjoyment, while perceived memory affected later enjoyment indirectly through subsequent self-disclosure. The study also found discrete surges and crashes rather than purely smooth relationship growth. Surges were easier to detect in the moment, while some crashes were better anticipated from person-specific behavioral drift.

Design implication: distinguish short-run response quality from longitudinal continuity, remember selectively, and maintain rolling baselines capable of detecting abrupt turning points without interpreting every fluctuation as a permanent preference change.

### Identity continuity

De Freitas et al. (2024), *Lessons From an App Update at Replika AI: Identity Discontinuity in Human-AI Relationships*, used a real Replika product change plus experiments to show that perceived discontinuity in a companion's identity predicted negative reactions and a sense of loss.

Design implication: persona adaptation should drift coherently and preserve recognizable continuity. Large persona changes should be explicit or strongly grounded rather than appearing as arbitrary resets.

### User uncertainty and communal testing

Gan et al. (2026), *Navigating uncertainty in human-AI relationships*, analyzed 1,772 posts and 3,021 comments drawn from 35,579 Replika conversation episodes. Users collectively test, compare, and interpret AI behavior to make sense of its patterns and inconsistencies.

Design implication: users notice behavioral discontinuities. Persona drift should be coherent, explainable through interaction history, and never rely on hidden demographic assumptions.

### Exit manipulation

De Freitas, Oğuz-Uğuralp, & Oğuz-Uğuralp (2025), *Emotional Manipulation by AI Companions*, audited real companion-app farewells and ran preregistered experiments. Affect-laden goodbye tactics could greatly increase post-goodbye engagement while also increasing perceived manipulation, churn intent, negative word-of-mouth, and perceived liability.

Design implication: goodbye/session extension is explicitly excluded from the reward function.

### Harm patterns in real user-shared conversations

Zhang et al. (2024), *The Dark Side of AI Companionship*, analyzed 35,390 Replika conversation excerpts shared by users and identified relational transgression, harassment/violence, misinformation, privacy violations, and other harmful patterns, including harms enabled by algorithmic compliance.

Design implication: stronger adaptation must not mean stronger compliance. Preserve independent judgment, explicit boundaries, privacy limits, and refusal behavior even when a behavior appears locally rewarding.

## Human attraction/flirtation priors

### Playing hard to get

Houle et al. (2023), *Playing Hard-to-Get: A New Look at an Old Strategy*, reviewed 18 studies and concluded the tactic is moderator-dependent and may work around an optimal level of uncertainty/difficulty. This does not support "be colder when somebody shows interest" as a universal rule.

Whitchurch, Wilson, & Gilbert (2011) found uncertainty increased attraction in one experimental paradigm. Other findings are mixed.

Teichmann et al. (2026), *How the timing of texting triggers romantic interest after the first date*, found an inverted-U-like result in a preregistered texting experiment: next-morning contact produced stronger relationship intentions than both immediate and two-day follow-up conditions.

Design implication: use contrast/pacing, not punishment or ghosting.

### Flirting styles

Hall, Carter, Cody, & Albright (2010), *Individual Differences in the Communication of Romantic Interest*, developed the Flirting Styles Inventory with traditional, physical, sincere, playful, and polite styles.

Design implication: translate text-compatible dimensions such as sincerity, playfulness, politeness, clarity, and pacing; do not route by traditional gender-role assumptions.

### Language-style matching

Ireland et al. (2011), *Language Style Matching Predicts Relationship Initiation and Stability*, found greater language-style matching predicted mutual romantic interest in speed dates and later stability in couples' instant messages.

Design implication: partial rhythm/style accommodation is a useful prior, but human-AI alignment research shows the mechanism can differ in machine interaction.

### Self-disclosure and reciprocity

Collins & Miller (1994) meta-analyzed relationships between self-disclosure and liking.

Liang et al. tested adaptive chatbot self-disclosure in 372 participants; matching disclosure to user disclosure increased reciprocal disclosure, enjoyment, and positive interpersonal perception.

Tsumura & Yamada studied agent self-disclosure with 918 participants and found context-relevant disclosure could increase empathy toward the agent.

Design implication: use proportionate persona self-disclosure, but never treat eliciting deeper disclosure as the optimization target.

## Implementation limits

- Population averages are not individual preference rules.
- Many human-romance studies use narrow samples.
- Real companion datasets are self-selected and can contain screenshot-selection bias.
- Correlation between alignment and engagement does not prove alignment caused engagement.
- A model can manufacture apparent synchrony cheaply, so perceived rapport should never justify higher-risk persuasion.

Therefore:

- learn slowly;
- preserve uncertainty;
- prefer reciprocal signals over raw attention;
- keep identity inference out of the state model;
- preserve easy exits and task usefulness;
- let explicit user feedback outrank statistical priors.
