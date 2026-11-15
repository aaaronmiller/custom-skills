# Intent taxonomy

Load this at phase 5 and not before. Classification is where the value is
created; a reconstruction that is never classified is just a summary.

## Types

| Type | Definition | Test |
|---|---|---|
| `directive.feature` | Asked for a capability | Would a task list item satisfy it? |
| `directive.constraint` | A rule, limit, or "always/never" | Does it govern how rather than what? |
| `correction.behavior` | "No, not like that" | Is there an implied wrong prior action? |
| `correction.factual` | Fixing a wrong premise | Is it about a fact rather than behaviour? |
| `bugreport` | Error paste plus fix request | Is there evidence of a failure? |
| `scope.defer` | Postponed, not rejected | "Later", "next version", "after X" |
| `scope.cut` | Explicitly dropped | "Forget that", "drop it", "not doing that" |
| `preference.style` | Formatting, naming, tone | Would it belong in a style guide? |
| `question` | Asking, not instructing | Is an answer the expected response? |
| `meta.harness` | About the tool, not the project | Would it be true on any project? |
| `noise` | Approvals, filler, nothing extractable | Is there any obligation at all? |

## The two that most systems omit

`scope.cut` and `scope.defer` decide whether the audit is honest. Without them
every abandoned idea in the history reads as an incomplete feature, and the
portfolio looks 40 percent done when it is 80 percent done with a lot of
deliberate pruning. `scope.cut` is terminal: nothing may reopen it.

## The one that carries the most signal

`correction.behavior` is simultaneously evidence of an intent and evidence of a
violation. It creates or strengthens the intent, and it is also the record that
something was built wrong. Repeated corrections are the best available input to
a constitution.

## Rules

1. **Never emit a non-noise verdict without a verbatim span quoted from the
   item.** The merge rejects rows whose quote is not present in the source turn.
2. **One turn can carry several intents.** Emit several verdicts sharing the
   same `id` when it does. Under-mining a multi-directive turn is the most
   common failure at this step.
3. **Do not normalize away the specifics.** "Use Bun, not npm" is a constraint
   with content. "Use the right package manager" is not.
4. **Do not merge repetitions.** Emit them separately; counting is the merge
   step's job and the count is signal.
5. **When a turn is genuinely ambiguous, emit `noise` and move on.** A
   fabricated intent costs more than a missed one, because it will get a
   status, then a page, then a work item, and eventually something will build it.
6. **Every id in the batch gets at least one verdict.** Missing ids fail the merge.

## Scope values

`global` applies to all your work · `project` to this project · `feature` to one
feature · `file` to a specific file or module.

## Worked examples

| Turn | Verdict |
|---|---|
| "add rate limiting to /auth" | `directive.feature`, scope `feature` |
| "never use npm in this repo, bun only" | `directive.constraint`, scope `project` |
| "no, I said put the config in the root not in src" | `correction.behavior`, scope `file` |
| "we'll do the admin panel after launch" | `scope.defer` |
| "forget the plugin system, drop it" | `scope.cut` |
| "does this run on node 18?" | `question` |
| "y" | `noise` |
| "why does claude code keep truncating my file?" | `meta.harness` |
