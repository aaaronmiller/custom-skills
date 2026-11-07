# Contract tests for project-archive and portfolio-lineage (task T045)

An agent runs these before it depends on either skill. Each test uses fixtures
only, writes only inside a temporary sandbox, and prints one line starting
`PASS <clause>:` or `FAIL <clause>:` with the reason. Exit 0 on PASS, 1 on FAIL.

| Test | Clause | Owner |
|---|---|---|
| `test_da032.py` | DA-032: folder moves always never-class; under a hold an approved move first lists consumers, passes a sandbox test, writes manifest, path map, old-path links, working-copy repair and live-use guard | project-archive |
| `test_da033.py` | DA-033: mine, index, move, link in order; identity, locators, predecessor and successor, tested recovery, uncommitted and working-copy state kept; archive root excluded from discovery; lineage in Living Documents | project-archive |
| `test_da034.py` | DA-034: every clause marked covered, partial or unique; no folder with a unique clause lacking a destination is archived | portfolio-lineage |

Each test has two parts:
1. it runs the skill's `bin/contract --fixture <dir> --sandbox <dir>` exactly as
   the workbench harness does and applies the harness rules, ported line by line
   from `packages/durable-agent/src/assign/skill-contracts.ts` into `_common.py`;
2. it drives the skill's scripts on this folder's own fixtures (`fixtures/`),
   which the skills never see, and checks the result with independent code
   (raw `git` output, its own tree hash, its own recovery copy, its own walk).

## Run

```bash
python3 -I -B run_all.py                 # all three, then both digests
python3 -I -B run_all.py --mutants       # also prove each test fails on a broken skill
python3 -I -B test_da033.py --skills /path/holding/both/skills --tmp /some/scratch
python3 -I -B skill_digest.py            # digests only
```

`--skills` defaults to this folder's parent. Use `--project-archive` and
`--portfolio-lineage` to point at installed copies (for example
`~/.claude/skills/project-archive`).

## Digest

`skill_digest.py` prints the SHA-256 the workbench's `scripts/import-skill`
computes: over the sorted relative paths and bytes of every file in the skill
folder. Register a skill with
`python3 -I scripts/import-skill add --name <skill> --path <installed path> --origin <origin> --license MIT`
(not run by these tests). Run the skills with `python3 -B` so no `__pycache__`
appears and changes the digest.


## Running from custom-skills

In /home/cheta/code/custom-skills these tests live inside project-archive/, so pass the skills root: `python3 -I -B contract-tests/run_all.py --skills /home/cheta/code/custom-skills --mutants`. The default (the parent of this folder) fits the original out/ layout only.
