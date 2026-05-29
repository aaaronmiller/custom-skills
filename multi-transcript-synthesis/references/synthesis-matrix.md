# Synthesis Matrix

The synthesis matrix is the core analytical tool for cross-file idea comparison. Build it during Phase 3 (Idea Harvest) to systematically extract, compare, and evaluate ideas across all source documents.

## How to Build

### Step 1: Identify Themes

After reading all files, identify the 5–15 major themes or decision areas. These become the rows of the matrix.

Examples of themes:
- Architecture approach
- Data storage strategy
- Distribution mechanism
- Merge strategy
- User interface
- Deployment model
- Testing approach

### Step 2: Fill the Matrix

For each theme, record what EACH file proposes:

| Theme | File 1 | File 2 | File 3 | File 4 | File 5 | Resolution |
|-------|--------|--------|--------|--------|--------|------------|
| Architecture | "5-layer monolith" | "microservices" | "extension layer on existing" | (silent) | "plugin system" | Extension layer — user already has working L1-L3 |
| Storage | "SQLite registry" | "YAML manifests" | "Git-native" | "JSON index" | "SQLite + YAML" | YAML manifests (simpler, Git-friendly, user prefers) |
| Distribution | "Built-in symlinker" | "Delegate to skillshare" | "Wrap existing sync.sh" | "Custom copy engine" | "npm-style package links" | Wrap sync.sh — it already works for 18 platforms |

### Step 3: Classify Each Idea

Mark each cell with a confidence indicator:

- **🟢 Reinforced** — Same idea appears in 2+ files (high confidence)
- **🟡 Unique** — Appears in only one file but is genuinely valuable
- **🔴 Contested** — Two files disagree on approach
- **⚪ Silent** — File doesn't address this theme

### Step 4: Resolve Contests

For each 🔴 Contested item, evaluate using these criteria (in order):

1. **User intent alignment** — Which position better matches what the user actually asked for?
2. **Existing infrastructure** — Does the user already have something working? If so, extend it.
3. **Simplicity** — Which is simpler to implement and maintain?
4. **Research grounding** — Which approach has more existing tools/precedent?
5. **Model consensus** — If 3 out of 4 models agree, the outlier needs strong justification to win.

## Template

```markdown
## Synthesis Matrix: [Project Name]

### Themes Identified

1. [Theme 1]
2. [Theme 2]
...

### Matrix

| Theme | [File 1 name] | [File 2 name] | [File 3 name] | Confidence | Resolution |
|-------|------|------|------|------|------|
| [Theme 1] | [position] | [position] | [position] | 🟢/🟡/🔴 | [chosen approach + why] |
| [Theme 2] | [position] | [position] | [position] | 🟢/🟡/🔴 | [chosen approach + why] |

### Key Unique Ideas Worth Including

- From [File X]: [Idea] — valuable because [reason]
- From [File Y]: [Idea] — valuable because [reason]

### Best Code Snippets

- From [File X]: [Schema/pseudocode description] — useful as starter material
```

## When the Matrix is Done

The matrix should produce a clear "best version" composite that takes the strongest ideas from each source. If a theme has no clear resolution, flag it as an open question for the user.

The resolution column becomes the backbone of the requirements document.
