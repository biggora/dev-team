# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the
project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Note on history.** This file was introduced in 1.9.0. Every entry for 1.8.0 and earlier
> was reconstructed after the fact from the repository's commit history — the version-bump
> commits are the only record of what each release contained, and several of them say little.
> Those entries are therefore summaries of what the commits state, not complete release notes.
> The repository carries no git tags, so there are no comparison links.

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
