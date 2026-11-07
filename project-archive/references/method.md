# The lineage-archive method, and what this skill keeps

Source: the headless job `~/work/jobs/lineage-archive/` (2026-11-04), which wrote
archive indexes for the five predecessor folders of the durable agent. Paths
below are relative to that job root.

## What the job was asked to do

`brief.md`: for each folder write `<folder>-ARCHIVE-INDEX.md` with what the
folder was, its date range (file dates and dates inside files), its lineage
(what it came from, what superseded it), a file inventory with pointers to the
original files, and every reusable idea mapped to a register row as used,
deferred or rejected, or marked unregistered. Then `unregistered-items.md`
(each unregistered idea with file, line and a proposed disposition) and
`summary.md` (counts). Rules: read-only on inputs, write only under `out/`, no
network, plain English, quote only what was read and cite a file and line for
every mapping. The coverage check runs both ways: every source ID the register
cites exists in the folder, and every substantive idea in the folder is in the
register or in the unregistered list.

## How it was done (from `out/summary.md` section 4 and the transcript)

The transcript `log.jsonl` records 230 Read, 138 Bash, 37 Grep, 33 Write, 12
Agent, 10 Glob and 9 Edit tool calls. The commands that did the work:

| Step | Command (as run) | Output |
|---|---|---|
| Parse the register | `python3 -I out/evidence/tools/parse_register.py <plan.md> <out>` | `register-rows.json`, `register-index.txt` |
| Inventory | `python3 -I out/evidence/tools/inventory.py in out/evidence` | `file-inventory.json`: size, mtime, sha256, lines, dates inside, same-content copies, zip members |
| Zips without extracting | `python3 -I out/evidence/tools/zip_check.py in <out>` | `zip-check.json`: each member matched to an extracted copy |
| Copies | `python3 -I out/evidence/tools/diff_copies.py A B` | first differing byte between two copies |
| Mining | twelve sub-agents plus the coordinator, each with a fixed file slice and the shared `out/evidence/MINING-BRIEF.md` | `out/evidence/mined/*.json` |
| Quote check | `python3 -I out/evidence/tools/check_quotes.py mined/<reader>.json` | every quote compared to its cited line; status word checked against the row |
| Gap search | `python3 -I out/evidence/tools/find_unreg.py <root> <folder> '<regex>'` | candidate ideas not yet mapped |
| Assemble | `python3 -I out/evidence/tools/build_outputs.py <root>` | the five indexes, summary, unregistered list; fails on any dash or unfilled marker |

Disciplines worth keeping (MINING-BRIEF.md): readers never quote from memory;
every quote is a contiguous substring of one cited line and is checked by
script; an honest "unregistered" beats a weak mapping; process material (audits,
critiques, iteration logs) gets entries marked [process]; copies proven
identical by hash are read once; repairs by the coordinator are recorded in
`evidence/corrections.json`.

## Index layout the job produced (project-atlas-ARCHIVE-INDEX.md as the example)

Front matter (title, type archive-index, date, status, folder, original
location, register), then: 1 What the folder was, 2 Date range (a table of
evidence, date and where), 3 Lineage, 4 Coverage check of the source IDs the
register cites, 5 Reusable ideas and their register rows, 6 File inventory
(bytes, modified, lines, sha256 first 12, idea entries citing it, same-bytes
notes), 7 Notes for the move (duplicates, citations that do not point at the
folder, drift inside the folder, copy-outs before the move).

## What this skill keeps, and what it leaves to people or other skills

| Method element | In this skill |
|---|---|
| Inventory with hashes, dates inside files, duplicates | `archive.py mine` (`mine.json`) and index sections 2 and 5 |
| What the folder was, lineage | index sections 1 and 3, from the README heading and `--predecessor` / `--successor` |
| Ideas mapped to a register | Replaced by clause marks from portfolio-lineage (DA-034) in index section 4; idea-level mining by readers stays a human or agent task, because it is judgement |
| Files only here or different from the successor | `mine --successor-dir` |
| Notes for the move | `plan.py` (consumers, path map, repair plan, punch items for embedded absolute paths) |
| Nothing moved, nothing deleted | the dry-run mover only prints; the job's own status line was "nothing has been moved" |

The job stopped at "index". This skill adds the last two steps of the archive
rule (move and link) with the DA-032 and DA-033 safeguards, which the job's
`RESULT.md` left to the coordinator.
