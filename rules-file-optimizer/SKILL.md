---
name: rules-file-optimizer
description: >-
  Consolidate a set of reference rules files into an existing one and compress
  the result without losing capability. Use when a CLAUDE.md, AGENTS.md,
  GEMINI.md or system prompt has grown until it stops being followed, when
  instructions are being ignored, when the same rule appears in several
  sections, or when comparing your rules file against how other agents write
  theirs. Produces a measured compliance baseline, a section-by-section
  container decision, and a compressed file plus a rationale document.

  Triggers: "optimize my CLAUDE.md", "my rules file is too long", "instructions
  are being ignored", "compare my system prompt", "consolidate rules files",
  "audit my AGENTS.md", "rules file bloat", "why is Claude not following my
  instructions", "system prompt review".
license: MIT
metadata:
  version: 1.0.0
  origin: >-
    derived from the 2026-08-23 system prompt analysis,
    /home/cheta/code/agents/prompt-comparison-2026-08-23.html
tags:
  - rules
  - system-prompt
  - audit
  - meta
  - TOOL
---

# Rules file optimizer

Takes an existing rules file plus a set of reference rules files, and produces a
compressed replacement that keeps every capability, plus a rationale document that
explains each decision.

This is the sibling of `skill-audit`. That one audits a skill ecosystem; this one audits
the contract the agent operates under. Both start with measurement rather than reading,
because a rules file cannot be judged by reading it — a file that reads well and is not
followed is the failure mode.

## The premise

**A rules file has a compliance budget.** Rules compete for a finite amount of attention,
and past some size each added rule reduces compliance with the rules already present. A
file that only grows will eventually enforce nothing, and the sections added last displace
the ones that were working.

This is measurable, and measuring it first is what separates a real optimization from a
tidy-up.

## Phase 1: Measure compliance before reading anything

Do not start by reading the rules file. Start by checking whether it is being followed.

```bash
python3 scripts/measure_compliance.py <session-transcript.jsonl>
```

**Isolate terminal replies.** The unit is the last assistant text block before a genuine
user turn — not every assistant message. Most assistant messages are one-line preambles
before a tool call. On a real session, the naive median was 107 characters and the terminal
reply median was 2,958: a 27-fold difference from the definition of the unit alone.

Genuine user turns exclude system-injected content: anything beginning with `<` or
`[Request interrupted`.

**Then check each stated rule against the transcript.** For every rule in the file that
makes a checkable claim — a required opening, a length budget, a prohibition — count how
often it held. A rule below roughly 70% is not being followed, whatever it says about
itself.

Record the baseline. It is the only evidence that the work changed anything, and it must be
re-run afterwards.

## Phase 2: Find the structural defects

```bash
python3 scripts/audit_rules_file.py <rules-file.md>
```

Five mechanical checks, each derived from a defect found in a real file:

1. **Duplicated rules.** The same rule stated in two sections will drift, and the reader
   obeys whichever it met first. Real instance: one file stated a blocking-decision limit
   twice, once as a ceiling and once as a quota, with the quota phrasing first. 28% of
   replies ended in an unnecessary decision menu.
2. **Bare cardinals.** "One X per reply" reads as a target. Only "at most", "up to" or "no
   more than" transmits a maximum, and the zero case has to be named explicitly.
3. **Untriggered HOW rules.** A rule describing the shape of an output, left as a bare
   imperative, acquires the power to create the output it was meant to format. Question
   formatting rules manufacture questions.
4. **Unowned decisions.** For each decision the file governs, count the sections that
   constrain it. More than one owner means the procedure gets reassembled from fragments,
   differently each time. This does not require a contradiction to cause a misread — a
   competent auditor misread three of four rules in one file that had no contradictions.
5. **Self-immunising sections.** Grep for "preserve if", "do not remove", "keep this
   section". A section that instructs the reader to preserve it will outlive the policy it
   depends on. Real instance: a section carrying a preserve clause named a model as the
   capability floor four days after another section demoted it.

## Phase 3: Decide the container for each section

This is where most optimizations go wrong.

**The wrong question is "is this a procedure or a fact".** The right question is:

> **Does this fire every turn, or only when a matching task starts?**

| answer | container |
| --- | --- |
| every turn | stays resident in the rules file |
| on a matching task | three-line stub in the file, body in a skill |
| pure reference | one line, or a URL |

**Critical caveat.** If a section was previously a skill and was promoted into the rules
file because it was being ignored, **do not move it back**. A skill body loads only when
invoked; if nothing reliably invokes it, its contents are inert no matter how well written.
Moving it back rebuilds the failure it was created to fix.

The resolution is that the rules file is the **activation layer** — what exists, when to
reach for it, the one line of syntax needed to take the first correct action — and the
skill is the **manual**. A section carrying the manual in the activation slot is the thing
to fix, and it usually shrinks by 90% without anything leaving the system.

Worked example of the criterion doing real work: a Living Documents section holds the task
list in files rather than in context, so it is read and written continuously. It stays
resident despite being the single largest compression, because a skill body would arrive
after the turn was already shaped.

## Phase 4: Harvest from the reference files

```bash
python3 scripts/compare_prompts.py <target.md> <reference1.md> <reference2.md> ...
```

Build a concept coverage matrix: which file addresses which concern, and which formulation
is best. Look for four things.

**Concepts the target lacks entirely.** These are the highest-value additions. Check
specifically for: reversibility as the gate on action; whether approval persists across
occurrences; what to do on encountering unexpected state; nested instruction-file scoping
and precedence; and whether tool preference is stated.

**Formulations the references state better.** A rule can be present and badly worded.
Proportional response length beats a fixed line cap, because a constant is violated the
moment a task needs more, and a routinely violated rule teaches that rules are approximate.

**Direct contradictions.** Where the target asserts the opposite of a reference, surface it
as a decision rather than silently adopting either. Real instance: two frontier prompts say
"one approval is not a blank check"; the target said the opposite. Both are defensible;
the divergence should be deliberate.

**What only the target has.** Do not compress these away. A locally invented rule that
solves a real local problem is the most valuable content in the file, and it will not
appear in any reference.

## Phase 5: Compress

For every section marked stub-and-skill, write: the trigger, the minimum syntax to take the
first action, and a pointer. Two to four lines.

**Keep the numbers, drop the prose.** A measurement that carries the argument earns its
place if it costs under ten words. "Fourteen of nineteen apparent blockers were already
answered" is six words and is the entire case for a gate. The two paragraphs explaining how
that was measured belong in the rationale document.

**Drop rationale wholesale.** This is usually the single largest saving. Sections written
immediately after a failure tend to carry the evidence that motivated them, which then
reloads on every session forever to justify a rule the reader has already accepted.

**Delete superseded sections outright** rather than annotating them. An annotated dead
section still costs its full length.

## Phase 6: Write the rationale document

Every compression removes reasoning from where it was visible. It has to land somewhere or
the next editor will restore the bloat, correctly, because they will not know why it went.

The rationale document should run several times the length of the rules file and cover:
what went wrong with measurements; the container decision and its physics; every section's
what/why/what-was-removed; what was deliberately not done and why; the comparison against
reference files; rules for future edits; and outstanding work.

It is read by a human once, then only when a rule is questioned. It pays no per-session
cost, so length is free there and expensive in the rules file.

## Phase 7: Re-measure

Re-run Phase 1 against a session conducted under the new file. If compliance has not moved,
the compression was not the fix and the size hypothesis was wrong. Record the result either
way.

## Anti-patterns

- **Optimizing by reading.** A file that reads well and is not followed is the failure
  being fixed. Measure first.
- **Moving ignored sections back into skills.** See Phase 3.
- **Cutting the locally invented rules** because they do not appear in the reference files.
  That is backwards: they exist because someone hit a problem the reference authors did not.
- **Adding a section without retiring one.** The budget is the premise of the whole
  exercise.
- **Claiming success without re-measuring.** Phase 7.
