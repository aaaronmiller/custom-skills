# Requirements Document Template

> This template produces output compatible with SpecKit (`speckit.specify`), OpenSpec (`opsx:propose`), Cursor, Kiro, and generic spec-driven workflows.

## Template Structure

```markdown
---
date: {{DATE}} {{TIME}} {{TZ}}
ver: 1.0.0
author: {{AUTHOR}}
model: {{MODEL}}
tags: [{{TAGS}}]
---

# [Project Name] -- Requirements Specification v1.0

## 1. Purpose

[1-3 paragraphs explaining what this project delivers and why it exists.
Focus on the problem being solved and the value created.
No technology mentions. Written for business stakeholders.]

## 2. Glossary

| Term | Definition |
|------|-----------|
| **[Domain Term]** | [Plain-language definition accessible to non-technical readers] |

## 3. User Scenarios

### 3.1 Primary User Story

As a [user type], I want to [action] so that [outcome].

### 3.2 Acceptance Scenarios

**Scenario 1: [Happy Path Name]**
- Given: [precondition]
- When: [action]
- Then: [expected result]

**Scenario 2: [Edge Case Name]**
- Given: [precondition]
- When: [action]
- Then: [expected result]

[Include 3-5 scenarios covering primary flow, key edge cases, and error conditions]

## 4. Functional Requirements

### 4.1 [Feature Group Name]

**FR-001**: The system SHALL [requirement using SHALL/MUST/SHOULD language].
- Acceptance: [How to verify this requirement is met]

**FR-002**: The system MUST [requirement].
- Acceptance: [Verification method]

[Group requirements logically by feature area.
Each requirement gets a unique FR-XXX identifier.
Every requirement includes acceptance criteria.
Use SHALL for mandatory, SHOULD for recommended, MAY for optional.]

### 4.2 [Next Feature Group]

**FR-010**: ...

## 5. Non-Functional Requirements

### 5.1 Performance

**NFR-001**: [Measurable performance target, e.g., "System SHALL respond to user queries within 200ms at P95"]

### 5.2 Reliability

**NFR-010**: [Availability, fault tolerance, data durability targets]

### 5.3 Security

**NFR-020**: [Authentication, authorization, data protection requirements]

### 5.4 Scalability

**NFR-030**: [Expected load, growth projections, scaling requirements]

### 5.5 Accessibility

**NFR-040**: [WCAG level, screen reader support, keyboard navigation]

[Only include subsections relevant to the project. Remove unused sections entirely.]

## 6. Key Entities

[Conceptual data model. Describe WHAT the entities represent and their relationships.
Do NOT include implementation details like column types, table names, or database technology.]

| Entity | Description | Key Attributes | Relationships |
|--------|-------------|----------------|---------------|
| [Entity 1] | [What it represents] | [Important attributes without types] | [Related to Entity 2 via...] |

## 7. Success Criteria

SC-001: [Measurable user-facing metric, e.g., "Users complete primary workflow in under 3 minutes"]
SC-002: [Measurable system metric, e.g., "System handles 500 concurrent users without degradation"]
SC-003: [Business metric, e.g., "Reduce manual process time by 60%"]

## 8. Prior Art Analysis

### 8.1 Existing Solutions

| Solution | Strengths | Weaknesses | Gap This Project Fills |
|----------|-----------|------------|----------------------|
| [Tool/Project] | [What it does well] | [Where it falls short] | [Why build instead of use] |

### 8.2 Patterns Adopted

[Describe architectural or UX patterns borrowed from prior art and why they fit.]

### 8.3 Patterns Avoided

[Describe approaches considered and rejected, with rationale.]

## 9. Assumptions and Dependencies

### Assumptions
- [Assumption about users, e.g., "Users have stable internet connectivity"]
- [Assumption about scope, e.g., "Mobile support is out of scope for v1"]

### Dependencies
- [External dependency, e.g., "Requires access to [API/Service]"]
- [Infrastructure dependency, e.g., "Assumes Docker-capable deployment environment"]

## 10. Identified Risks

| # | Risk | Severity | Mitigation | Related Req |
|---|------|----------|-----------|-------------|
| 1 | [Risk description] | Critical/High/Medium/Low | [Mitigation strategy] | FR-XXX |

## 11. Scope Boundaries

### In Scope
- [Explicitly included feature/capability]

### Out of Scope
- [Explicitly excluded feature/capability with brief rationale]

### Future Considerations
- [Features deferred to later versions]
```

## Section Classification

**Mandatory (always include):**
- Purpose, User Scenarios, Functional Requirements, Non-Functional Requirements, Key Entities, Success Criteria, Scope Boundaries

**Conditional (include when relevant):**
- Glossary (when domain jargon exists)
- Prior Art Analysis (always when Phase 2 research found relevant alternatives)
- Assumptions and Dependencies (when external factors constrain the project)
- Identified Risks (when non-trivial risks exist)

**Rules:**
- When a section does not apply, remove it entirely (never leave as "N/A")
- Maximum 3 `[NEEDS CLARIFICATION]` markers. Use only for decisions that significantly impact scope
- Every FR must have acceptance criteria
- No technology, framework, API, or implementation detail in this document
- Written for non-technical stakeholders where possible
- Requirements must be testable and unambiguous
