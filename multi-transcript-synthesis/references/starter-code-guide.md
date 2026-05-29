# Starter Code Guide

When source documents contain code snippets, schemas, pseudocode, or data models, preserve the valuable ones in a `references/starter-code.md` file alongside the requirements and design documents.

## Why Preserve Code

Models produce better output when they have existing material to evaluate and improve rather than generating from zero. Even if the build agent rewrites everything, having starter code:

1. **Anchors thinking** — The model studies the proposed approach before inventing its own
2. **Preserves domain knowledge** — Schemas and types encode complex decisions that are easy to lose in prose
3. **Reduces cold-start time** — The build agent doesn't re-derive data models from requirements text
4. **Catches implicit decisions** — Code reveals assumptions that prose doesn't (field types, optional vs required, naming conventions)

## What to Preserve

### High Value (Always Preserve)
- **TypeScript/Python type definitions** — interfaces, types, enums, schemas
- **YAML/JSON schemas** — configuration formats, data models
- **Algorithm pseudocode** — merge strategies, scoring formulas, decision trees
- **Directory structures** — proposed file trees
- **CLI command tables** — command names, flags, descriptions

### Medium Value (Preserve if Well-Designed)
- **Configuration examples** — sample YAML/JSON for adapters, manifests
- **API interface definitions** — abstract interfaces, method signatures
- **State machine diagrams** — lifecycle flows, status transitions

### Low Value (Summarize in Prose Instead)
- **Boilerplate code** — standard Express/Hono server setup, package.json
- **Obvious implementations** — file reading, JSON parsing
- **Framework-specific code** — React components, Svelte templates (recreate fresh)

## Format

```markdown
# Starter Code Reference — [Project Name]

> These snippets are extracted from source documents and preserved as starting 
> material for the build agent. They encode design decisions, schemas, and 
> algorithms that should be reviewed before implementation. The build agent 
> may rewrite, extend, or discard them — but should read them first.

## Data Models

### [Model Name]
**Source:** [filename], lines [X–Y]
**Notes:** [why this is preserved, any caveats]

\`\`\`typescript
// [code here]
\`\`\`

## Algorithms

### [Algorithm Name]
**Source:** [filename]
**Notes:** [context]

\`\`\`
// [pseudocode here]
\`\`\`

## Configuration Schemas

### [Config Name]
**Source:** [filename]
**Notes:** [context]

\`\`\`yaml
# [schema here]
\`\`\`
```

## When NOT to Include Starter Code

- When the source code is from an obviously wrong approach (model was off-track)
- When the code is for a component that already exists in the user's infrastructure
- When the code is language-specific but the build agent will use a different language
- When including it would bias the build agent toward a suboptimal approach

In these cases, note the snippet's existence in the scratchpad but don't promote it to starter-code.md. The build agent benefits from a clean slate when the existing code would mislead.

## The "Think About This" Pattern

For code that shouldn't be used directly but contains good ideas, use this pattern:

```markdown
### Distribution Strategy (Think About This)
**Source:** spec-v2.md
**Notes:** This proposes a custom distribution engine. The user already has 
sync.sh + skillshare handling distribution. DO NOT rebuild distribution. But 
the adapter interface pattern below is worth considering for the provenance layer.

\`\`\`typescript
// Only the interface is worth preserving — not the implementation
interface ToolAdapter {
  detect(): Promise<boolean>;
  getDistributionMode(type: ArtifactType): 'symlink' | 'copy' | 'generate';
}
\`\`\`
```

This gives the build agent the seed of an idea without leading them down the wrong path.
