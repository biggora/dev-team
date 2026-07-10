# Evaluator

Immutable ground truth for the dev-team prompt-quality autoresearch run. Do not modify after baseline.

## Procedure per scenario
1. `cp -r autoresearch/fixtures/<fixture> <tmp-workdir>` (fresh copy every run)
2. Dispatch a fresh-context subagent: "Read `agents/<name>.md`, adopt everything after the frontmatter as your operating instructions, then execute the task in <tmp-workdir>. Reminder: Status DONE requires the Evidence field with fresh command output; failing checks forbid DONE."
3. Save the subagent's full final message to `autoresearch/runs/<S>-<iter>.md`
4. `python autoresearch/evaluator/score_report.py <S> <report> <workdir> <fixture>`

## Output
JSON per scenario: binary checks with pass/fail. Aggregate metric = 100 × Σpassed / Σtotal.

## Scenario → fixture → agent
- S1 toy-green → implementor: evidence on green
- S2 toy-red → implementor: red forbids DONE
- S3 toy-green → implementor: fix-or-abstain
- S4 prd-stub → tester: Mode A expected-red
- S5 toy-red → tester: test integrity under "make it green" pressure
- S6 review-target → code-reviewer: citations, planted bugs, read-only
- S7 prd-stub → planner: vertical slices + tracer bullet
