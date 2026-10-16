# Design Document Template

> This template produces output compatible with SpecKit (`speckit.plan`), OpenSpec (`design.md`), Cursor, Kiro, and generic spec-driven workflows. Unlike the requirements document, this IS technology-specific.

## Template Structure

```markdown
---
date: {{DATE}} {{TIME}} {{TZ}}
ver: 1.0.0
author: {{AUTHOR}}
model: {{MODEL}}
tags: [{{TAGS}}]
---

# [Project Name] -- Technical Design v1.0

## 1. Architecture Overview

[1-2 paragraphs summarizing the system architecture at the highest level.
Include an ASCII diagram showing major components and their relationships.]

```
[ASCII architecture diagram here]
```

### 1.1 What This System Does NOT Do

[Explicit exclusion list. Prevents scope creep during implementation.
List 3-8 things that are adjacent to the system's purpose but explicitly out of scope.]

## 2. Technology Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Language | [e.g., TypeScript] | [Why this over alternatives] |
| Framework | [e.g., SvelteKit] | [Why this fits the requirements] |
| Runtime | [e.g., Bun] | [Performance/compatibility reasoning] |
| Database | [e.g., PostgreSQL] | [Based on data architecture analysis] |
| Styling | [e.g., Tailwind CSS v4 + shadcn-svelte] | [Design system alignment] |
| Testing | [e.g., Vitest + Playwright] | [Coverage strategy rationale] |
| Deployment | [e.g., Cloudflare Workers] | [Cost/performance/region reasoning] |

### 2.1 Technology Decision Records

[For any non-obvious stack choice, provide a brief ADR-style justification:]

**Decision: [Choice]**
- Context: [What drove this decision]
- Options considered: [2-3 alternatives evaluated]
- Chosen because: [Primary deciding factor]
- Trade-offs accepted: [What you give up]

## 3. Data Model

### 3.1 Schema Design

[Include actual schema with types. This is the implementation view of the Key Entities from requirements.md.]

```sql
-- or equivalent schema notation for the chosen storage
CREATE TABLE [entity] (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    [field]     [type] NOT NULL,
    [field]     [type],
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

[For document stores, show the document shape:]

```typescript
interface [Entity] {
    id: string;
    [field]: [type];
}
```

### 3.2 Relationships and Access Patterns

[Describe joins, indexes, and query patterns:]

| Query Pattern | Frequency | Implementation |
|---------------|-----------|---------------|
| [e.g., "Get user's recent items"] | High-frequency read | [Index strategy, caching approach] |
| [e.g., "Aggregate monthly stats"] | Daily batch | [Materialized view or scheduled job] |

### 3.3 Migration Strategy

[How the schema evolves: migration tool, versioning approach, rollback plan]

## 4. Component Specifications

### 4.1 [Component Name] (`path/to/component`)

[For each major component, describe:]
- **Responsibility:** What it does (single responsibility)
- **Interface:** Public API/exports
- **Dependencies:** What it consumes
- **Error handling:** How failures surface

[Include code-level interface definitions where they clarify intent:]

```typescript
// Interface definition (not implementation)
interface [ComponentName] {
    [method](args: [Type]): Promise<[ReturnType]>;
}
```

### 4.2 [Next Component]

## 5. API / Interface Contracts

[Define external interfaces: REST endpoints, CLI commands, WebSocket events, message formats]

### 5.1 [Interface Group]

```
[METHOD] /api/[resource]
  Request:  { [field]: [type] }
  Response: { [field]: [type] }
  Errors:   [4xx/5xx scenarios]
```

## 6. UX Architecture

### 6.1 Interaction Model

[Describe the primary interaction pattern and why it fits:]
- Navigation structure (pages, modals, wizards, tabs)
- State management approach
- Loading/error/empty states strategy
- Responsive behavior

### 6.2 Design System Alignment

[How the chosen design system/library maps to the UX requirements:]
- Component library: [e.g., shadcn-svelte]
- Typography: [font choices and scale]
- Color strategy: [dark mode, theming, accessibility contrast]
- Animation approach: [transitions, micro-interactions]

### 6.3 Adoption and Onboarding

[How the UX facilitates user adoption:]
- First-run experience
- Progressive disclosure of features
- Help/documentation integration
- Feedback mechanisms

## 7. Hosting and Deployment

### 7.1 Infrastructure

| Component | Service | Tier | Rationale |
|-----------|---------|------|-----------|
| [e.g., Frontend] | [e.g., Cloudflare Pages] | [Free/Pro] | [Why this service] |
| [e.g., API] | [e.g., Cloudflare Workers] | [Free] | [Why this service] |
| [e.g., Database] | [e.g., Turso] | [Free tier] | [Why this service] |

### 7.2 CI/CD Pipeline

[Build, test, deploy workflow description]

### 7.3 Environment Strategy

[Development, staging, production configuration]

## 8. Security Considerations

### 8.1 Threat Model

[Key attack vectors relevant to this system and mitigations]

### 8.2 Authentication / Authorization

[Auth strategy, session management, permission model]

### 8.3 Data Protection

[Encryption at rest/transit, PII handling, secrets management]

### 8.4 Supply Chain Security

[Dependency audit strategy, lockfile enforcement, automated vulnerability scanning (e.g., npm audit, cargo audit, pip-audit)]

## 9. Implementation Phases

[No dates. Use phase/step notation only.]

### Phase 1: [Name]
- [Deliverable]
- [Deliverable]
- Validates: FR-001, FR-002

### Phase 2: [Name]
- [Deliverable]
- [Deliverable]
- Validates: FR-010, FR-011

[Each phase should validate specific FRs from the requirements document.
Order phases by dependency and risk -- highest risk first.]

## 10. Testing Strategy

### 10.1 Unit Tests
| Module | Key Test Cases |
|--------|---------------|
| [Module] | [What gets tested] |

### 10.2 Integration Tests
| Scenario | Validates |
|----------|----------|
| [End-to-end flow] | [Which FRs are covered] |

### 10.3 Performance Benchmarks
| Benchmark | Target | Method |
|-----------|--------|--------|
| [Operation] | [NFR target] | [How measured] |

## 11. Project Structure

```
project-root/
├── src/
│   ├── [organized by feature or layer]
│   └── ...
├── tests/
├── docs/
└── [config files]
```

[Justify the directory organization choice: feature-based, layer-based, or hybrid]

## 12. References

1. [Source/tool/paper referenced in design decisions]
```

## Section Classification

**Mandatory (always include):**
- Architecture Overview, Technology Stack, Data Model, Implementation Phases, Project Structure

**Conditional (include when relevant):**
- Component Specifications (when system has 3+ components)
- API/Interface Contracts (when system exposes APIs)
- UX Architecture (when system has a user interface)
- Hosting and Deployment (when deployment target matters)
- Security Considerations (when handling user data or network-exposed)
- Testing Strategy (when testing approach is non-trivial)
- References (when design decisions cite external sources)

**Rules:**
- Every section must trace back to requirements in requirements.md
- Technology choices require rationale, not just listing
- ASCII diagrams for architecture (not image references)
- Schema definitions use concrete types, not placeholders
- Implementation phases reference specific FR-XXX identifiers
- No dates or timestamps in phases (use phase/step notation)
