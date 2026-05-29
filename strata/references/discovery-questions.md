---
date: 2026-05-18 10:00:00 PDT
ver: 1.0.0
author: ice-ninja
model: claude-opus-4-7
tags: [strata, discovery, interview, intake]
---

# Discovery Questions (Interactive mode)

Do not ask all of these at once. Proceed by category, 2 to 4 questions per round, reassessing the Confidence Gate after each. Use the structured-question tool when available so the user taps rather than types. As answers arrive, tag each one as intent, spec, or implementation; the separation begins in the interview, not in the artifacts.

## Problem space
What problem does this solve and who has it. What happens today without it. What do people use now and why is it insufficient.

## Solution vision
What does success look like for the user, as an outcome not a task. Walk the primary workflow start to finish. What is explicitly out of scope for the first version.

## Users and adoption
Who are the one to three primary user types. What is their technical sophistication. How do they discover and adopt this. What makes them choose this over the alternative.

## Data and state
What must be stored. What are the relationships between entities. What is the data lifecycle. What are the privacy and retention requirements.

## Technical constraints
Target platforms. Offline requirement. Performance expectations as numbers. Integration requirements. Deployment target (capture this as an intent constraint, never as an architecture).

## UX and interaction
What interaction pattern fits. What design language fits the audience. Accessibility requirements. How errors surface. Responsive, PWA, offline-first needs. Internationalization needs.

## Business and distribution
Open source, commercial, or internal. Monetization if any. Competitive landscape. Regulatory and compliance requirements.

## STRATA-specific probes (always ask before exiting intake)
Which decisions does the user want fixed up front versus left for the system to resolve. This populates `substrate.md`. What is the single sentence outcome. If it does not fit in one sentence, intake is not done. What are the failure branches when things go wrong. These become intent failure conditions, not spec test cases.

## Exit
When the Confidence Gate clears 85%, confirm: "I have enough clarity. Here is what I understand in one paragraph: [...]. Should I proceed to research and artifact generation?"
