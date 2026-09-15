# Document Review Dimensions

Applied by `doc-reviewer` as `Sweep` against the dispatched document(s). Run every
dimension every time. `n/a — <reason>` is valid; skipping a dimension silently is
not.

For each dimension: what to look for, and how to classify what you find under the
`review-contract` skill's three classes (`must-fix-now` blocks the gate and consumes
the rework budget; `fix-in-slice` is a real defect fixed in the same slice, no
dedicated rework round; `backlog` is recorded debt, never blocks).

## 1. Completeness

Look for: `TBD`, placeholder text, empty sections, sections present in the document
type's checklist (see dimension 7) but missing entirely.

- `must-fix-now`: a required section is empty or a placeholder on a document about to
  gate downstream work (e.g., an empty Acceptance Criteria section in a PRD).
- `fix-in-slice`: an optional or supplementary section left thin but not blocking.
- `backlog`: a nice-to-have elaboration (extra examples, more detail) not required by
  the checklist.

```
RV-PRD-001 | must-fix-now | Critical | docs/prd.md §Non-Functional Requirements | section reads "TBD — revisit after MVP" | fill in measurable targets or remove the section if genuinely out of scope for this slice, with a stated reason
```

## 2. Internal consistency

Look for: the same document asserting X in one place and not-X elsewhere — a
requirement stated one way in the narrative and differently in its own acceptance
criteria, an ID referenced before it is defined.

- `must-fix-now`: a direct contradiction that would cause a downstream agent to
  implement the wrong behavior depending on which passage it reads.
- `fix-in-slice`: an inconsistent term for the same concept (e.g., "order" vs.
  "purchase") with no behavioral ambiguity.
- `backlog`: an awkward phrasing that is not actually contradictory.

```
RV-PRD-004 | must-fix-now | Critical | docs/prd.md §FR-009 vs §AC-021 | FR-009 says password reset links expire in 24h, AC-021 tests a 1h expiry | reconcile to one value and update whichever passage is wrong
```

## 3. Cross-document consistency

Look for: alignment against every other document in `docs/` — PRD requirements match
architecture components, design screens cover all user stories and every use case
allowed for its role, plan covers all architecture components.

- `must-fix-now`: a component in the architecture with no corresponding PRD
  requirement (or vice versa), a design missing a screen for an in-scope use case, or
  a plan missing a slice for an architecture component.
- `fix-in-slice`: terminology drift between documents referring to the same entity.
- `backlog`: a cross-document cross-reference link that would be nice but is not
  required for actionability.

```
RV-PLAN-002 | must-fix-now | Critical | docs/plan.md vs docs/architecture.md §Notification Service | architecture defines a Notification Service component with no corresponding slice in the plan | add a slice (or an explicit task inside an existing slice) implementing the Notification Service, or record why it is out of scope
```

## 4. Actionability

Look for: whether the next agent can act without guessing — acceptance criteria are
testable (a command or test can objectively pass/fail them), architecture decisions
include rationale, design specs include component states.

- `must-fix-now`: an acceptance criterion or architecture decision so vague the next
  agent must invent behavior (e.g., "handle errors appropriately").
- `fix-in-slice`: a criterion that is testable but missing one edge case's expected
  behavior.
- `backlog`: a criterion that could be phrased more crisply but is unambiguous today.

```
RV-PRD-007 | must-fix-now | Critical | docs/prd.md §AC-030 | "the system should respond quickly" — no threshold, no Given/When/Then | rewrite as Given/When/Then with a measurable target, e.g. "response time < 200ms at p95"
```

## 5. Traceability

Look for: FR/AC/ROLE/UC/OQ IDs present, stable, not renumbered or reused across
revisions; every user-visible AC-ID appears in at least one use case's `Covers:` list.

- `must-fix-now`: an ID reused for two different requirements, or a renumbering that
  breaks a reference from another document (e.g., the plan citing an AC-ID that no
  longer exists at that number).
- `fix-in-slice`: a new requirement added without an ID assigned yet, caught before
  it propagates.
- `backlog`: an ID gap (e.g., AC-004 skipped) that is harmless and documented.

```
RV-PRD-010 | must-fix-now | Critical | docs/prd.md §AC-014 | AC-014 was originally "email must be unique"; this revision reused AC-014 for an unrelated password-length rule and moved the original to AC-014a | never reuse an ID — assign the new rule the next unused AC-ID and restore AC-014's original text
```

## 6. Source discipline

Look for: every requirement citing a source (a quote from the request, or file:line
of a user input or existing project code) or explicitly marked
`invented — requires user confirmation`.

- `must-fix-now`: a requirement with no source and no `invented` marker, presented as
  if it were user-specified — this misleads every downstream agent about what is
  confirmed.
- `fix-in-slice`: a source citation present but imprecise (points to the right doc,
  wrong section).
- `backlog`: a source citation that could be more specific but is not misleading.

```
RV-PRD-013 | must-fix-now | Critical | docs/prd.md §FR-022 | "users can export data as CSV" has no Source line and is not marked invented | add a Source citation, or mark "invented — requires user confirmation" and add an OQ-ID
```

## 7. Type-specific checklist

Apply the reviewer's own PRD / architecture / design / plan checklist — this
dimension is the per-document-type checklist owned and maintained in
`agents/doc-reviewer.md`. This skill does not duplicate that checklist; read it from
there and apply it in full for the document type under review.

- `must-fix-now`: failure of any checklist item the owning checklist itself marks as
  blocking (e.g., architecture's "no unresolved TBD or placeholder decisions").
- `fix-in-slice` / `backlog`: per the severity guidance already embedded in that
  checklist item.

```
RV-ARCH-005 | must-fix-now | Critical | docs/architecture.md §Local runtime topology | section is missing entirely though the PRD names a Postgres dependency | add the Local runtime topology section per the architecture checklist, listing the image, tag, env var, and health check
```

## 8. Technical accuracy

Look for: impossible constraints, contradictory requirements, missing error handling
paths described at the requirements or design level (not implementation-level bugs —
those are code dimensions).

- `must-fix-now`: a constraint that cannot be satisfied simultaneously with another
  stated constraint, or a described flow with no error path for a clearly reachable
  failure (e.g., a payment flow with no declined-card path).
- `fix-in-slice`: an error path described briefly that could use one more concrete
  detail.
- `backlog`: an edge case genuinely out of scope for this product's stated goals.

```
RV-PRD-016 | must-fix-now | Critical | docs/prd.md §FR-030 | requires "real-time sync" and separately "works fully offline with no conflicts" for the same data with no reconciliation strategy | either scope one behavior as primary and the other as best-effort, or add a conflict-resolution strategy
```

## 9. Local-stack and readiness clauses

Look for: a "Local runtime topology" or equivalent section naming every external
dependency with its container image/tag or emulator, and a Definition of Ready
stating what the user can do against real external integrations.

- `must-fix-now`: the document claims `Local stack: N/A` while the PRD or
  architecture names a database, queue, mail, storage, or third-party API dependency
  — this is always Critical per the doc-reviewer checklist.
- `fix-in-slice`: a named dependency present but missing its pinned tag or health
  check reference (the compose file itself is devops-engineer's scope; the doc only
  needs to name it correctly).
- `backlog`: a readiness clause that could name one more emulator limitation but does
  not currently mislead anyone.

```
RV-ARCH-008 | must-fix-now | Critical | docs/architecture.md §Local runtime topology | states "Local stack: N/A" while docs/prd.md FR-011 requires sending real emails via SMTP | correct the section to name the SMTP dependency and its local container/emulator (e.g., Mailpit) or its containerized emulator per the local-stack skill
```
