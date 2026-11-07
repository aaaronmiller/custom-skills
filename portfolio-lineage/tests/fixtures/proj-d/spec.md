# proj-d spec (fixture)

Test data: a predecessor whose clauses are all covered or partial.

## Requirements

- **SPEC-001**: THE system SHALL create the run record and reserve the active-task index in one atomic transaction.
- **SPEC-008**: WHEN a tool call has no interception policy, THE system SHALL refuse it within 200 ms.

## Decisions

1. Keep the archive root outside the code roots.

Some prose that is not a clause: this folder was an early attempt.
