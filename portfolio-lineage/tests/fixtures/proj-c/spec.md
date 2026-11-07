# proj-c spec (fixture)

Test data: a predecessor with one covered, one partial and one unique clause.

## Requirements

- **SPEC-001**: THE system SHALL create the run record and reserve the active-task index in one atomic transaction.
- **SPEC-008**: WHEN a tool call has no interception policy, THE system SHALL refuse it within 200 ms.
- **SPEC-021**: THE runtime SHALL set the SQLite adapter to synchronous FULL and read the setting back before the first run starts, because WAL with synchronous NORMAL can lose the last commits on power loss.
