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
