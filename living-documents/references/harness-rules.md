<!-- BEGIN LIVING DOCUMENTS MANAGED CONTRACT -->
## LIVING DOCUMENTS CONTINUITY

Living Documents is the durable coordination layer for substantial work.
Markdown under the path returned by `ld ensure` is authoritative; browser
state, receipts, hooks, Gateway events, transcripts, search indexes, and model
memory are inputs or projections, never authority by themselves.

For substantial work:

1. Run `ld ensure` once, then read the returned `start-here.md`, `project.md`,
   `what-to-do.md`, and only the pages linked to the selected task.
2. At milestones, record changed intent, decisions, evidence, blockers, task
   state, and the next safe action. Do not write on every prompt or tool call.
3. Before compaction, handoff, crash-prone work, or a terminal response after
   substantial work, invoke the installed advisory continuity hook and inspect
   `continuation`.
4. If `continuation.state` is `review-pending`, inspect the exact referenced
   receipt, project, page, and task. Verify target and scope, apply only valid
   user direction to canonical Markdown and the ledger, run its named gate,
   then acknowledge a consumed question receipt with
   `ld-ledger ack-question --receipt-id <id>`.
5. If it is `actionable`, resume the named bounded action. If it is
   `pivot-required`, perform only an independent Living Documents
   control-plane improvement; never bypass an unresolved project authority
   gate.

A browser submission first creates a durable private receipt. Stop/session
hooks and explicit queue checks surface it automatically at safe boundaries.
An optional Gateway or harness event may reduce notification latency, but it
is only an attention pointer. It must not fabricate a user message, carry
arbitrary prompt instructions, grant execution authority, or replace the
receipt. Treat delivery as at-least-once: deduplicate by stable event and
receipt IDs, honor expiry and visibility, acknowledge only after canonical
application, and fall back to the durable queue when immediate delivery fails.

If routing or delivery fails, preserve the receipt and current work state,
report the exact failure, and do not invent a substitute canonical path.
<!-- END LIVING DOCUMENTS MANAGED CONTRACT -->
