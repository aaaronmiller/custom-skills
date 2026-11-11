# Mechanical Checks: Rules and Heuristics

Detail for `scripts/audit_mechanical.py`. SKILL.md carries the summary; this
file carries the rules, the heuristics that keep each check quiet on healthy
skills, and the measured cases behind them. Every behaviour below has a
tripping and a healthy fixture in `tests/test_audit_mechanical.py`.

## Portability rules

Claude Code parses frontmatter leniently; the claude.ai uploader, the Claude
API, Codex and Gemini do not. On 2026-11-10, 48 of 94 skills in `custom-skills`
failed at least one hard rule, mostly unexpected top-level keys.

| Rule | Level | Source |
|---|---|---|
| Valid YAML mapping between `---` fences on line 1 | ERROR | quick_validate.py |
| No UTF-8 BOM before the opening `---` | ERROR | claude.ai uploader rejects it |
| Top-level keys only `name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility` (everything else under `metadata`) | ERROR | quick_validate.py, claude.ai |
| `name` kebab-case, 1-64 chars, no `anthropic` or `claude` | ERROR | quick_validate.py, Anthropic docs |
| `description` non-empty, at most 1024 chars, no `<` or `>` | ERROR | quick_validate.py |
| `compatibility`, when present, at most 500 chars | ERROR | agentskills.io |
| `name` equals the folder name | WARN | agentskills.io, opencode |
| `description` on one physical line: a block scalar (`>`, `\|`) or a value that continues onto a following line (a quoted string closed there, a hand-wrapped plain scalar) is reported; if double-quoted, no inner `"` (quote triggers with `'`) | WARN | gemini-cli validate_skill.cjs |
| `metadata` values are strings | WARN | agentskills.io |
| Body under 500 lines; no nested `SKILL.md`; LF line endings | WARN | Anthropic best practices, OpenAI API, opencode |
| Description over 500 chars (Codex shortens it under budget); `metadata.description-reviewed` (a review date) silences it, recording a hand review that the key use case leads, and the trigger-loss gate still applies | WARN | openai/codex skills loader |
| Claude Code-only keys (`argument-hint`, `disable-model-invocation`, ...) | WARN | strip when packaging for upload |

The 500-line body limit is the one limit this skill uses everywhere
(`MAX_BODY_LINES`, the S-tier indicators and the validation checklist).

## Disclosure and ghost tools: which paths count

- SKILL.md: every `references/`, `scripts/`, `assets/`, `templates/`, `data/`
  or `bin/` path it names.
- `references/**/*.md`: only lines that tell the agent to run or load
  something (run, python3, bash, node, see, read, load, open, follow). A
  references file often describes files in the user's project or files a run
  will create, so a bare mention is not a claim that the skill ships the file.
  Fences tagged `text`, `tree`, `markdown` or `md` and quoted illustrations
  (`says:`, `e.g.`, `for example`) are skipped.
- Prefixes `${CLAUDE_SKILL_DIR}/`, `$CLAUDE_SKILL_DIR/`, `$SKILL_ROOT/`,
  `$SKILL_DIR/` and `./` resolve to the skill folder. Any other variable
  (`$CK/scripts/x.py`) names another tree and is skipped.
- A path after another tree's root on the same line (`C:\`, any drive letter,
  `/mnt/`, `~/`, `$HOME/`, `/home/`, `/Users/`) belongs to that tree. Measured
  false alarm: `system-checkup/SKILL.md` named `data/annotations.json` inside
  `C:\Users\...\downloads-desktop-cleanup.livingdoc`.
- A path right after another skill's name ("the humanize-writing skill's
  `references/ai-vocabulary-list.md`") belongs to that skill.
- A references file may name a sibling relative to itself; either resolution
  counts as present.
- Ghost tools: a script on a run line that the skill does not ship. A path
  with a directory outside the disclosure directories (`helpers/x.py`) counts
  too, unless its first directory is a user-tree or run-output directory
  (`src/`, `lib/`, `app/`, `public/`, `out/`, `tmp/` and the rest of
  `USER_TREE_DIRS`), its first segment is a host without a scheme
  (`bun.sh/install.ps1`), its file name is a product (`React/Next.js`) or a
  placeholder (`tests/test_foo.py`), or the line places it in the user's tree.
  Measured false alarms behind each exemption (2.5.1 corpus run): aaron-job-search,
  damage-control, project-archive's recorded `out/evidence/tools/*.py`, graphify.
- Ghost tools skip framework entry points that live in the user's project
  (`manage.py`, `setup.py`, `server.js`, `index.js`, `app.py` and similar) and
  any bare name on a line that places it in "your project", "the repo" or the
  user's code. Cue words inside a file name (the `.sh` in `install.sh`) do
  not count.

## Shipped but unreferenced: the whole folder

The whole skill folder ships to every harness and upload, so the whole folder
is scanned, not only the disclosure directories. Measured miss before 2.5.0:
`skill-audit/SKILL.md.bak` (21 KB, full skill frontmatter) sat at the skill
root unflagged.

- Orphans: files nothing reaches from SKILL.md, directly, through a reached
  text file, or by a Python import. Names match as whole path segments:
  `notes.md` is reached by `./notes.md`, `refs/notes.md` or a sentence-final
  `notes.md.`, never by `release-notes.md` or `notes.md.bak`. A reached text also reaches every file
  under a directory it names (`pipeline/`, `always_on/`), every match of a
  glob with a directory part (`schemas/*.schema.json`), and a directory named
  as a range (`prompts/W1-a.md through prompts/W5-e.md`) when both endpoints
  exist. A bare top-level `references/` or `scripts/` is convention talk and
  reaches nothing.
- Companions are exempt: `README.md`, `LICENSE*`, `CHANGELOG.md`,
  `marketplace.json`, `package.json`, `requirements.txt`, `pyproject.toml`;
  `__init__.py` and lockfiles beside any reached file. Development companions
  are exempt too: anything under `tests/` or `evals/`, `SKILL.md.tmpl` (source
  template for a generated SKILL.md), `.provenance.yaml`, `.provenance.json`.
- Stray backups anywhere: `*.bak`, `*.orig`, `*.old`, `*~`.
- Any file other than SKILL.md carrying skill frontmatter (`name:` plus
  `description:`) outside `references/`. Files under `references/` are covered
  by the hidden-skill effectiveness check instead. Both checks exempt a
  non-backup file that SKILL.md, or a file it reaches, names by path: that is a
  deliberate load, such as skill-doctor's `$SKILL_ROOT/scorers/*.md` rubrics
  (judgment from b4886c1). A basename mention alone does not exempt it.
- Caches and session state: `__pycache__`, `.pytest_cache`, `.mypy_cache`,
  `.ruff_cache`, `.omc`, `.pyc`, `.DS_Store`. Packaged archives at the root and
  nested skill copies.

## Effectiveness details

- Links: a `<file>.md#<anchor>` target resolves relative to the file that holds it,
  or to the skill root; `(#anchor)` resolves in the same file. Headings and
  links inside fenced code are template text and are ignored. Duplicate
  headings get GitHub's `-1`, `-2` suffixes; `id="x"` and `{#x}` anchors count.
  A missing bare file name with no directory part (`intent.md#prior-art`) that
  exists nowhere in the skill names a generated or user document and is
  skipped; a missing target with a directory (`references/<file>.md#<anchor>`)
  is dead. A plain link with no anchor (`[x](references/<file>.md)`) follows
  the same resolution and bare-name rule, in SKILL.md and in every reference
  file, whatever words surround it.
- Private data (ERROR): claude.ai chat URLs and key shapes `sk-ant-`,
  `sk-proj-`, `sk-`, `ghp_`/`gho_`/`ghs_`/`ghu_`/`ghr_`, `github_pat_`,
  `xoxb-`/`xoxp-`, `AIza`, `AKIA`. Scanned in every md, txt, json, yaml, yml,
  toml, py, sh, js, ts and `.env` file. A match containing `EXAMPLE` (AWS
  documents `AKIAIOSFODNN7EXAMPLE`) or a placeholder word (your, placeholder,
  redacted, dummy, xxxx) is documentation and is allowed.
- Budget: SKILL.md over 25,000 bytes is reported in decimal KB with one
  decimal and the exact byte count, so 25,164 B prints as `25.2 KB (25,164 B)`.
- Version drift: frontmatter `ver:` or `version:` under `assets/` or
  `templates/` versions the document a skill generates, not the skill, and is
  not compared with `metadata.version`.
- Undeclared triggers: a skill that quotes no trigger phrases may still
  activate from its prose; it is listed because trigger collisions cannot be
  checked for it.
