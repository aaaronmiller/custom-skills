# Successor spec (fixture)

Test data for the portfolio-lineage skill, not a real specification. The
clauses are adapted from findings of the lineage-archive job (2026-11-04,
summary.md section 3) so the marks exercise real cases.

## Requirements

- **SPEC-001**: THE system SHALL create the run record and reserve the active-task index in one atomic transaction.
- **SPEC-002**: WHEN a tool call has no interception policy, THE system SHALL refuse it.
- **SPEC-003**: THE system SHALL keep a hazard register for the adopted runtime.
- **SPEC-004**: Folder moves SHALL be never-class when unattended.

## Archive layout

The archive root is kept outside the code roots so discovery does not list archived specs.
