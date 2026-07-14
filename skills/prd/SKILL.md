---
name: prd
description: 'Generate high-quality Product Requirements Documents (PRDs) for software systems and AI-powered features. Includes executive summaries, user stories, technical constraints, and risk analysis.'
license: MIT
---

# Product Requirements Document (PRD)

## Overview

Design comprehensive, production-grade Product Requirements Documents (PRDs) that bridge the gap between business vision and technical execution. This skill works for modern software systems, ensuring that requirements are clearly defined.

## When to Use

Use this skill when:

- Starting a new product or feature development cycle
- Translating a vague idea into a concrete technical specification
- Defining requirements for AI-powered features
- Stakeholders need a unified "source of truth" for project scope
- User asks to "write a PRD", "document requirements", or "plan a feature"

---

## Operational Workflow

### Phase 1: Discovery (The Interview)

Before writing a single line of the PRD, you **MUST** interrogate the user to fill knowledge gaps. Do not assume context.

**Ask about:**

- **The Core Problem**: Why are we building this now?
- **Existing Inputs**: What already exists — prototypes, mockups, brand, design system, UI language, reference products, prior docs? Inventory them first; the PRD cites them as sources. "Nothing exists" is a valid answer recorded explicitly.
- **Success Metrics**: How do we know it worked?
- **Constraints**: Budget, tech stack, or deadline?

### Phase 2: Analysis & Scoping

Synthesize the user's input. Identify dependencies and hidden complexities.

- Map out the **User Flow**.
- Define **Non-Goals** to protect the timeline.
- Record assumptions and uncertainties with their source, impact, confidence, owner, and validation method.
- Compare at least two plausible scope alternatives and state the selected trade-off.
- Test negative scenarios, dependency failures, conflicting stakeholder needs, and missing NFRs.

### Phase 3: Technical Drafting

Generate the document using the **Strict PRD Schema** below.

---

## PRD Quality Standards

### Requirements Quality

Use concrete, measurable criteria. Avoid "fast", "easy", or "intuitive".

Every requirement and decision must trace to the user's request, a user-provided input, or cited project code. Mark any requirement with no source `invented — requires user confirmation` and register it as an open question. Give every acceptance criterion a stable `AC-###` ID; once assigned, never renumber, reuse, or transfer it to another criterion. Retire obsolete IDs explicitly.

```diff
# Vague (BAD)
- The search should be fast and return relevant results.
- The UI must look modern and be easy to use.

# Concrete (GOOD)
+ The search must return results within 200ms for a 10k record dataset.
+ The search algorithm must achieve >= 85% Precision@10 in benchmark evals.
+ The UI must follow the 'Vercel/Next.js' design system and achieve 100% Lighthouse Accessibility score.
```

---

## Strict PRD Schema

You **MUST** follow this exact structure for the output:

### 1. Executive Summary

- **Problem Statement**: 1-2 sentences on the pain point.
- **Proposed Solution**: 1-2 sentences on the fix.
- **Success Criteria**: 3-5 measurable KPIs.
- **Definition of Ready**: what the user can actually do against the real external dependencies when the product is done; mock or stub mode never satisfies it.

### 2. User Experience & Functionality

- **User Personas**: Who is this for?
- **User Stories**: `As a [user], I want to [action] so that [benefit].`
- **Acceptance Criteria**: Bulleted list of "Done" definitions for each story.
- **Requirement IDs**: Number functional requirements as `FR-###` and acceptance criteria as executable `AC-###` statements.
- **Non-Goals**: What are we NOT building?

### 3. AI System Requirements (If Applicable)

- **Tool Requirements**: What tools and APIs are needed?
- **Evaluation Strategy**: How to measure output quality and accuracy.

### 4. Technical Constraints & Known Integrations

- **Technical Constraints**: Only constraints stated by the user or derived from cited project code.
- **Known Integrations**: Existing APIs, data stores, and authentication boundaries observed in cited code; do not design replacements or new interactions.
- **Security & Privacy Requirements**: Required outcomes, data-handling rules, and compliance constraints without prescribing implementation.
- **No HOW Decisions**: Leave architecture, data flow, API shape, storage design, and authentication design to downstream architecture work.

### 5. Assumptions, Uncertainties & Open Questions

- **Register**: Statement, source/evidence, impact, categorical confidence (`low`, `medium`, `high`, or `unknown`), owner, and validation method.
- **Open Questions**: `OQ-###` — question, affected FR/AC-IDs, and a `Confirm before:` trigger (slice or phase). Triggered questions must be answered by the user or explicitly waived before the gated work starts.

### 6. Scope Alternatives & Trade-offs

- **Alternatives**: At least two plausible boundaries.
- **Decision**: Selected alternative, evidence-backed reason, and what is traded away.

### 7. Negative Scenarios

- **Failure Cases**: Invalid, conflicting, unavailable, dependency-failure, and relevant NFR scenarios.
- **Expected Behavior**: Product response and affected FR/AC-IDs.

### 8. Decisions & Residual Risks

- **Decision Record**: Decision, source/evidence, and affected requirements.
- **Residual Risk**: Mitigation, verification, or explicit acceptance.

### 9. Risks & Roadmap

- **Phased Rollout**: MVP -> v1.1 -> v2.0.
- **Technical Risks**: Latency, cost, or dependency failures.

---

## Implementation Guidelines

### DO (Always)

- **Define Testing**: For AI systems, specify how to test and validate output quality.
- **Iterate**: Present a draft and ask for feedback on specific sections.
- **Keep one normative artifact**: The PRD creator updates the same PRD and never creates a separate adversarial challenge document.
- **Disposition every challenge**: On a `CH-PRD-*` revision, return exactly one of `accepted_and_fixed`, `rejected_with_evidence`, or `needs_decision`, with citations.
- **Make residual risk explicit**: Record mitigation, verification, or acceptance in the PRD.

### DON'T (Avoid)

- **Skip Discovery**: Never write a PRD without asking at least 2 clarifying questions first.
- **Hallucinate Constraints**: If the user didn't specify a tech stack, ask or label it as `TBD`.
- **Invent probabilities**: Use categorical impact and confidence or `unknown`.
- **Rewrite IDs**: Never renumber or reuse an assigned AC-ID.
- **Mock-Ready**: Never define done through mock-mode criteria alone when the product's value requires real integrations.

---

## Example: Intelligent Search System

### 1. Executive Summary

**Problem**: Users struggle to find specific documentation snippets in massive repositories.
**Solution**: An intelligent search system that provides direct answers with source citations.
**Success**:

- Reduce search time by 50%.
- Citation accuracy >= 95%.

### 2. User Stories

- **Story**: As a developer, I want to ask natural language questions so I don't have to guess keywords.
- **AC**:
  - Supports multi-turn clarification.
  - Returns code blocks with "Copy" button.

### 3. AI System Architecture

- **Tools Required**: `codesearch`, `grep`, `webfetch`.

### 4. Evaluation

- **Benchmark**: Test with 50 common developer questions.
- **Pass Rate**: 90% must match expected citations.
