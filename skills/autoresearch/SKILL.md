---
name: autoresearch
description: |
  Autonomous iterative improvement loop (Agent-Optimizer pattern) for optimizing ANYTHING measurable.
  Apply when the user wants to: optimize, tune, improve, benchmark, iterate, experiment autonomously,
  maximize/minimize a metric, run A/B variants automatically, find the best config/prompt/algorithm.

  Trigger phrases (EN): "optimize this", "make it faster", "improve the score", "auto-tune",
  "run experiments", "find the best version", "benchmark and improve", "keep iterating until better",
  "autonomous optimization", "self-improving loop".

  Trigger phrases (RU): "оптимизируй", "улучши показатель", "автоматически подбери параметры",
  "прогони эксперименты", "найди лучший вариант", "итерируй пока не улучшится",
  "настрой автоматически", "бенчмаркинг и улучшение".

  Domain coverage: code performance, prompt engineering, email copy, config tuning, CSS/Lighthouse
  scores, database queries, test coverage, text readability, business process throughput — anything
  where "better" can be expressed as a single number.
---

## Overview

The Agent-Optimizer pattern, originating from Andrej Karpathy's autoresearch project, asks a deceptively simple question: *what if an AI agent ran its own experiments indefinitely?*

The insight is that most optimization work follows the same shape regardless of domain — you have something to improve, a way to measure improvement, rules about what you can change, and an isolated place to make changes. The agent's job is to run that loop faster and more systematically than a human would.

This skill makes that pattern available for any measurable goal: not just neural network research, but prompt tuning, email copy optimization, config parameters, CSS performance scores, query speed, or any other domain where "better" maps to a number.

The key shift: the human defines success criteria upfront. The agent handles the trial-and-error.

---

## The Four Pillars

Every optimization project needs exactly these four things. If any pillar is missing, establish it before the loop begins.

### 1. Scalar Metric — The Score

A single number that goes up (or down) when things improve. Single means single — if you have multiple metrics, pick the one that matters most, or combine them into a weighted score.

Why scalar? Because the agent needs an unambiguous signal. "Better" must mean "higher number" (or lower, consistently).

Examples:
- **Code performance:** execution time in milliseconds (lower = better)
- **Prompt engineering:** LLM judge score 0-100 for output quality
- **Email copy:** click-through rate % from A/B test simulation
- **Config tuning:** requests-per-second under load
- **CSS/UI:** Lighthouse performance score 0-100
- **Text quality:** Flesch readability score
- **Test suite:** pass rate % or coverage %

### 2. Evaluator — The Test

An automated script that takes the current state of the Sandbox and outputs the metric. The evaluator is sacred — the agent never modifies it.

Why immutable? Because if the agent can change the test, it will eventually find a way to pass the test without actually improving anything. The evaluator is the ground truth.

Examples:
- **Code:** `hyperfine --runs 50 'node src/solution.js'` → median ms
- **Prompt:** script that calls an LLM judge on 20 test cases → average score
- **Email:** simulation script that scores copy against heuristics → conversion estimate
- **Config:** `wrk -t4 -c100 -d10s http://localhost:3000` → req/sec
- **Lighthouse:** `lighthouse --output=json | jq '.categories.performance.score'`

### 3. Program — The Rules

A `program.md` file the human writes that specifies: what to optimize, which approaches are allowed, which are forbidden, and what constraints exist.

This is the human's primary contribution. Clear rules prevent the agent from finding degenerate solutions (e.g., hardcoding test inputs, disabling the feature to make it faster, etc.).

Examples of what program.md covers:
- "Optimize the `processRecords` function in `src/processor.js` for throughput"
- "Allowed: change algorithm, data structures, batch size, loop ordering"
- "Forbidden: change function signature, remove validation, use external dependencies"
- "Constraint: output must be identical to the reference output in `fixtures/expected.json`"

### 4. Sandbox — The Asset

A single file (or tightly scoped directory) that the agent is allowed to modify. Every change happens here. Nothing outside the sandbox is touched.

Why one file? Atomic changes are traceable, reversible, and learnable. When an experiment fails, you know exactly what caused it.

Examples:
- **Code:** `src/solution.js` — the function being optimized
- **Prompt:** `prompts/system.txt` — the system prompt
- **Email:** `copy/email_v1.md` — the email body
- **Config:** `config/server.yaml` — the tunable parameters
- **CSS:** `src/styles/critical.css` — the critical path stylesheet

---

## Setup Protocol

Run this once before starting the loop.

```bash
# 1. Create an isolated branch for this optimization run
git checkout -b autoresearch/<tag>
# Example: git checkout -b autoresearch/processor-speed

# 2. Commit the starting state (baseline)
git add .
git commit -m "autoresearch: baseline"
```

Then create the project files:

**`program.md`** — write this yourself, following the template:
```
# Optimization Program

## Goal
[One sentence: what you want to improve and by how much]

## Sandbox
[Path to the single file the agent may modify]

## Evaluator
[Command that outputs the metric as a plain number]

## Metric
[Name, direction (higher/lower = better), unit]

## Allowed changes
- [list]

## Forbidden changes
- [list]

## Constraints
- [output correctness requirements, performance floors, etc.]
```

**`results.tsv`** — create with headers:
```
commit	metric_value	status	description
baseline	<run evaluator here>	kept	Starting state
```

Fill in the baseline metric by running the evaluator once on the unmodified sandbox.

**Verify the loop will work:**
```bash
# Evaluator must output a clean number (or parseable output)
<evaluator command>
# Should print something like: 142.3

# Sandbox file must exist and be committed
git status
```

---

## The Optimization Loop

Run this loop indefinitely until the user stops it or a target metric is reached.

### Phase 1 — Analyze History

Read `results.tsv` and identify patterns:
- Which types of changes improved the metric?
- Which consistently made things worse?
- Is there a trend that suggests what to try next?
- What has not been tried yet?

Generate a hypothesis: "Based on the history, I believe [change X] will improve [metric] because [reasoning]."

### Phase 2 — Make One Atomic Mutation

Apply exactly one logical change to the sandbox file. "One change" means one idea, even if it touches multiple lines.

Good atomic changes:
- Replace a sorting algorithm
- Change a batch size from 100 to 500
- Rewrite one paragraph of email copy
- Adjust a single config parameter
- Reorder CSS properties for render priority

Bad (non-atomic) changes:
- Refactor the algorithm AND change the batch size
- Rewrite the whole file
- Multiple independent experiments in one commit

### Phase 3 — Run the Evaluator

```bash
# Run the evaluator and capture the metric
METRIC=$(<evaluator command>)
echo "Metric: $METRIC"

# Also verify correctness if applicable
<correctness check command>
```

If the evaluator crashes or returns garbage, that is a crash — see the decision phase.

### Phase 4 — Decision

**If metric improved (compared to current baseline):**
```bash
git add <sandbox file>
git commit -m "autoresearch: <brief description of change> | metric: <value>"
# This commit becomes the new baseline
BASELINE=$METRIC
```

**If metric did not improve:**
```bash
git checkout -- <sandbox file>
# Do NOT commit. Log the failed attempt with the pre-change commit hash.
```

**If evaluator crashed or produced invalid output:**
```bash
# Attempt to fix (max 2 attempts)
# If fixed: continue to metric check
# If still broken after 2 attempts:
git checkout -- <sandbox file>
# Log as crashed
```

### Phase 5 — Log the Attempt

Always append to `results.tsv`, whether the attempt succeeded or failed. The log is how the agent learns.

```bash
# Get current HEAD commit (if kept) or "discarded" marker
COMMIT=$(git rev-parse --short HEAD)
STATUS="kept"  # or "discarded" or "crashed"
DESCRIPTION="<what was changed>"

echo "$COMMIT	$METRIC	$STATUS	$DESCRIPTION" >> results.tsv
```

The TSV log is committed periodically (every 5-10 iterations) to preserve it.

---

## Results Tracking

`results.tsv` format:

| Column | Type | Description |
|---|---|---|
| `commit` | string | Git short hash (kept) or `discarded`/`crashed` |
| `metric_value` | number | Raw metric value from the evaluator |
| `status` | string | `kept`, `discarded`, or `crashed` |
| `description` | string | What change was made and the hypothesis behind it |

Example:
```
commit	metric_value	status	description
baseline	142.3	kept	Starting state
a1b2c3d	138.7	kept	Replace linear scan with binary search in findRecord()
discarded	145.1	discarded	Increase batch size 100→500 - cache pressure increased latency
e4f5a6b	131.2	kept	Pre-sort input array to improve cache locality
crashed	—	crashed	Attempted memoization - introduced circular reference
e7d8c9f	128.9	kept	Replace object spread with Object.assign in hot path
```

Reading this table, the agent can see: sorting and cache locality helped; large batch sizes hurt; memoization needs care.

---

## Git Checkpoint Protocol

The git branch is the source of truth for what has worked. Discarded experiments never appear in the commit history — only improvements do.

**Keep (improvement confirmed):**
```bash
git add <sandbox file>
git commit -m "autoresearch: <description> | metric: <new> (was <old>)"
```

**Discard (no improvement):**
```bash
git checkout -- <sandbox file>
# Working tree is restored to last kept state. No commit.
```

**Crash with recovery:**
```bash
# Attempt 1: try to fix the crash in sandbox
# Run evaluator again
# If fixed and improved: keep
# If not fixed after 2 attempts:
git checkout -- <sandbox file>
# Log as crashed in results.tsv
```

**Commit the log periodically:**
```bash
git add results.tsv
git commit -m "autoresearch: update results log (N iterations)"
```

**Check current baseline at any time:**
```bash
git log --oneline -10
```

---

## Mental Rules for the Agent

**Rule 1: Never modify the evaluator.**
The evaluator is not part of the sandbox. If you modify the evaluator, you have invalidated every result. If the evaluator has a bug, stop the loop and report it to the human.

**Rule 2: One change per experiment.**
If you change two things at once and the metric improves, you don't know which change helped. If it worsens, you don't know which change hurt. Atomicity is what makes the history learnable.

**Rule 3: The log beats your intuition.**
Before making a decision, read `results.tsv`. Your intuition about what might work is less reliable than evidence from actual experiments. Let the log guide the next hypothesis.

**Rule 4: Failed experiments are data, not failures.**
A discarded attempt that reveals "batch size increases hurt performance" is valuable. Log it with enough description to be useful later.

**Rule 5: Time-box each experiment.**
If the evaluator takes more than a reasonable amount of time (set in program.md), something is wrong. Stop and investigate rather than waiting indefinitely.

**Rule 6: Don't chase noise.**
If the metric fluctuates by ±2% naturally, a 1% improvement is not a real signal. Account for variance in your decision threshold.

---

## Domain-Specific Examples

### 1. Code Performance Optimization

- **Sandbox:** `src/processor.js` — a data processing function
- **Evaluator:** `node benchmark.js` → prints median execution time in ms
- **Metric:** milliseconds (lower = better)
- **Typical mutations:** algorithm selection, data structure choice, loop ordering, pre-computation, avoiding allocation in hot paths
- **program.md note:** "Output must match `fixtures/expected.json` exactly. Verify with `node verify.js`."

### 2. Prompt Engineering

- **Sandbox:** `prompts/system_prompt.txt` — the system prompt for an LLM
- **Evaluator:** `python eval_prompt.py` → runs prompt on 20 fixed test cases through an LLM judge, prints average score 0-100
- **Metric:** judge score (higher = better)
- **Typical mutations:** reorder instructions, add/remove examples, change persona framing, adjust output format specification, add/remove constraints
- **program.md note:** "Test cases in `fixtures/test_cases.json` are immutable. Do not add examples that overlap with test cases."

### 3. Email Copy Optimization

- **Sandbox:** `copy/email.md` — email subject + body
- **Evaluator:** `node score_email.js` → runs heuristic scoring (subject line clarity, CTA prominence, word count, urgency signals) and prints a 0-100 score
- **Metric:** estimated conversion score (higher = better)
- **Typical mutations:** rewrite subject line, change CTA phrasing, adjust opening hook, modify social proof placement, change email length
- **program.md note:** "Product claims must remain factually accurate. Do not add pricing that differs from `pricing.json`."

### 4. Config Tuning

- **Sandbox:** `config/server.yaml` — server configuration parameters
- **Evaluator:** `./run_loadtest.sh` → runs a 10-second load test and prints requests/second
- **Metric:** req/sec (higher = better)
- **Typical mutations:** connection pool size, timeout values, buffer sizes, worker thread count, cache TTL values
- **program.md note:** "Latency p99 must stay below 200ms. `run_loadtest.sh` also checks this and exits non-zero if violated."

### 5. CSS / Lighthouse Score

- **Sandbox:** `src/styles/critical.css` — critical path CSS
- **Evaluator:** `node lighthouse_score.js` → runs headless Lighthouse and prints performance score 0-100
- **Metric:** Lighthouse performance score (higher = better)
- **Typical mutations:** inline vs. defer rules, font loading strategy, animation properties, selector specificity reduction, unused rule removal
- **program.md note:** "Visual regression test must pass: `node visual_test.js` must exit 0. Layout must not shift more than 0.1 CLS."

---

## Reference Files

When setting up a new autoresearch project, create this directory structure:

```
autoresearch/
  program.md          # Human-written rules (the Program pillar)
  results.tsv         # Experiment log
  evaluator/
    run.sh            # The evaluator script (never modified by agent)
    README.md         # How the evaluator works and what it outputs
```

The sandbox file lives in the main project tree, not in `autoresearch/`. It is a real project file being actively improved.

If the project has a `references/` directory, look there for domain-specific evaluation techniques, scoring rubrics, or benchmark patterns relevant to the current optimization goal.
