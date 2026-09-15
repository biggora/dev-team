# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the
project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Note on history.** This file was introduced in 1.9.0. Every entry for 1.8.0 and earlier
> was reconstructed after the fact from the repository's commit history — the version-bump
> commits are the only record of what each release contained, and several of them say little.
> Those entries are therefore summaries of what the commits state, not complete release notes.
> The repository carries no git tags, so there are no comparison links.

## [2.0.0] - 2026-09-15

### Breaking

- **Every agent's structured report gained required fields.** All 12 agents now carry a
  `Context:` field (immediately after `Files changed:`) listing every source their dispatch's
  `Required reading` block named, one line each as `<path> → <what was taken from it>`. A
  `DONE` report that omits `Context:` when the dispatch listed Required reading is no longer
  valid — the coordinator's new Context gate treats it as `DONE_WITH_CONCERNS` and
  re-dispatches. The five implementation agents (`backend-dev`, `frontend-dev`,
  `implementor`, `devops-engineer`, `tester`) additionally carry `Self-check:` after
  `Evidence:`; `code-reviewer` and `doc-reviewer` additionally carry `Sweep:` after
  `Evidence:`, and omitting a sweep dimension is forbidden. The canonical block in
  `templates/agent-template.md` reflects this; any external tooling or dashboard that parses
  agent reports by fixed field order must account for the new fields.
- **Coordinator dispatch prompts must now name a `Required reading` block.** Writing "read
  the documentation" is no longer sufficient — agents do not read documents the coordinator
  did not name, and a path without an extraction instruction is read superficially. This
  obligation governs every dispatch prompt the three coordinator skills construct — the
  Phase 2 dispatch-prompt checklist, the per-agent reviewer dispatches under `### Inter-agent
  context passing`, PRD/plan debate dispatches, and the Phase 4 cross-cutting review
  dispatches alike.

### Upgrading

Agent prompts and skills load at session start, not on file edit — an installed plugin keeps
running the version it loaded until refreshed, and editing a checkout does not update an
installed plugin or a running session (see Installation in `README.md`). Reinstall or update
the plugin for your platform and start a new session before the `Context:`, `Self-check:`, and
`Sweep:` report fields and the Context gate take effect. Until then, a session still running
the 1.9.0-loaded agent prompts will keep emitting reports without the new fields while a
2.0.0-loaded coordinator enforces the gate against them — re-dispatching them repeatedly for a
field they were never told to produce.

### Added

- **`skills/review-contract/`** — new locally-authored skill (not vendored; no
  `skills-lock.json` entry) that is the single source of truth for the three report fields
  (`Context`, `Self-check`, `Sweep`), the `RV-<scope>-NNN` finding schema, the three finding
  classes, the late-finding rule, and the disposition protocol. `SKILL.md` plus
  `references/code-dimensions.md` (11 dimensions), `references/doc-dimensions.md` (9
  dimensions), and `references/finding-schema.md` (grammar, worked examples, a worked
  recheck).
- **Ordinary review contract.** Findings from `code-reviewer` and `doc-reviewer` carry stable
  `RV-<scope>-NNN` IDs, never renumbered or reused, each classed exactly one of:
  `must-fix-now` (blocks the gate — the only class that triggers a rework dispatch and
  consumes the rework budget), `fix-in-slice` (a real but non-blocking defect, fixed by that
  agent's next scheduled dispatch in the same slice, never a dedicated rework round), or
  `backlog` (debt, recorded, never blocks). The rework budget stays 2 rounds per artifact per
  gate but is now counted on open `must-fix-now` findings instead of on dispatches.
- **Late-finding rule.** On a recheck, the reviewer carries every prior `RV-ID` forward with a
  state (`resolved`, `rejected_with_evidence`, `open`) and may raise a new `must-fix-now`
  finding only when the rework itself introduced it (with a rationale line naming the change)
  or when it is a Critical correctness or security defect. Anything else noticed for the
  first time on a recheck is filed as `backlog` — this is the cycle cap that stops reviewers
  from delivering findings in batches across successive reworks. `adversarial-reviewer` keeps
  its own `CH-*` debate protocol and budget, explicitly unchanged and separate from `RV-*`.
- **Rework packet.** A creator re-dispatched with review findings answers with exactly one
  disposition per `RV-ID` — `accepted_and_fixed`, `rejected_with_evidence` (cited), or
  `needs_decision`. A rework report missing a disposition for any `must-fix-now` ID is
  `DONE_WITH_CONCERNS`, not `DONE`.
- **Document-agent inventory (Process Step 0).** `product-analyst`, `architect`, `planner`,
  and `ui-ux-designer` now run `Glob('docs/**/*.md')` and read every document it returns
  before producing new content; an existing normative document is binding and a conflict with
  it is named in `Concerns` with the owning document and affected IDs, never silently
  overridden. `agents/architect.md`, which previously never mentioned the PRD in its process
  at all, now derives requirements from `docs/prd.md` AC-IDs in both its greenfield and
  existing-project variants, and requires every AC-ID to be addressable by a component.
- **Context gate (coordinator Phase 3).** A report whose `Context:` field does not account for
  every source listed in that dispatch's `Required reading` is treated as `DONE_WITH_CONCERNS`
  and re-dispatched naming the unaccounted sources.
- Progress ledger (`docs/progress.md`) task table gained two columns: open `RV-` IDs with
  their class, and the attempt count per scope+role. No new table or section was added.

### Changed

- **Coordinator size.** Despite all of the above, the three coordinator skills absorbed the
  new contract without growing materially, because the five near-identical per-agent "dispatch
  code-reviewer for X" briefs under `### Inter-agent context passing` collapsed into one rule
  that delegates to the `review-contract` skill's rubric. The design constraint: added process
  must displace existing process.
- `## Review and Debate Limits` in all three coordinator skills now describes the ordinary
  review contract (`RV-` IDs, classes, late-finding rule, rework packet) in place of the old
  undifferentiated "2 creator-rework + reviewer-recheck dispatches" budget description; the
  numeric budget itself (2 rounds per artifact per gate) is unchanged, only what it counts.
- Every dispatch this skill constructs — the Phase 2 dispatch-prompt checklist, the per-agent
  reviewer dispatches under `### Inter-agent context passing`, debate dispatches, and the
  Phase 4 cross-cutting review dispatches — gained a **Required reading** line; Phase 3 gained
  a **Context gate** step (3b).
- `backend-dev`, `frontend-dev`, `implementor`, `devops-engineer`, and `tester` gained a
  **Self-check before reporting** process step, applying the `review-contract` skill's code
  dimensions to their own diff before writing their report.
- `code-reviewer` and `doc-reviewer` gained a **Review Completeness** section (the sweep
  dimensions), a **Finding Schema** section, and a **Late-Finding Rule** section, replacing
  their previous free-form "Output Format" section; `code-reviewer`'s status list gained
  `BLOCKED` for an oversized scope.
- `planner` and `product-analyst` gained the same Process Step 0 document inventory as
  `architect` and `ui-ux-designer`.

## [1.9.0] - 2026-09-05

### Breaking

- **CI/CD ownership moved from `implementor` to the new `devops-engineer` agent.**
  Use `/ask-devops` instead of `/ask-implementor` for CI pipelines, deployment configs and
  images, and publish/release work. The same applies to local infrastructure files —
  `docker-compose*.yml`, `Dockerfile*`, `.env.example`, `.dockerignore`, and seed/reset
  scripts — which are now `devops-engineer`'s exclusive writable scope; no other agent may
  edit them in any dispatch, parallel or not.
- `/ask-implementor` no longer accepts CI/CD or infrastructure work: it detects the request
  and redirects the user to `/ask-devops`. If such a task still reaches `implementor`, the
  agent reports `NEEDS_CONTEXT` naming `devops-engineer` rather than doing the work. Reading
  infrastructure files to understand how to run a project remains expected; editing them
  does not.
- Coordinators no longer dispatch CI/CD to `implementor`, and an execution plan that assigns
  CI/CD work to any agent other than `devops-engineer` is invalid.

### Added

- **Local-stack gate.** A project's external runtime dependencies — database, cache, message
  broker or queue, SMTP, object storage, search engine, identity provider, third-party HTTP
  API — must run locally in version-pinned containers with health checks before slice 1
  starts and for every verification afterwards. Evidence produced against a mock, stub, fake,
  or in-memory substitute for a dependency that has a container equivalent is not local
  evidence. A dependency with no runnable local service gets a containerized emulator
  (`stripe-mock`, `localstack`, `wiremock`, `mailpit`); where no emulator exists the
  coordinator halts for one batched user question and the affected AC stays `UNVERIFIED`
  until an explicit waiver is recorded. A project with genuinely no external dependencies
  records `Local stack: N/A — <reason>`. The gate is profile-independent — Micro does not
  exempt a task from it — and where a compose file already covers the whole inventory it is
  satisfied by evidence rather than by a dispatch.
- `agents/devops-engineer.md` — new specialist (sonnet, yellow; Read, Write, Edit, Grep,
  Glob, Bash) owning the local containerized stack, seed/reset, emulators, and CI/CD after
  the local-proof gate. The plugin now exposes 12 agents.
- `skills/local-stack/` — new skill with `SKILL.md` and six references: `datastores.md`,
  `messaging.md`, `cloud-emulators.md`, `service-emulators.md`, `seed-and-reset.md`,
  `test-integration.md`.
- `skills/ask-devops/` — new `/ask-devops` shortcut dispatching `devops-engineer`.
- Coordinator pipeline steps: Phase 0 step `2b. External-dependency scan`; Phase 1 action
  `4b. Infrastructure inventory`; greenfield step 4, local stack enablement, which must
  report DONE (or be recorded `N/A`) before any scaffolding or slice starts; Phase 2 action 5
  rewritten as an ordered (a)–(d) local-proof gate.
- Progress ledger (`docs/progress.md`) gained two sections: **Infrastructure inventory**
  (dependency → pinned image or emulator → health check → discovery env var → AC-IDs and
  suites) and **Local stack proof** (the last clean-state verification).
- `architect` now emits a **Local runtime topology** section naming, per dependency, the
  container image and pinned tag or emulator, the discovery env var, and the health check.
- `product-analyst` records a **local-verification route** for every external integration, or
  `no local equivalent — user decision required`.
- `code-reviewer` gained review step 6b for infrastructure files — unpinned images and
  missing health checks are Critical findings; `doc-reviewer` gained matching PRD,
  architecture, and plan checklist items.
- `specs/workflow.md` gained a `## Gates` section tabulating the four gates (local-stack,
  DoD, criteria coverage, local-proof) and updated Mermaid diagrams covering the local stack
  enablement subgraph and `devops-engineer`.
- Eval coverage: fixtures `evals/fixtures/containerized-project/` and
  `evals/fixtures/no-deps-library/`, plus coordinator-dispatch cases CD-009 (greenfield
  ordering with the local-stack gate and CI/CD last) and CD-010 (negative case: a premature
  pipeline request must halt).
- `keywords` entries `devops` and `docker` in the three plugin manifests and `package.json`.

### Changed

- `tester`: an acceptance test for an AC that names an external dependency is written against
  the container or emulator from the start (Mode A). Mode B brings the stack up
  (`docker compose up -d --wait`), confirms every service healthy, and runs unit,
  integration, and e2e suites against it; Evidence must include the `docker compose ps`
  output from the same session. Substituting a mock, stub, fake, or in-memory double for a
  containerized dependency is now a test-integrity violation of the same class as weakening
  an assertion. Report rules gained scope-aware red.
- `backend-dev` runs against the real local stack through the documented env vars and may not
  edit infrastructure files. `frontend-dev` verifies user flows against the running backend;
  a fixture- or MSW-backed run no longer substitutes, and affected criteria are marked
  `UNVERIFIED`.
- `planner`: a project with external runtime dependencies opens its plan with a single
  infrastructure-enablement task assigned to `devops-engineer`, scheduled before the tracer
  bullet and before shared scaffolding; slices list the local-stack services they exercise.
- `skills/dev-team-codex/SKILL.md` gained the CI/CD-last rule, which it was missing entirely,
  alongside the local-stack gate, the `/ask-devops` mapping, and the `local-stack` skill
  reference.
- `/handoff` and `/resume` carry local-stack state; `/resume` re-verifies the stack
  (`docker compose ps`, bringing it up if down) before resuming any slice or verification.

### Fixed

- `nodejs-stack` and `python-stack` advertised six `references/` files that never existed
  (`nextjs-patterns.md`, `nestjs-patterns.md`, `django-patterns.md`, `flask-patterns.md`, and
  `testing-patterns.md` in both skills). Both now point at the `architecture-patterns.md`
  that is actually present, plus the `local-stack` skill.
- `nodejs-stack`'s blanket "Mock external dependencies" testing guidance was correct only for
  unit tests; it now separates unit-level mocking of internal collaborators from integration
  and e2e runs against containers. `python-stack` received the equivalent correction.
- `python-stack/references/architecture-patterns.md` now names the container from
  `docker-compose.yml` as the "real database" its testing strategy assumes, and adds per-test
  isolation guidance.
- `package-lock.json` had drifted to 1.5.0 while `package.json` read 1.8.0; both now read
  1.9.0.

## [1.8.0] - 2026-07-24

### Changed

- Scope-proportional evidence, proportional adversarial debate, and session continuity, per
  the bump commit `a16ceea`.

## [1.7.0] - 2026-07-15

### Changed

- The "CI/CD last" principle enforced across the documentation and skills (`0c272f1`).

## [1.6.0] - 2026-07-14

### Added

- Pipeline profiles with a Phase 0 triage, for leaner task orchestration (`6511a18`).

## [1.5.0] - 2026-07-14

### Added

- Structured-workflow improvements: input traceability, open-question gating, and docs-code
  sync (`c1dbd7e`).

## [1.4.0] - 2026-07-11

### Changed

- Version bump only. The commit (`9357d6b`, "chore: bump plugin version to 1.4.0") touches
  nothing but the manifests and records no description of the release. The work merged
  alongside it on branch `feat/plugin-version-1.4.0` (`247f070`) included the adversarial
  review gates for PRDs and plans (`04a4591`), but the bump commit itself does not say so.

## [1.3.0] - 2026-07-10

### Added

- The `autoresearch` and `design-styles` skills wired into orchestration (`6c0f067`).

## [1.2.0] - 2026-07-10

### Changed

- Agent and skill templates refactored; paths and documentation made consistent (`bba7949`,
  which carries the bump for `package.json` and `.claude-plugin/plugin.json`). A follow-up
  commit the same day (`6c44015`) propagated 1.2.0 to the Copilot manifests and describes no
  functional change of its own.

## [1.1.0] - 2026-07-10

### Removed

- Deprecated mobile-testing scripts (`analyze_apk.py`, `check_environment.py`) and stale
  references (`codex-tools.md`, `copilot-tools.md`, `DESIGN.md`, `frame-template.html`),
  as repository cleanup (`723e780`, which also carries the bump).

## [1.0.1] - 2026-05-17

### Changed

- Version bump plus keyword formatting made consistent across the marketplace and plugin
  manifests (`33028ea`).

## [1.0.0] - 2026-04-13

### Added

- Initial dev-team plugin: README, plugin manifest, `package.json`, agent workflow,
  architecture outline, and skill templates (`76723ff`). No commit records a 1.0.0 bump; the
  version was the initial value in the manifests.
