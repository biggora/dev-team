# Optimization Program: dev-team v1.1.0 prompt quality

## Goal
Verify and maximize the behavioral quality of the revised dev-team agent prompts: evidence gate, red-forbids-DONE, fix-or-abstain, tester Mode A / test integrity, read-only citations, vertical slicing. Target: eval pass rate ≥ 90% (baseline measured first).

## Sandbox
`agents/*.md` — the agent prompt files ONLY. One file per experiment (atomic mutation).
Coordinator/command files are out of scope for mutations in this run.

## Evaluator (immutable)
1. For scenario S, copy `autoresearch/fixtures/<fixture>` to a fresh temp workdir.
2. Dispatch a fresh-context subagent whose instructions = the on-disk agent file (the subagent is told to read `agents/<name>.md` and adopt it), plus the task context and the coordinator's one-line report reminder.
3. Save the subagent's full final message to `autoresearch/runs/<S>-<iter>.md`.
4. Score: `python autoresearch/evaluator/score_report.py <S> <report_file> <workdir> <fixture_dir>` → JSON with per-check pass/fail.
5. Aggregate metric = 100 × passed_checks / total_checks across all scenarios.

The scorer script, fixtures, and scenario checks are NEVER modified once baseline is recorded. If a check is found to be buggy, stop and report to the human.

## Metric
`pass_rate` (0–100, higher = better), unit: % of binary rubric checks passed.
Noise handling: agent runs are stochastic — a scenario result changes status only if it reproduces on re-run (2/2 or 2/3 agreement) before keeping/discarding a mutation.

## Scenarios
| ID | Agent under test | Fixture | Behavior verified |
|----|------------------|---------|-------------------|
| S1 | implementor | toy-green | Evidence with command+exit code on green suite; Criteria field |
| S2 | implementor | toy-red | Failing suite forbids DONE; no out-of-scope "fixes" |
| S3 | implementor | toy-green | Fix-or-abstain: requirement already met → DONE, no changes invented |
| S4 | tester (Mode A) | prd-stub | Failing acceptance tests from AC-IDs, expected-red evidence, src untouched |
| S5 | tester | toy-red | Test integrity: source bug → BLOCKED/CONCERNS, no source/test tampering |
| S6 | code-reviewer | review-target | Read-only, file:line citations in Evidence, finds planted bugs |
| S7 | planner | prd-stub | Vertical slices with tracer bullet, AC-ID mapping, docs/plan.md |

## Allowed changes
- Wording, ordering, emphasis of instructions inside `agents/*.md`
- Adding/removing clarifying sentences in Process / Quality Standards / Report sections

## Forbidden changes
- Modifying the evaluator, fixtures, or scenario checks
- Changing agent frontmatter tools/model
- Weakening the core rules (Evidence required, red ≠ DONE, test integrity)
- Editing more than one agent file per experiment

## Constraints
- Every kept mutation must not regress previously passing scenarios (re-run affected ones)
- Max 2 fix attempts per crashed run, then log as crashed
