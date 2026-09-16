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

## Codex compatibility correction — 2026-09-05

This section tracks the user-approved Codex adapter correction independently of the historical work above.

- Goal: fix Codex execution, routing, installation guidance, and checks without changing Claude workflows.
- Profile: Standard; score 5 (size 2, novelty 1, clarity 0, reversibility 0, parallelizability 2). The approved user plan is authoritative; no new PRD or debate is needed.
- Baseline: clean working tree at `13f7469a171505f4a4a378d1f56356f487c212ee`; an immutable comparison copy was archived outside the repository before edits.
- Local stack: N/A — this plugin contains instructions and offline contract checks; live client verification uses disposable projects without application service dependencies.
- Run counter: 7/8 (tester Mode A; documentation specialist; adapter implementor; independent code reviewer; independent document reviewer; tester Mode B; document recheck). Live client scenarios are verification processes, recorded separately from implementation/review dispatches.

| Criterion | Required outcome | Status |
|---|---|---|
| CX-001 | Codex uses advertised tool schemas, isolated initial dispatch, bounded lifecycle and honest blocking | PASS static; live delegation UNVERIFIED |
| CX-002 | All entrypoints route once; installed-package paths and invocation policies work | PASS static and isolated package installation; live execution BLOCKED |
| CX-003 | Shared workflow bodies and Claude contracts remain intact; adapter consumes canonical rules | PASS exact preservation and live reviewer/Micro comparisons; PRD completion UNVERIFIED |
| CX-004 | Separate Codex checks pass; existing static suites show no new failures | PASS: Codex 11/11, Tier 1 26/26, AP static 22/22 |
| CX-005 | Live Codex and before/after Claude scenarios have actual execution evidence | PARTIAL: reviewer/Micro comparisons PASS; Codex execution BLOCKED and PRD completion UNVERIFIED |
| CX-006 | Independent code and document review passes | PASS: independent code review and document recheck |

| Task | Agent | Status | Evidence |
|---|---|---|---|
| Contract checks, Mode A | tester | DONE_WITH_CONCERNS | node --test evals/codex/contracts.test.cjs: 4 pass, 7 expected red, 0 skipped; historical defects reproduced before implementation |
| Codex installation documentation | documentation specialist | DONE | README-only diff; all other platform sections preserved against baseline |
| Adapter and conditional entries | implementor | DONE | npm run test:codex: 11/11 PASS; shared baseline preservation checks green |
| Independent code review | code-reviewer | DONE | 11/11 checks pass; all 33 preservation hashes match baseline; no actionable defects |
| Independent document review | doc-reviewer | DONE | recheck confirms corrected historical red status and separate static/live evidence; no remaining findings |
| Contract checks, Mode B | tester | DONE | npm run test:codex: 11/11; Git Bash Tier 1: 26/26; AP static: 22/22, all exit 0; 10 AP model cases remain UNVERIFIED |

Decisions: keep existing Claude runners/scorer/baselines and `npm test` unchanged; do not publish, upgrade the installed plugin, or change provider models. Preserve the current use-case catalog contracts. Checks cannot promote unavailable live scenarios to PASS.

### Live verification evidence

- Clients: Codex CLI 0.150.1; Claude Code 2.1.247; Node.js v24.15.0. No model override was supplied.
- Package copies: baseline and changed complete bundles were tested from temporary projects outside this repository. Transcripts and snapshots are in the task's temporary `dev-team-codex-94e98a0a24094d758cefebc3384b81fe` directory.
- Codex installation PASS: local marketplace add, plugin add and plugin list each exited 0 in an isolated test profile; the enabled package is 1.9.0. The normal user profile remains enabled at 1.8.0. The temporary authentication copy was removed after the probe.
- Codex live review BLOCKED: the installed skill was discovered at the test cache path, but the child CLI policy rejected all subprocess reads, including `Get-Content` and `Get-FileHash` in the fixture. The client reported BLOCKED without inventing findings. Natural-language discovery is observed; specialist execution, context-isolation marker, rework, explicit entry and resume remain UNVERIFIED. No policy bypass was attempted.
- Claude reviewer PASS before/after: both runs invoked native `dev-team:code-reviewer` and found the seeded subtraction defect. The fixture SHA-256 remained `6E78DD8D5D442A8E66B4A610AC4AA571FDD9D7201285CCDAF860CD1AA98B4CBF`. The changed package selected `dev-team:ask-reviewer` directly; the baseline first selected the overly broad Codex bridge.
- Claude Micro PASS before/after: both executed native implementor then independent code-reviewer, produced addition, and passed fresh assertions for `(2,3)=5` and `(-2,3)=1`. The changed run additionally used the existing tester as a read-only verifier; no new source/test files were requested.
- Claude PRD before/after UNVERIFIED: both real runs exercised product-analyst/adversarial-reviewer revisions. The changed package reached native doc-reviewer after three rework cycles, with no fourth debate cycle. Both clients then exited 1 on the provider's session limit (`You've hit your session limit`, reported reset 15:40 Europe/Riga); no final document-gate PASS is claimed. The remaining process had already exited when checked; no live client process was left running and no further provider attempt was made.
- BASELINE_FAIL retained: `npm test` exits 1 with `Error: no test specified`; it was intentionally not replaced. AP model cases and separate live-client smokes are different evidence sets.

### Final disposition

Status: DONE_WITH_CONCERNS. Approved source changes and offline checks are complete, independent code/document review passed, and the normal plugin installation was not changed. Runtime sign-off remains partial for the two external blockers above. Re-run the blocked Codex scenarios in a profile where ordinary file reads are permitted, and re-run the PRD comparison after provider availability returns; do not treat the current static successes as that missing proof. No publishing, version bump, commit, or update of the normal installed plugin was performed.

## v2.0.0 review contract — 2026-09-15

This section tracks the review-contract change set (three report fields `Context`/`Self-check`/`Sweep`, the `RV-<scope>-NNN` finding schema, the late-finding rule, the disposition protocol, and the document-agent Step 0 inventory) independently of the historical work above.

- Goal: add a mandatory review contract across all 12 agent prompts, the three coordinator skills, the eleven `ask-*` shortcuts, and `specs/workflow.md`, then correct the defects two independent reviews found before this documentation pass.
- Profile: Full, by inspection — no Phase 0 triage record predates this ledger entry, but the change touches all 12 agent prompts, all 3 coordinator skills, all 11 shortcuts, and `specs/workflow.md`, and is a breaking change to every agent's report contract (new required `Context:` field, `Self-check:`/`Sweep:` for the agents that carry them), which is well past the Full-profile threshold on size and reversibility alone.
- Run counter: 15/40 (Full circuit-breaker). Basis, since no per-dispatch ledger rows exist for this change set: 6 build subtasks S1–S6 (the only subtask numbering the tree itself records, in `evals/codex/README.md`'s re-anchor note) that landed the `review-contract` skill, the 12 agent prompts, the 3 coordinator skills, the 11 `ask-*` shortcuts, and `specs/workflow.md`; 1 correction to S1; 2 independent final reviews (code-reviewer and doc-reviewer, which together found 33 defects); 4 fix subtasks correcting the contract, the agent prompts, the coordinator skills, and the `ask-*` shortcuts plus `specs/workflow.md`; this documentation pass (G1); and the pending G2 (contract tests + baseline re-anchor) = 15. Discrepancy: the dispatch that requested this ledger entry framed the build work as "seven build subtasks S1–S7" and the fix work as "F1–F5"; the tree evidences only S1–S6 (`evals/codex/README.md`) and names no F-numbers anywhere, so this count uses S1–S6 and "4 fix subtasks" per the files, not the S1–S7/F1–F5 framing — see the G1 agent report's Concerns.
- Baseline: `evals/codex/baseline.json` was deliberately re-anchored from the 1.9.0 baseline at commit `13f7469a171505f4a4a378d1f56356f487c212ee` to the current working tree, for `agents/*.md` (all 12), the three coordinator skills, and the three plugin manifests — every file whose hashed content subtasks S1–S6 actually changed; files they did not touch kept their prior hash. Its `commit` field is the placeholder `uncommitted-worktree — re-anchor pending the v2.0.0 commit` (`evals/codex/README.md`).
- Local stack: N/A — this plugin ships instructions and offline static contract checks; it has no runtime service dependencies.

| Task | Agent | Status | Evidence |
|---|---|---|---|
| `skills/review-contract/` (SKILL.md + 3 references) | implementor (S1) + 1 correction | DONE | `skills/review-contract/SKILL.md`, `references/code-dimensions.md`, `references/doc-dimensions.md`, `references/finding-schema.md` present in the tree |
| 12 agent prompts — Context/Self-check/Sweep fields, RV-ID contract | implementor (S2–S4) | DONE | `git diff --stat`: all 12 `agents/*.md` modified |
| 3 coordinator skills — Required reading, Context gate (Phase 3 step 3b), review contract | implementor (S5) | DONE | `git diff --stat`: `skills/dev-team*/SKILL.md` each +26/-14 |
| 11 `ask-*` shortcuts — Required reading / review-state passthrough | implementor (S6) | DONE | `git diff --stat`: all `skills/ask-*/SKILL.md` modified |
| `specs/workflow.md` — Gates table, rework-limit table, RV-ID mermaid nodes | implementor (S6, same batch) | DONE | `git diff --stat`: `specs/workflow.md` 150 lines changed |
| Independent review 1 | code-reviewer | DONE_WITH_CONCERNS | part of the 33 defects found across both reviewers; per-reviewer split not recorded in this ledger |
| Independent review 2 | doc-reviewer | DONE_WITH_CONCERNS | part of the 33 defects found across both reviewers |
| Fix pass (4 subtasks: contract, agent prompts, coordinator skills, `ask-*` + `specs/workflow.md`) | implementor | DONE | corrections verified in the current tree, e.g. `skills/dev-team/SKILL.md:303` (Context gate at Phase 3 step 3b), `skills/dev-team/SKILL.md:231` (Required reading extended to reviewer/debate/Phase 4 dispatches), `agents/doc-reviewer.md:193,195` (`reclassified` state, `Introduced by:`/`Pre-existing Critical:` rationale lines) |
| Documentation pass (this entry) | technical writer (G1) | DONE | see the G1 agent report's Evidence field |
| Contract tests + baseline re-anchor | tester (G2) | PENDING | scheduled after G1 per dispatch order |

### Decisions

- `skills/review-contract/` is locally authored and carries no `skills-lock.json` entry — `skills-lock.json` tracks provenance for vendored (externally sourced) skills only; this repository's own coordinator and `ask-*` skills carry no lock entries either.
- No Tier 1 (`evals/runner/run-tier1.sh`) case was added for `review-contract`: Tier 1 tests natural-language phrase routing to user-facing skills, but `review-contract` is invoked by other agents' own process steps (Self-check/Sweep), never by direct user phrasing, so it doesn't fit that methodology. Its invariants are instead covered by `evals/codex/contracts.test.cjs` CX-005–CX-011 (the `Context:` field on all 12 agents; `Self-check:`/`Sweep:` scoping; the RV-ID schema and its three classes; the late-finding rationale rule; `adversarial-reviewer`'s CH-*-only exemption; the three coordinator skills' byte-identical review contract; the four document agents' Step 0 inventory; and the skill package's existence).
- `evals/codex/baseline.json` was deliberately re-anchored rather than incrementally patched, because subtasks S1–S6 changed the hashed content of every preserved/shared file the baseline tracks; re-anchoring keeps the preservation check meaningful instead of permanently red against a baseline that no longer describes the tree. G2 owns re-running this after its own changes and setting the real `commit` value.

### Open Items

- `evals/codex/baseline.json`'s `commit` field is the placeholder `uncommitted-worktree — re-anchor pending the v2.0.0 commit`; it must be set to the commit that actually lands v2.0.0 once that commit is made — a user decision, not an agent's.
- See `### Technical debt` below for two known-unfixed asymmetries review found and this pass deliberately did not fix.

### Technical debt

Closed — 2026-09-16 (prompt-contract and release-engineering pass, T1 of the v2.0.0 closeout):

- **Architecture/design rework limit (previously open above).** Question asked: which number governs — the coordinators' "Maximum 1 rework (not 2)" or the 2 stated elsewhere? Decided: the coordinator is authoritative, because it is what the orchestrating model actually executes and its "(not 2)" is a deliberate anti-bureaucracy reduction, not an oversight. `specs/workflow.md`'s rework-limit table (`specs/workflow.md:303-304`) and its architecture/design recheck loops, the `CLAUDE.md`/`AGENTS.md`/`GEMINI.md` "Independent limits" sentence and Inline Review Workflow table, and `skills/ask-architect/SKILL.md` + `skills/ask-designer/SKILL.md` all read 1 for these two gates now; every other ordinary-review gate keeps the generic 2-rework budget, which was not weakened.
- **Marketplace version drift (previously open above).** Question asked: do marketplace-file versions track the plugin version? Decided: yes. `.claude-plugin/marketplace.json` (was `1.5.0`) and `.copilot-plugin/marketplace.json` (was `1.4.0`) now read `2.0.0`, matching `package.json` and the three `plugin.json` manifests.

No open technical debt remains.
