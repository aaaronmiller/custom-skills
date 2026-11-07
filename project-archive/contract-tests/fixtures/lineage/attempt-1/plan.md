# Attempt 1 plan (contract fixture)

Test data: one clause the current spec covers and one it lacks.

## Requirements

- **A1-01**: Every archive SHALL record the predecessor and the successor of the archived folder.
- **A1-02**: Each folder move SHALL leave a link at the old path and write an old-to-new path map, because harnesses key session history by absolute path.
