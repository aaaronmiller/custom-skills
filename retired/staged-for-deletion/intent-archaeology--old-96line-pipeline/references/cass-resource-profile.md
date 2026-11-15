# CASS resource profile for constrained hosts

Use `scripts/cass-low-memory-index.sh` when an Intent Archaeology run needs a
CASS refresh on a machine where an unconstrained index can threaten the active
agent session.

The wrapper is print-first. It never starts a refresh until `--execute` is
given. Its transient user-systemd service imposes `MemoryMax`, `CPUQuota`, and
`RuntimeMaxSec` on the actual CASS process. These external cgroup limits are
the acceptance mechanism; CASS environment knobs are useful tuning hints but
are not sufficient proof that an installed binary will stay within bounds.

Before execution, capture `cass health --json`. After execution or a cgroup
termination, capture it again and verify: no active rebuild, no unexpected
quarantine, and no partial-index state. Do not use this wrapper with `--full`
or `--watch`. A persistent watcher requires a separate decision and service
contract.
