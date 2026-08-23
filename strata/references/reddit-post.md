# I audited my own spec-driven pipeline against the article that inspired it. It failed 6 of its own rules.

*Draft for r/ExperiencedDevs, r/LocalLLaMA, or r/AI_Agents. ~950 words.*

---

Two months ago I read Kapil Viren Ahuja's "Spec-Driven Development Isn't Broken. It will collapse." and it reorganized how I think about agent workflows. The thesis: spec-driven development and vibe coding fail for the *same* reason. Both compress three distinct things — intent, specification, implementation — into one artifact. Vibe refuses to separate them. Spec fuses them into a single document with intent buried inside and architecture pre-locked at the top.

I built a methodology on top of it. Six artifacts, six rules, a validator, and the thing the article named but didn't ship: a continuity ledger, so a project that sits dormant doesn't wake up with amnesia.

Then last week I did something uncomfortable. I audited my implementation against the article's actual claims, adversarially, instead of assuming I'd implemented what I thought I had.

**It failed six of its own rules.** Here's what I found, because the failure modes generalize past my specific tooling.

## Finding 1: the load-bearing check was unarmed

The core rule is that no technology token may appear in the intent or spec layers. A framework name in a spec means implementation leaked into a layer that doesn't own it. The validator enforces this with a denylist and fails the build.

The denylist had 56 entries. It covered react, postgres, kubernetes, terraform. It did **not** cover python, grafana, prometheus, echarts, pytest, html, or css.

I ran it against a spec I'd written the day before. It passed clean. That spec names Python, Grafana, and Prometheus in its requirements document.

The rule that "fails the build instead of warning" could not see the most common stack in my own workspace. A denylist that never fires isn't a passing build — it's an unarmed check reporting success.

## Finding 2: the eval binding validated the tag, not the eval

Every spec clause is supposed to carry an `EVAL-ID` bound to an evaluation stored *outside* the build tree. Outside matters: the StrongDM example everyone cites for autonomous development keeps evals separate specifically so the implementing agent can't read them and optimize against the test.

My validator checked that a `[EVAL-...]` tag existed on the line. That's all.

`[EVAL-TOTALLY-FAKE-1]` pointing at nothing passed validation. So did an `evals/` directory sitting *inside* the tree where the agent can read it — which is worse than missing, because it looks compliant while actively enabling gaming.

A spec clause bound to a nonexistent eval is the article's own phrase: a document that lies with confidence.

## Finding 3: no drift detection in a methodology that exists to prevent drift

The whole point is surviving time. The article's sharpest line is that a drifted spec is worse than no spec, because it lies with confidence. Kapil's own confession is that his load-bearing document drifted for months while he was the person arguing for separation.

My validator checked structure at authoring time. Nothing ever compared artifacts against each other afterward. Zero drift detection in an anti-drift methodology.

## Finding 4: the fidelity gap had no instrument

The article's most uncomfortable point: OpenAI's Symphony spec runs ~1,400 lines. That's what "complete enough to drive deterministic agent behavior" actually costs. Almost nobody writes that. Most teams ship "build a microservice to search red shoes," and the distance between those two documents is where the methodology collapses.

My skill *cited* this. It measured nothing. The confidence gate scored **intake quality**, not spec depth. A four-clause spec passed.

## What I changed

All of it is executable, none of it is prose:

- **Denylist tripled** and made extensible — drop a `tech-tokens.txt` beside the artifacts and it merges automatically. Domain-specific leaks are the ones a generic list always misses.
- **Eval resolution**: tags must resolve to a manifest outside the tree. If an `evals/` dir exists *inside*, that's a named, separate error explaining why it's worse than missing.
- **Testability lint**: flags clauses containing "robust," "intuitive," "seamless," "as needed," and ~20 more. If it can't become pass/fail, it's intent wearing a spec's clothes.
- **Fidelity floor**: below 8 clauses, a spec is a headline, not a contract.
- **Bidirectional drift**: spec clauses no architecture decision cites, and architecture citing clauses that no longer exist.

## The part I got wrong while fixing it

My first run flagged 10 violations against a real corpus. Seven were in `design.md` — the *derived* layer, where technology choices are supposed to live. Flagging those was a false positive.

I'd built a check that cried wolf, which is exactly the failure I'd criticized, because a check that cries wolf gets switched off and then you have no check at all. It now infers each file's layer from its filename and only enforces separation on human-authored ones.

Honest count after the fix: **3 real violations, 0 false positives.** The old validator found 0.

## Why I'm posting this

The uncomfortable pattern isn't that my tool had bugs. It's that **every one of these was a rule I had already written down.** The prose was correct. The enforcement was theater. I'd read the article, agreed with it, implemented something shaped like it, and then never checked whether the check checked anything.

The article's own line covers it better than I can: *separation that depends on vigilance is separation that decays; separation that fails the build is separation that holds.* That's only true if the thing that fails the build can actually see the violation.

If you've built spec tooling with a lint rule in it, go run it against a document you know is dirty. Confirm it fails. Mine passed a document naming three technologies in a layer that forbids technology names, and I'd have kept trusting it indefinitely.

Source article: "Spec-Driven Development Isn't Broken. It will collapse." — Kapil Viren Ahuja, Activated Thinker, May 2026. Lineage credit also to Nate B. Jones (four crafts) and Dan Shapiro (substrate levels).
