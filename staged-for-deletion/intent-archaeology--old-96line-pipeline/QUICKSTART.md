# Quickstart

```bash
python3 scripts/00-init.py                                  # check env, create db
python3 scripts/01-inventory.py                             # find projects in ~/code ~/code2
python3 scripts/02-attribute.py                             # sessions -> projects
python3 scripts/03-enrich.py                                # raw JSONL -> event schema
python3 scripts/04-batch.py --project <slug> --items 60     # emit a batch
#   read references/taxonomy.md, classify, write verdicts.json
python3 scripts/05-merge.py --verdicts verdicts.json        # deterministic merge
python3 scripts/06-render.py                                # prompt wiki
python3 scripts/status.py                                   # where am I
```

On a constrained host, inspect the bounded CASS refresh command before any
archive refresh:

```bash
scripts/cass-low-memory-index.sh
```

See `references/cass-resource-profile.md`. The wrapper is print-first and
requires `--execute` for the deliberately separate mutating step.

Every script is resumable. If one dies, rerun the same command.

State: `~/.intent-archaeology/archaeology.db`
Output: `~/.intent-archaeology/derived/prompt-wiki/`
Yours: `~/.intent-archaeology/human/` (no script writes here)

Override the location with `INTENT_ARCH_HOME`.

Start with one project you know well. Read `corrections.md` first.
