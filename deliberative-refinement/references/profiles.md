# Intensity Profiles

## Summary

| Profile | V(X, Y, S) | Use Case |
|---------|------------|----------|
| Lite | V(3, 1, 0) | Quick validation, low stakes |
| **Standard** | **V(8, 3, 1)** | **Default** |
| Deep | V(12, 5, 2) | Important decisions |
| Exhaustive | V(15, 5, 3) | Critical outcomes |

## Parameters

### X: Agent Count
- 3-5: Quick check
- 7-9: Standard deliberation
- 12-15: High-stakes, diverse perspectives

### Y: Rounds
- 1: Single pass
- 3: Standard with refinement
- 5: Deep analysis

### S: Probes (Evidence Grounding)
- 0: No grounding (speed)
- 1: LINEAR — deep dive on key finding
- 2: LINEAR — two-stage verification
- 3: BRANCHING — triangulate 3 sources

## Probe Strategies

**LINEAR (DEPTH)**
```
Probe 1: Initial search
Probe 2: Deeper on key finding
Probe 3: Verify specific claim
```

**BRANCHING (BREADTH)**
```
Probe 1: Source A
Probe 2: Source B (independent)
Probe 3: Source C (independent)
```

## Selection

| Signal | Profile |
|--------|---------|
| "quick check" | Lite |
| "help me", "think through" | Standard |
| "important", "careful" | Deep |
| "bulletproof", "critical" | Exhaustive |
| Ambiguous | Standard |

## Variants

| Variant | Config | Notes |
|---------|--------|-------|
| **Flash** | V(5,2,1) | LINEAR only, ~3x faster |
| **Pro** | V(8,3,1) | Full BRANCHING support |
