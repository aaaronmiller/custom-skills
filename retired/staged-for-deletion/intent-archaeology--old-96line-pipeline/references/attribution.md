# Attribution ladder

Phase 2 reference. Most of the pipeline's accuracy is won or lost here, and
it should involve almost no model.

| Rung | Method | Confidence | Notes |
|---|---|---|---|
| 1 | Session `cwd` resolves inside a known project path | 1.0 | Should cover the majority |
| 2 | Git identity: remote URL or initial commit sha | 1.0 | Key on identity, never path. `~/code2` exists because paths change. |
| 3 | Absolute paths in tool calls fall inside one project | 0.6-1.0 | Requires 60 percent concentration in one project |
| 4 | Branch name matches a project | 0.7 | Spec-kit encodes feature ids in branches |
| 5 | Workspace basename matches a project slug | 0.5 | Not deterministic. Spot-check these. |
| 6 | Unattributed | 0.0 | Left for a human. Never guessed. |

## Why the ladder rather than a classifier

A silent attribution error is the worst failure this pipeline has: one
project's sessions land under another, everything downstream is confidently
wrong, and nothing looks broken. Deterministic rungs are checkable; a
classifier's mistakes are not.

## Reading the coverage number

Rungs 1 to 4 are the trust signal. Below 70 percent means most sessions were
started from `~` rather than a project root, and you should expect a long
manual tail. Report the number rather than hiding it; every later confidence
claim inherits it.

## Fixing the residual by hand

```bash
sqlite3 ~/.intent-archaeology/archaeology.db \
  "UPDATE session SET project_id='<slug>', attribution_method='manual', attribution_rung=1, attribution_confidence=1.0 WHERE source_path='<path>'"
```

Manual attributions are recorded as rung 1 because a human decision is the
strongest evidence available.
