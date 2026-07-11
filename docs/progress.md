# Progress Ledger

## Goal

Implement mandatory adversarial debate for every PRD and execution plan while preserving the existing evidence and document-review gates.

## Acceptance Criteria

- AC-001: A read-only `adversarial-reviewer` supports PRD and Plan modes with stable challenge IDs and evidence-backed verdicts.
- AC-002: Product and planner agents remain sole artifact writers and record assumptions, alternatives, dispositions, and residual risks.
- AC-003: Universal, Node, Python, shortcut, and Codex workflows enforce up to three debate cycles followed by arbitration/final document review.
- AC-004: Debate state and retry budgets remain distinct from the existing two-rework document-review gate.
- AC-005: Workflow, lifecycle, role inventory, and platform documentation consistently describe the new behavior.
- AC-006: Routing and workflow evaluations cover PRD/Plan debate and preserve existing regressions without modifying the immutable autoresearch scorer.

## Tasks

| Task | Agent | Status | Evidence |
|---|---|---|---|
| Agent contracts | Agent Prompt Engineer | DONE | New read-only two-mode challenger; creator/reviewer contracts passed re-review with file:line evidence |
| Orchestration | Workflow Engineer | DONE | Universal/Node/Python, shortcuts, and Codex lifecycle passed parity review |
| Documentation | Technical Writer | DONE | Final documentation gate passed; five Mermaid blocks balanced and lifecycle wording consistent |
| Evaluations | Test Engineer | DONE_WITH_CONCERNS | Static suite 16/16 PASS; 8 model-backed cases emitted as UNVERIFIED pending baseline |
| Inline and cross-cutting review | Code/Doc Reviewers | DONE | Agent, orchestration, documentation, and eval gates all returned PASS after rework |

## Decisions

- One internal `adversarial-reviewer` uses PRD and Plan modes; no public shortcut is added.
- Creators own normative documents; reviewers remain read-only and no challenge file is created.
- Debate permits three cycles, independently of the existing two normal-review reworks.
- `doc-reviewer` arbitrates unresolved items after cycle three and still provides the final document gate.
- The cycle-three arbitration dispatch performs the full review and replaces, rather than precedes, ordinary review.
- The isolated adversarial v1 suite remains outside aggregate scoring until its model-backed baseline is recorded.

## Open Questions

- Model-backed AP-M001 through AP-M008 remain UNVERIFIED until a separate baseline run is authorized and recorded.
