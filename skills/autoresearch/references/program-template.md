# Program Template: Autoresearch Loop

A `program.md` is the contract the optimization loop operates under.
It answers three questions: what are we improving, how do we measure it, and what are we allowed to touch.

---

## Universal Template

```markdown
# Autoresearch Program: [PROJECT NAME]
Date: YYYY-MM-DD
Operator: [your name / team]

---

## Goal

One sentence stating what we are optimizing and why it matters.

Example: "Reduce the median response latency of the user-lookup endpoint from ~200 ms to under 100 ms
without changing the public API contract."

---

## Metric

- **Name:** [metric_key as it appears in evaluator output]
- **Direction:** [higher is better | lower is better]
- **Unit:** [ms | score | requests/sec | bytes | etc.]
- **Baseline:** [measured value before optimization starts]
- **Target:** [value that constitutes success; leave blank for open-ended runs]

The evaluator MUST print this key to stdout in the format:
```
metric_key: <numeric value>
```

---

## Sandbox

- **File:** `[path/to/file]`
- **Scope:** [which sections / functions / fields are mutable]
- **Off-limits:** [what must not change — interfaces, dependencies, tests, etc.]
- **Integrity check:** [how to verify the sandbox file is still valid after a mutation]

---

## Evaluator

- **Script:** `[path/to/evaluator]`
- **Runtime:** [Python 3.11 | Bash | Node.js | etc.]
- **Invocation:** `[exact shell command to run it]`
- **Expected runtime:** [< N seconds per run]
- **Output format:**
  ```
  metric_key: <value>
  [optional secondary metrics in the same format]
  ```
- **Exit codes:** 0 = success; non-zero = evaluator failure (experiment is discarded)

---

## Constraints

### Allowed mutations
- [List of permitted change types — e.g., "reorder statements", "change numeric constants", "rename local variables"]

### Forbidden mutations
- [List of disallowed changes — e.g., "add new imports", "change function signatures", "modify test files"]

### Validation rules
- [Rules the sandbox file must pass after every mutation before the evaluator runs — e.g., "must parse as valid JSON", "must import without error", "linter must pass"]

---

## Time Budget

- **Max time per experiment:** [N seconds]
- **Max total experiments:** [N | unlimited]
- **Wall-clock budget:** [N hours | unlimited]

---

## Success Criteria

Stop when any of the following is true:
1. Metric reaches [target value].
2. Metric has not improved in [N] consecutive experiments.
3. Wall-clock budget is exhausted.

---

## Output

- Results logged to: `results.tsv` (tab-separated: `experiment_id`, `[metric_key]`, `notes`)
- Commits saved to: current git branch
- Best state tagged as: `autoresearch/best`
```

---

## Filled-In Example 1: Python Performance Optimization

```markdown
# Autoresearch Program: Optimize process() Function
Date: 2026-06-16
Operator: Aleksejs

---

## Goal

Speed up the `process(data)` function in `src/process.py` on a 10,000-item list
to reduce API latency on the hot path.

---

## Metric

- **Name:** time_ms
- **Direction:** lower is better
- **Unit:** ms
- **Baseline:** 142.3
- **Target:** < 50

---

## Sandbox

- **File:** `src/process.py`
- **Scope:** The body of the `process()` function only. Helper functions it defines internally are also in scope.
- **Off-limits:** Function signature `process(data: list) -> list` must not change. No new top-level imports.
- **Integrity check:** `python -c "from src.process import process; process([])"` must exit 0.

---

## Evaluator

- **Script:** `bench.py`
- **Runtime:** Python 3.11
- **Invocation:** `python bench.py`
- **Expected runtime:** < 5 seconds
- **Output format:**
  ```
  time_ms: 98.7
  ```
- **Exit codes:** 0 = success; 1 = output mismatch vs. expected.pkl

---

## Constraints

### Allowed mutations
- Any pure Python rewrite of the function body
- Using stdlib modules already imported in the file
- Changing data structures (list → dict, etc.) internally

### Forbidden mutations
- Adding `import` statements for third-party packages
- Changing the function's return type
- Modifying `bench.py` or `expected.pkl`

### Validation rules
- File must parse: `python -m py_compile src/process.py`
- Output must match: evaluator exits 0 only if output equals expected.pkl

---

## Time Budget

- **Max time per experiment:** 10 seconds
- **Max total experiments:** 200
- **Wall-clock budget:** 2 hours

---

## Success Criteria

Stop when any of:
1. `time_ms` < 50
2. No improvement in 30 consecutive experiments
3. 2-hour budget exhausted
```

---

## Filled-In Example 2: Prompt Engineering

```markdown
# Autoresearch Program: Customer Support Prompt Optimization
Date: 2026-06-16
Operator: ML Team

---

## Goal

Improve the quality of Claude's customer support responses by iterating on the system prompt,
as measured by an LLM judge scoring 20 fixed test cases.

---

## Metric

- **Name:** score
- **Direction:** higher is better
- **Unit:** points (0.0–10.0)
- **Baseline:** 6.1
- **Target:** 8.5

---

## Sandbox

- **File:** `prompt.txt`
- **Scope:** Entire file content.
- **Off-limits:** Must not include any of the 20 test case questions verbatim. Must stay under 800 tokens (checked via `tiktoken`).
- **Integrity check:** `python check_prompt.py prompt.txt` — verifies token count and no test leakage.

---

## Evaluator

- **Script:** `eval_prompt.py`
- **Runtime:** Python 3.11
- **Invocation:** `python eval_prompt.py prompt.txt`
- **Expected runtime:** < 90 seconds (20 API calls)
- **Output format:**
  ```
  score: 7.4
  min_case_score: 4.0
  max_case_score: 9.5
  ```
- **Exit codes:** 0 = success; 1 = API error; 2 = token limit exceeded

---

## Constraints

### Allowed mutations
- Rewording any sentence
- Adding or removing instructions
- Changing tone, persona, or formatting directives
- Adding examples (as long as they are not test cases)

### Forbidden mutations
- Including test case content
- Hardcoding expected answers
- Setting temperature or other model parameters inside the prompt

### Validation rules
- Token count <= 800 (tiktoken cl100k_base)
- No test case leakage (eval by `check_prompt.py`)

---

## Time Budget

- **Max time per experiment:** 120 seconds
- **Max total experiments:** 50
- **Wall-clock budget:** 3 hours

---

## Success Criteria

Stop when any of:
1. `score` >= 8.5
2. No improvement in 10 consecutive experiments
3. 3-hour budget exhausted
```

---

## Filled-In Example 3: Config Tuning (nginx)

```markdown
# Autoresearch Program: nginx Throughput Tuning
Date: 2026-06-16
Operator: DevOps

---

## Goal

Maximize HTTP requests-per-second for a static file server under a realistic concurrent load
by tuning nginx.conf parameters.

---

## Metric

- **Name:** requests_per_sec
- **Direction:** higher is better
- **Unit:** req/s
- **Baseline:** 3420
- **Target:** 6000

---

## Sandbox

- **File:** `/etc/nginx/nginx.conf` (working copy: `nginx.conf`)
- **Scope:** Any directive inside `http {}` and `server {}` blocks.
- **Off-limits:** `worker_processes` must not exceed $(nproc); SSL directives must remain; `access_log` must stay on.
- **Integrity check:** `nginx -t -c $(pwd)/nginx.conf` must exit 0.

---

## Evaluator

- **Script:** `bench_nginx.sh`
- **Runtime:** Bash
- **Invocation:** `bash bench_nginx.sh`
- **Expected runtime:** < 20 seconds
- **Output format:**
  ```
  requests_per_sec: 4810.3
  latency_p99_ms: 18.4
  ```
- **Exit codes:** 0 = success; 1 = nginx failed to reload; 2 = server returned non-200

---

## Constraints

### Allowed mutations
- Any numeric tuning directive (timeouts, buffer sizes, worker_connections, etc.)
- Enabling/disabling nginx modules already compiled in
- gzip settings

### Forbidden mutations
- Removing SSL
- Disabling access_log
- Changing `listen` port
- Modifying the upstream app

### Validation rules
- Config syntax check: `nginx -t -c nginx.conf`
- Health check: `curl -sf http://localhost:8080/health` returns 200

---

## Time Budget

- **Max time per experiment:** 30 seconds
- **Max total experiments:** 100
- **Wall-clock budget:** 1 hour

---

## Success Criteria

Stop when any of:
1. `requests_per_sec` >= 6000
2. No improvement in 15 consecutive experiments
3. 1-hour budget exhausted
```
