# Code Review Dimensions

Applied by implementation agents (backend-dev, frontend-dev, implementor,
devops-engineer, tester) as `Self-check` against their own diff before reporting, and
by `code-reviewer` as `Sweep` against the dispatched scope. Run every dimension every
time. `n/a — <reason>` is valid; skipping a dimension silently is not.

For each dimension: what to look for, and how to classify what you find under the
`review-contract` skill's three classes (`must-fix-now` blocks the gate and consumes
the rework budget; `fix-in-slice` is a real defect fixed in the same slice, no
dedicated rework round; `backlog` is recorded debt, never blocks).

## 1. Requirement conformance

Look for: the diff against the AC-IDs actually in scope for this dispatch, including
denial ACs (a `denied` permission-matrix cell is behavior to implement, not an
omission to excuse).

- `must-fix-now`: an in-scope AC is unimplemented, implemented wrong, or a denial AC
  is not enforced.
- `fix-in-slice`: an AC is partially covered but the gap does not change observable
  behavior for the tested paths.
- `backlog`: an out-of-scope AC is noticed as unaddressed.

```
RV-SLICE3-001 | must-fix-now | Critical | src/api/orders.ts:88 | AC-012 requires a 403 for ROLE-002 on DELETE /orders/:id; handler returns 200 | add the role check before the delete call and return 403 with the denial body defined in AC-012
```

## 2. Correctness and logic

Look for: null/undefined handling, boundary conditions, off-by-one errors, error
paths that swallow or mis-propagate, race conditions, resource leaks (unclosed
handles, unawaited promises, missing `finally`).

- `must-fix-now`: a defect that produces wrong output, a crash, or a leak on a
  reachable path.
- `fix-in-slice`: a defect only reachable in a documented edge case not yet covered
  by acceptance criteria.
- `backlog`: a theoretical edge case with no realistic trigger in this product.

```
RV-SLICE2-004 | must-fix-now | Critical | src/billing/invoice.ts:41 | totalCents sums an empty line-items array and returns NaN instead of 0 | guard the reduce with an initial value of 0
```

## 3. Security

Look for: authn/authz on every new route or handler, input validation at trust
boundaries, injection (SQL, command, template), secrets committed or logged, and that
denial-of-access behavior actually denies (no silent fallthrough to an authorized
path).

- `must-fix-now`: any missing authz check, injection vector, or committed secret.
- `fix-in-slice`: input validation that is present but incomplete (e.g., missing
  length bound) on a field with no external attack surface yet.
- `backlog`: a hardening suggestion beyond the current threat model (e.g., rate
  limiting not yet required by any AC).

```
RV-SLICE1-002 | must-fix-now | Critical | src/auth/login.ts:22 | password compared with === instead of a constant-time compare | use crypto.timingSafeEqual (or the project's existing bcrypt.compare) instead of ===
```

## 4. Data and persistence

Look for: query correctness, N+1 query patterns, transaction boundaries around
multi-step writes, migration reversibility, missing indexes on new query predicates.

- `must-fix-now`: a query that returns wrong rows, a missing transaction around
  writes that must be atomic, or a migration that is not reversible and ships to a
  shared environment.
- `fix-in-slice`: an N+1 pattern on a low-traffic path with no AC tied to its latency.
- `backlog`: a missing index that only matters at a scale not yet in scope.

```
RV-SLICE4-006 | must-fix-now | Critical | src/repos/orderRepo.ts:60 | order creation and inventory decrement are two separate awaits with no transaction; a failure between them leaves inventory unadjusted | wrap both writes in a single DB transaction with rollback on either failure
```

## 5. Error handling and observability

Look for: consistent error shapes across handlers, errors logged with enough context
to diagnose (not swallowed with an empty catch), failure surfaces that match the
project's established error contract.

- `must-fix-now`: an empty catch block that swallows a failure the caller needs to
  know about, or an error response shape that breaks the documented API contract.
- `fix-in-slice`: a log line missing useful context (request ID, entity ID) on a path
  that already fails loudly to the caller.
- `backlog`: a nice-to-have structured-logging improvement with no functional impact.

```
RV-SLICE2-009 | fix-in-slice | Important | src/jobs/emailWorker.ts:33 | catch block logs err.message only, drops stack trace and job ID | log the full error object plus jobId for correlation
```

## 6. Project conventions (including accessibility)

Look for: CLAUDE.md rules, naming conventions, file/directory structure, import
patterns (relative vs. alias, barrel files) actually used elsewhere in the repo, and
— for UI code — accessibility conventions already established in the project
(semantic elements, ARIA attributes, keyboard focus order, color-contrast tokens).

- `must-fix-now`: a convention breach that will propagate (e.g., a new module using
  the wrong import style that later files will copy), one CLAUDE.md marks as a hard
  rule, or a UI change that breaks an established accessibility convention (e.g., an
  interactive element that is not keyboard-reachable, a missing accessible name).
- `fix-in-slice`: a local naming inconsistency contained to one file.
- `backlog`: a stylistic preference not codified anywhere.

```
RV-SLICE1-005 | fix-in-slice | Suggestion | src/utils/formatDate.ts:1 | file uses camelCase default export where every sibling util exports a named function | rename to a named export to match src/utils/*.ts
```

## 7. Version-appropriate framework patterns

Look for: the actual installed versions in `package.json` / `pyproject.toml` /
`requirements.txt` — review against those versions, not assumptions or training-data
defaults. A pattern standard in the installed version is not an error because an
older version did it differently; a pattern deprecated in the installed version is.

- `must-fix-now`: use of an API removed or deprecated-with-warning in the installed
  version, or a pattern that breaks under that version's defaults.
- `fix-in-slice`: a working but outdated idiom the installed version has since
  superseded, with no functional difference yet.
- `backlog`: a stylistic modernization with no behavioral change.

```
RV-SLICE3-011 | must-fix-now | Critical | src/app/page.tsx:1 | uses getServerSideProps in a Next.js 15 App Router project where that API is Pages-Router-only and silently ignored | replace with an async Server Component or a route handler per the installed App Router
```

## 8. Test integrity

Look for: weakened assertions, added `skip`/`only`, deleted tests, tests that run
but assert nothing meaningful. This dimension is checked by code-reviewer whenever
test files changed as part of the diff. backend-dev, frontend-dev, implementor and
devops-engineer do not edit tests and self-check this dimension only if they
mistakenly touched one; the **tester** self-checks this dimension against its entire
diff, every time.

- `must-fix-now`: any weakened assertion, `skip`/`only` left in, a deleted test, or a
  test that passes vacuously — an implementation agent making a red test green by
  editing the test is always Critical.
- `fix-in-slice`: n/a — this dimension has no fix-in-slice tier; a test-integrity
  violation always blocks.
- `backlog`: n/a — same reasoning.

```
RV-SLICE2-013 | must-fix-now | Critical | tests/auth.spec.ts:44 | assertion changed from expect(res.status).toBe(403) to expect(res.status).toBeDefined() | restore the original 403 assertion; fix the handler instead of the test
```

## 9. Docs-code sync

Look for: contradictions between the change and `docs/prd.md`, `docs/design.md`,
`docs/plan.md`, `docs/use-cases.md` — a code change that alters requirements, design,
or plan without updating the owning document.

- `must-fix-now`: the change contradicts a documented AC or use case and the owning
  document was not updated in the same slice.
- `fix-in-slice`: a minor doc lag (e.g., an example snippet in the doc now stale) that
  does not misdirect the next agent.
- `backlog`: a documentation nicety unrelated to the change's correctness.

```
RV-SLICE3-015 | must-fix-now | Critical | src/api/orders.ts:5 | endpoint now returns 201 with a location header, but docs/prd.md AC-018 still specifies 200 with no header | update AC-018 in docs/prd.md in this same slice, or revert the response shape to match it
```

## 10. Infrastructure contract

Only when infrastructure files changed (`docker-compose*.yml`, `Dockerfile*`,
`.env.example`, seed/reset scripts) — otherwise mark `n/a — no infrastructure files
touched`. Check every image carries an explicit pinned tag, every service declares a
health check with dependents waiting on `condition: service_healthy`, volumes are
named and removed by `down -v`, host ports are deterministic with a documented
override, no production or real third-party credentials appear, `.env.example` lists
every variable read, and up/reset are idempotent.

- `must-fix-now`: `latest` or an untagged image, a missing health check, or a
  committed real credential — all Critical because they make downstream "green
  locally" claims unreproducible or leak secrets.
- `fix-in-slice`: `.env.example` missing a comment on a variable that is otherwise
  present and correct.
- `backlog`: a port choice that works but is undocumented as configurable.

```
RV-INFRA-002 | must-fix-now | Critical | docker-compose.yml:14 | postgres image pinned to `latest` | pin to `postgres:16-alpine` (or the version the app was developed against)
```

## 11. Dead code, duplication, and over-engineering

Look for: code left over from a prior approach, logic duplicated across files that
should share one implementation, and abstractions built beyond what the current spec
needs (speculative configuration, unused extension points, generic solutions for a
single-use case). Over-engineering is a defect here, not a virtue — flag it against
the spec, do not propose further enhancements.

- `must-fix-now`: dead code that will confuse or be invoked accidentally (an
  unreachable branch that still runs on a code path with side effects).
- `fix-in-slice`: real duplication between two files that should share one function,
  with no functional risk today.
- `backlog`: a speculative abstraction that works but was not asked for.

```
RV-SLICE1-009 | fix-in-slice | Important | src/services/{userService.ts,adminService.ts} | both files implement an identical 20-line email-normalization block | extract to src/utils/normalizeEmail.ts and import from both
```
