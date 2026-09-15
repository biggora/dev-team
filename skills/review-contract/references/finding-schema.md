# Finding Schema

The grammar, worked examples, and the late-finding recheck protocol referenced from
`SKILL.md`. This replaces free-form findings in ordinary code and document reviews.
`adversarial-reviewer`'s `CH-*` debate protocol is separate and not governed by this
file.

## Grammar

```
RV-<scope>-NNN | <class> | <severity> | <file:line or doc§section> | <issue> | <required fix>
```

| Field | Rule |
|---|---|
| `RV-<scope>-NNN` | `<scope>` is a slice or artifact tag (`SLICE2`, `PRD`, `PLAN`, `ARCH`, `INFRA`, ...). `NNN` is a stable three-digit number, monotonically assigned, never renumbered, never reused — even after the finding is resolved. |
| `<class>` | Exactly one of `must-fix-now`, `fix-in-slice`, `backlog`. |
| `<severity>` | Exactly one of `Critical`, `Important`, `Suggestion`. |
| `<file:line or doc§section>` | A precise locator — `src/auth/session.ts:41` for code, `docs/prd.md §AC-014` for documents. Never a bare filename with no line or section. |
| `<issue>` | One sentence stating what is wrong, not what is missing in general. |
| `<required fix>` | One sentence stating the concrete fix — specific enough that the creator does not have to guess. |

## Multi-line locator variant

The single-line form above is the default. When a finding genuinely spans more than
one file — or needs a corroborating citation to be actionable — set the locator field
to `multi` and list each reference on its own indented line directly under the
finding:

```
RV-PLAN-003 | must-fix-now | Critical | multi | docs/plan.md Slice 4 depends on a Notification Service with no owning component in docs/architecture.md, though docs/prd.md FR-019 requires it | add the Notification Service to docs/architecture.md, or remove the FR-019 dependency from Slice 4
  docs/plan.md §Slice 4
  docs/architecture.md §Components (Notification Service absent)
  docs/prd.md §FR-019
```

Use `multi` only when a single locator would misrepresent the finding's scope — do
not use it to bundle unrelated findings together.

## Confidence scoring

Score every candidate finding before deciding whether to report it:

| Score | Meaning |
|---|---|
| 0 | False positive or pre-existing issue |
| 25 | Might be real, might be false positive |
| 50 | Real issue but minor, not impactful |
| 75 | Verified real issue, will impact functionality |
| 100 | Confirmed critical issue, will happen frequently |

**Report a finding at all only when its score is >= 75.** Below that threshold, do
not report it — do not hedge it in as a `Suggestion` to appear thorough.

## Worked examples across classes

```
RV-SLICE2-003 | must-fix-now | Critical | src/auth/session.ts:41 | session guard returns early before checking token expiry, allowing expired sessions through | move the expiry check above the early return, before any authorized branch executes

RV-SLICE2-004 | must-fix-now | Important | src/api/users.ts:19 | missing input validation on `email` field allows empty string to reach the DB unique constraint, surfacing a raw SQL error to the client | validate non-empty and shape with the project's existing zod schema before the repo call

RV-SLICE2-005 | fix-in-slice | Important | src/services/pricing.ts:77 | discount calculation duplicates the rounding logic already in src/utils/money.ts | replace with a call to utils/money.ts:roundToCents in this slice's next scheduled dispatch

RV-SLICE2-006 | fix-in-slice | Suggestion | src/components/Cart.tsx:5 | prop destructuring order does not match the project's alphabetical convention seen elsewhere | reorder props alphabetically next time this file is touched

RV-SLICE2-007 | backlog | Suggestion | src/utils/date.ts:12 | date formatting helper could accept a locale parameter for future i18n | record as backlog; no AC currently requires localization

RV-PRD-001 | backlog | Important | docs/prd.md §NFR-002 | non-functional target for concurrent users is stated as "high" rather than a number, but no AC currently depends on the exact figure | record as backlog until a slice introduces a load-related AC
```

## Worked recheck: carried-forward IDs plus one new `must-fix-now` under each exception

Cycle 1 produced `RV-SLICE2-003` (above) and `RV-SLICE2-004` (above), both
`must-fix-now`. The creator was re-dispatched, fixed both, and reported:

```
RV-SLICE2-003 | accepted_and_fixed
RV-SLICE2-004 | accepted_and_fixed
```

On the cycle-2 recheck, the reviewer re-examines the same scope. The correct report
carries every prior ID forward with a state, then evaluates only what changed:

```
Sweep (recheck):
RV-SLICE2-003 | resolved | expiry check now runs before the authorized branch (session.ts:39-44)
RV-SLICE2-004 | resolved | zod schema validates non-empty email before the repo call (users.ts:15-21)

RV-SLICE2-008 | must-fix-now | Critical | src/api/users.ts:22 | the new zod validation throws a raw ZodError that leaks the schema's internal field names to the API client instead of the project's standard 400 error envelope | catch the ZodError and map it to the existing errorEnvelope() helper before returning 400
Introduced by: the RV-SLICE2-004 fix added zod validation but did not wrap its thrown error in the project's error envelope.

RV-SLICE2-011 | must-fix-now | Critical | src/api/users.ts:52 | raw string concatenation builds the SQL WHERE clause from the unvalidated `sort` query param, allowing SQL injection | replace with a parameterized query or the project's query builder's safe sort whitelist
Pre-existing Critical: reachable by any authenticated user hitting GET /users?sort=..., not introduced by the RV-SLICE2-004 rework — this line is untouched by that fix and has been present since cycle 1.
```

`RV-SLICE2-008` is legitimate under exception (a): it is `must-fix-now`, and the
`Introduced by:` line names exactly which prior fix introduced it (the
`RV-SLICE2-004` fix). `RV-SLICE2-011` is legitimate under exception (b): it is a
Critical security defect, and the `Pre-existing Critical:` line states its reachable
impact and confirms the rework did not introduce it — so the reviewer does not have
to fabricate an `Introduced by:` line it cannot truthfully write, and does not have
to downgrade a live SQL-injection vulnerability to `backlog`. Either finding without
its matching rationale line would be invalid and must be filed as `backlog` instead.

Anything the reviewer notices for the first time on this recheck that was already
present in cycle 1's reviewed scope, is NOT something the rework introduced, and is
not a Critical correctness or security defect, goes to `backlog`, for example:

```
RV-SLICE2-009 | backlog | Suggestion | src/api/users.ts:8 | the handler still uses `var` in one spot instead of `const`, present since cycle 1 | record as backlog; not introduced by this rework and not blocking
```

## Worked ILLEGAL late finding — and why it is illegal

Same recheck, same scope. Suppose the reviewer instead writes:

```
RV-SLICE2-010 | must-fix-now | Important | src/api/users.ts:30 | the handler does not log a warning when validation fails | add a warning-level log line on validation failure
```

This is **illegal**. Reasons:

1. This code at `users.ts:30` existed unchanged since cycle 1 and was inside the
   reviewer's reviewed scope in cycle 1 — the reviewer simply missed it then. It was
   not introduced by the `RV-SLICE2-004` rework, so exception (a) does not apply and
   no `Introduced by:` line can be truthfully written.
2. Its severity is `Important`, not Critical, so exception (b) does not apply either
   — a `Pre-existing Critical:` line would misstate its severity, not supply a
   missing rationale. There is no legal rationale line of either form to attach.

Because neither exception in the late-finding rule applies, `RV-SLICE2-010` must be
filed as `backlog`, not `must-fix-now`. Filing it as `must-fix-now` would trigger a
third rework cycle for a gap that was the reviewer's own miss in cycle 1 — exactly
the cost this contract exists to prevent. The correct report is:

```
RV-SLICE2-010 | backlog | Suggestion | src/api/users.ts:30 | handler does not log a warning when validation fails; present since cycle 1, not introduced by this rework | record as backlog
```
