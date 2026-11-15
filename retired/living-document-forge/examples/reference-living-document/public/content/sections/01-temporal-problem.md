---
id: temporal-problem
title: The temporal problem
updated: 2026-07-09
---

## Generation outruns inspection

A capable agent can produce several pages while a human is still evaluating the first paragraph. The mismatch is not merely inconvenient. It changes the architecture required for trustworthy collaboration.

Linear chat assumes that one message can be read, understood, answered, and retired before the next arrives. Complex research and design work violates that assumption. Several sections may need independent review, a question may remain open while another branch advances, and attached evidence may apply to only one claim.

A living document responds by making collaboration **spatial, persistent, and addressable**. The human can stop at any section, annotate a specific target, defer a proposal, and return later without losing the surrounding argument.

This also changes the reading surface. A terminal transcript or chat scrollback is optimized for chronological output, not sustained review. The input box moves away from the passage being inspected, context collapses into vertical scrolling, and the reader is forced to remember which paragraph needed a decision. A browser-native document keeps navigation, review controls, annotations, and local drafts near the content they govern.

## The interface is a protocol

Dashboard, section index, annotations, proposals, and worklogs are not ornamental conveniences. They are protocol elements created by the decision to decouple generation from review.

- Sections provide stable places for durable concepts.
- Annotations let a reader disagree without immediately rewriting prose.
- Proposals turn possible changes into individually decidable objects.
- History records events without pretending they were all releases.
- Worklogs make model-authored change inspectable after the conversation has moved on.

The result should feel less like racing a fast typist and more like entering a workshop where every unfinished object remains on its labeled bench.
