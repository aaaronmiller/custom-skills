# Running deliberative councils inside agy

For V(X,Y,S) methods (X seats, Y rounds, S probes per gap). The method stays complete; only its packaging changes.

## Packaging
- One pass (one lens) per agy session. Each pass is a unit with its own record, snapshot and marker.
- The pack carries: the council roster with one-line mandates, the adoption rule verbatim, the lens for this pass, and prior passes as decision tables.
- The full protocol file stays on disk; the pack quotes its binding rules and points to it for edge cases.

## Procedure block for the template

Paste into `<procedure>` and fill the numbers:

```
1. Write a plan of attack to {{RECORD_PATH}} under "## 0. Plan": the lens, the 3 to 6 riskiest areas to examine, and the probe planned for each gap.
2. Probe 1 (before round 1): run a real command, line-range read or search that tests the riskiest assumption. Append the command and a trimmed excerpt of its output to the record under "## Probe 1".
3. Round 1: every one of the {{X}} seats states a position on each candidate change, in its own voice, with reasoning. Append to the record under "## Round 1" in one write.
   If round 1 is unanimous on any item, add an adversarial seat for round 2 on that item.
4. Probe 2, Round 2, Probe 3, Round 3 likewise, each appended as it completes. Later rounds respond to earlier ones and to the probe evidence; seats may change position and say why.
5. Probe 4 (after the final round): verify the evidence behind every change headed for adoption.
6. Tally: table of change | votes (n of {{X}}) | evidence (path:line or command) | outcome (adopted at {{ADOPT_THRESHOLD}}+ with evidence or pure clarity/testability fix; open at {{OPEN_RANGE}}; rejected below).
7. Apply adopted changes with targeted edits. Run any regeneration scripts the protocol requires after each edit to a governed file.
8. Checkpoint protocol.
```

## Keeping the deliberation rich without bloating residency
- Write each round in one large append. The words are the product; they are not the cost driver.
- Do not paste whole files into the record; cite path:line and quote at most the lines at issue.
- Compress earlier rounds only in your head, never in the record: the record keeps every round in full for the operator.
- Probe output goes through `tail`, `grep` or a line range before it enters context.

## Unanimity and echo chambers
A single model voicing ten seats tends to converge. Countermeasures that cost nothing in quota:
- Give each seat a mandate that conflicts with at least one other seat (simplicity vs completeness, feasibility vs ambition, red team vs author).
- Require at least one seat to argue the strongest case against each candidate change in round 1.
- Schedule an independent Gemini Pro red-team unit after the Claude pass when the stakes are high; it runs on the other pool.

## Multi-refiner campaigns
When several refiners run in sequence (for example passes 1 to 5 by one model, 6 to 10 by another), the later refiner's pack should list the earlier decisions with their evidence and explicitly invite challenge. An independent second opinion is usually the point of the second refiner.
