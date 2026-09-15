---
name: review-contract
description: >
  This skill should be used when an agent is about to review code, review a document,
  sweep an artifact for findings, recheck a previously reviewed artifact, or self-check
  its own change before reporting. Trigger phrases include "review", "code review",
  "document review", "sweep", "findings", "rework", "self-check before reporting",
  "RV-ID", "must-fix-now", "fix-in-slice", "backlog", "late finding", "review
  completeness", "recheck", "disposition", "carry findings forward", and "Context /
  Self-check / Sweep report fields". Applies to code-reviewer and doc-reviewer running
  a Sweep, to backend-dev, frontend-dev, implementor, devops-engineer, and tester
  running a Self-check before reporting, and to the coordinator classifying findings
  or sizing a rework dispatch.
---

# Review Contract

## Overview

This contract exists to stop the pipeline from burning cycles on two failure modes:
agents skimming required reading instead of using it, and reviewers delivering
findings in batches across successive reworks instead of exhaustively in one pass.
It defines three report fields, a finding schema, a late-finding rule that caps how
many rework cycles a review can generate, and a disposition protocol for rework
reports. Read a dimension list in `references/` only when you are about to apply it —
do not summarize it into your own output.

## Who applies this contract and when

- **Implementation agents** (backend-dev, frontend-dev, implementor, devops-engineer,
  tester) apply the code dimensions from `references/code-dimensions.md` to their OWN
  diff before reporting, as `Self-check`. Fix what you find; report what you fixed.
- **code-reviewer** applies the code dimensions from `references/code-dimensions.md`
  to the assigned scope as `Sweep`.
- **doc-reviewer** applies the document dimensions from `references/doc-dimensions.md`
  to the assigned scope as `Sweep`.
- **The coordinator** applies the finding schema, the late-finding rule, and the
  disposition discipline (below) when classifying findings and sizing rework budgets.
- **adversarial-reviewer keeps its own `CH-*` debate protocol.** It is NOT governed by
  the RV-ID schema, the late-finding rule, or the disposition discipline in this
  contract — those apply only to ordinary code/doc review and rework cycles.

## Report fields

Three report fields are defined by this contract. Carry the ones that apply to your
role; do not invent new field names for the same purpose.

### `Context:` — every agent

List every source your dispatch's "Required reading" block named, one line each:

```
Context:
docs/prd.md → AC-014, AC-015, denial AC-009
docs/architecture.md → "Session storage" section
src/auth/session.ts:12-40 → existing guard pattern reused
```

The only permitted empty value is `none required — dispatch listed no required
reading`. Do not write `Context: read the PRD` — name the exact sections, AC-IDs, or
file:line taken from each source.

### `Self-check:` — implementation agents

Run every code dimension (`references/code-dimensions.md`) against your diff;
state count run, then only what you fixed and what was `n/a` — clean
dimensions are covered by the count:

```
Self-check: ran all 11 code dimensions against my diff.
Fixed before reporting: missing null check on session.user (correctness); unvalidated slug param (security).
n/a: infrastructure contract (no infrastructure files touched).
```

Nothing to fix: `Self-check: ran all 11 code dimensions against my diff. Fixed
before reporting: none.`

### `Sweep:` — code-reviewer and doc-reviewer

One line per dimension of the applicable dimension list (code or document), in order:

```
Sweep:
1. Requirement conformance → checked, 1 finding
2. Correctness and logic → checked, clean
...
9. Docs-code sync → n/a — no docs/ changes in this scope
```

Omitting a dimension from `Sweep` is forbidden. If you did not check it, write
`n/a — <reason>`, never silence.

### Three new report rules

- **Context required for DONE.** If the dispatch listed Required reading and your
  `Context` field does not account for every listed source, you may not report DONE.
- **Sweep must be complete.** Every dimension gets a verdict. If the scope is too
  large to sweep in one pass, report BLOCKED with a proposed split — never deliver a
  partial review and call it DONE.
- **Self-check before report.** Run the code dimensions against your own diff first
  and fix what you find; report what you fixed, not what you plan to fix later.

## Finding schema

Ordinary code and document reviews report findings in exactly this grammar — it
replaces free-form findings entirely:

```
RV-<scope>-NNN | <class> | <severity> | <file:line or doc§section> | <issue> | <required fix>
```

- `<scope>` is a slice or artifact tag: `RV-SLICE2-003`, `RV-PRD-001`, `RV-INFRA-002`.
- `NNN` is a stable, monotonically assigned number. **IDs are stable across reworks:
  never renumber, never reuse.**
- `<class>` is exactly one of `must-fix-now`, `fix-in-slice`, `backlog`.
- `<severity>` is exactly one of `Critical`, `Important`, `Suggestion`.
- Report a finding at all only above the confidence threshold in
  `references/finding-schema.md` (**>= 75**).

Full grammar (including the multi-line locator variant for findings that span more
than one file), the confidence rubric, worked examples across all three classes, and
a worked recheck showing both late-finding exceptions are in
`references/finding-schema.md`. Read it before writing your first finding.

### Class semantics — this is what gates the pipeline

- **`must-fix-now`** — blocks the gate. Correctness, security, a requirement
  violation, or a convention breach that will propagate into later work. **Only this
  class triggers a rework dispatch, and only this class consumes the rework budget.**
- **`fix-in-slice`** — a real defect that does not block. Record it in the ledger;
  the same agent fixes it inside the same slice, at its next scheduled dispatch. It
  never causes a dedicated rework round. **Closure:** before slice N's
  Definition-of-Done gate passes, every open `fix-in-slice` finding for that slice is
  either fixed or explicitly re-classed `backlog` with a recorded reason — never
  dropped silently. In a final or cross-cutting review with no further slices (a
  Phase 4 review, or a review of a completed change set), `fix-in-slice` means "fix
  before the task is reported complete."
- **`backlog`** — recorded as technical debt. Never blocks, never causes a dispatch.
  **Destination:** the `### Technical debt` section of `docs/progress.md`; where no
  ledger exists (the Micro profile), report it in the coordinator's final report.

Misclassification is itself a defect. Inflating a cosmetic issue to `must-fix-now`
wastes a full rework cycle; downgrading a real correctness defect to `backlog` ships
a bug. Classify by consequence, not by how easy the fix looks.

### Profile interaction

Under the Micro profile (no slices, no `docs/progress.md`), a review emits only
`must-fix-now` and `backlog` — `fix-in-slice` has no referent because no slice
exists. Use scope tag `MICRO` (e.g. `RV-MICRO-001`). `backlog` rows go into the
coordinator's final report, per the destination rule above.

## Late-finding rule — the cycle cap

This is the most important rule in the contract; it is what stops findings from
dripping out one rework at a time.

On any recheck of an artifact you have already reviewed:

1. **Carry every prior RV-ID forward** with a state: `resolved`,
   `rejected_with_evidence`, `open`, or `reclassified → <new class>`. Never drop a
   prior ID silently.
2. Raise a **NEW** `must-fix-now` finding only if (a) the rework itself introduced
   it, or (b) it is a Critical correctness or security defect the rework did not
   introduce.
3. A new `must-fix-now` on a recheck **must** carry exactly one rationale line:
   `Introduced by: <the rework change that created it>` under (a), or
   `Pre-existing Critical: <the reachable impact, plus a statement that the rework
   did not introduce it>` under (b). A new `must-fix-now` carrying neither line is
   invalid — file it as `backlog` instead.
4. **Everything else you notice for the first time on a recheck is `backlog`.** It
   does not block the gate and does not consume the rework budget.
5. **Reclassifying a prior finding** (e.g., a `backlog` that should have been
   `must-fix-now`) follows the same rationale discipline as step 3 when upgrading to
   `must-fix-now`; a downgrade never returns rework budget already consumed.

Rationale: an issue that existed in cycle 1 and sat inside your reviewed scope was
YOUR miss, not a new problem introduced by the creator. The cost of a reviewer's miss
is one backlog row — not another rework cycle charged to the creator. See
`references/finding-schema.md` for a worked recheck (carried-forward IDs plus one
legitimately new `must-fix-now` under each exception) and a worked example of an
ILLEGAL late finding.

## Disposition discipline

When an agent is re-dispatched with findings, it answers with **exactly one**
disposition per RV-ID: `accepted_and_fixed`, `rejected_with_evidence`, or
`needs_decision`.

- `rejected_with_evidence` requires a citation (file:line, doc section, or test
  output) — a bare rejection is not a disposition.
- A rework report that omits a disposition for any `must-fix-now` ID is
  `DONE_WITH_CONCERNS`, not `DONE`.

## Dimensions

<!-- SYNC: dimension names and order below must be kept in step with
     agents/code-reviewer.md and agents/doc-reviewer.md. This skill file is
     authoritative — if the two ever drift, the agent prompts are wrong. -->

Apply the full dimension list every time you run a Self-check or a Sweep — do not
cherry-pick. Names only here; look-fors, class guidance per dimension, and one worked
finding line each live in the reference files.

**Code dimensions** (`references/code-dimensions.md`, applied by implementation
agents as Self-check and by code-reviewer as Sweep):
1. Requirement conformance
2. Correctness and logic
3. Security
4. Data and persistence
5. Error handling and observability
6. Project conventions (including accessibility for UI code)
7. Version-appropriate framework patterns
8. Test integrity
9. Docs-code sync
10. Infrastructure contract
11. Dead code, duplication, and over-engineering

**Document dimensions** (`references/doc-dimensions.md`, applied by doc-reviewer as
Sweep):
1. Completeness
2. Internal consistency
3. Cross-document consistency
4. Actionability
5. Traceability
6. Source discipline
7. Type-specific checklist
8. Technical accuracy
9. Local-stack and readiness clauses

The type-specific checklist (dimension 7) is the per-document-type checklist owned
by `agents/doc-reviewer.md` (PRD, architecture, design, plan) — apply it from there;
this skill does not duplicate it.

## Additional Resources

- **`references/code-dimensions.md`** — all 11 code dimensions: what to look for,
  must-fix-now vs fix-in-slice vs backlog per dimension, one worked RV-ID example each.
- **`references/doc-dimensions.md`** — all 9 document dimensions, same treatment.
- **`references/finding-schema.md`** — full grammar, the multi-line locator variant,
  the confidence rubric, worked examples across classes, a worked recheck with
  carried-forward states, and a worked ILLEGAL late finding.
