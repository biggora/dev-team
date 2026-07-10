# Evaluator Patterns Reference

An evaluator is the measurement instrument of the autoresearch loop.
It transforms the current state of the sandbox into a single scalar number.
The quality of the loop is determined almost entirely by the quality of the evaluator.

---

## What Makes a Good Evaluator

### 1. Deterministic (or near-deterministic)

The evaluator must return the same (or nearly the same) number for the same input.
A regression that looks like noise will cause good mutations to be discarded and bad ones to be kept.

- Run benchmarks multiple times and return the median, not a single measurement.
- For non-deterministic scorers (LLM judges), average across N runs.
- Fix random seeds wherever possible.
- Use the same hardware/environment for every run.

### 2. Fast

The loop's throughput is bounded by the evaluator's runtime.
Target: under 30 seconds per evaluation. Under 10 seconds is ideal.

- Use a representative but small dataset (100–1000 samples, not millions).
- Cache fixtures to disk; never re-generate them inside the evaluator.
- Profile the evaluator itself before deploying it — avoid N+1 calls.

### 3. Isolated

The evaluator must not be affected by state left by previous experiments.

- Restart servers or clear caches between runs if they accumulate state.
- Use a fixed database snapshot, not a live database that grows.
- Do not write to shared files during evaluation; write only to stdout.

### 4. Sensitive

A good evaluator detects small, meaningful differences.
If two very different mutations produce the same score, the evaluator is too coarse.

- Prefer continuous metrics (0.0–1.0, ms, bytes) over binary pass/fail.
- Add secondary metrics to stdout for debugging, even if only the primary metric drives decisions.

---

## Output Format Convention

Every evaluator must write its output to **stdout** in `key: value` format, one metric per line:

```
primary_metric: 87.4
secondary_metric_1: 12
secondary_metric_2: 0.003
```

Rules:
- The primary metric key must match exactly the key named in `program.md`.
- Values must be bare numbers — no units, no extra text on the same line.
- Exit code 0 means success; any non-zero exit means the evaluator itself failed (not that the sandbox performed poorly). The loop discards experiments where the evaluator exits non-zero.

---

## Handling Non-Deterministic Metrics

Some metrics are inherently noisy — LLM scoring, network latency, or JIT-compiled benchmarks.
Use one of these strategies:

### Strategy A: Multiple runs, take median

```python
import statistics, subprocess, sys

RUNS = 5
scores = []
for _ in range(RUNS):
    result = subprocess.run(["python", "single_eval.py"], capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(1)
    for line in result.stdout.splitlines():
        if line.startswith("score:"):
            scores.append(float(line.split(":")[1].strip()))

print(f"score: {statistics.median(scores):.4f}")
```

### Strategy B: Fixed random seed

```python
import random, numpy as np

random.seed(42)
np.random.seed(42)
# ... rest of evaluation
```

### Strategy C: Confidence interval filter

If the variance is too high to distinguish signal from noise, measure the coefficient of variation.
If CV > 0.1 (10%), warn in stderr and increase RUNS:

```python
import statistics
cv = statistics.stdev(scores) / statistics.mean(scores)
if cv > 0.1:
    print(f"WARNING: high variance (CV={cv:.2f}), consider more runs", file=sys.stderr)
```

---

## Common Evaluator Patterns

---

### Pattern 1: Benchmark Script (Time-Based)

Use when: optimizing code speed, query time, server latency.

```python
#!/usr/bin/env python3
"""bench.py — time the process() function over 1000 iterations."""
import statistics, time, pickle, sys
from src.process import process

with open("fixtures/dataset.pkl", "rb") as f:
    dataset = pickle.load(f)

with open("fixtures/expected.pkl", "rb") as f:
    expected = pickle.load(f)

# Correctness check first — fail fast
result = process(dataset)
if result != expected:
    print("ERROR: output mismatch", file=sys.stderr)
    sys.exit(1)

# Benchmark
times = []
for _ in range(1000):
    t0 = time.perf_counter()
    process(dataset)
    times.append((time.perf_counter() - t0) * 1000)

print(f"time_ms: {statistics.median(times):.2f}")
print(f"time_ms_p95: {sorted(times)[950]:.2f}")
```

**Shell equivalent (wrapping an external command):**

```bash
#!/usr/bin/env bash
# bench_nginx.sh — measure nginx throughput with wrk
set -euo pipefail

# Reload config
sudo nginx -s reload
sleep 1

# Warmup
wrk -t2 -c10 -d3s http://localhost:8080/ > /dev/null 2>&1

# Measurement
OUTPUT=$(wrk -t4 -c100 -d10s http://localhost:8080/ 2>&1)

# Extract Requests/sec from wrk output
RPS=$(echo "$OUTPUT" | grep "Requests/sec" | awk '{print $2}')
P99=$(echo "$OUTPUT" | grep "99%" | awk '{print $2}' | tr -d 'ms')

echo "requests_per_sec: $RPS"
echo "latency_p99_ms: $P99"
```

---

### Pattern 2: Test Suite Pass Rate

Use when: optimizing code correctness, prompt reliability, config validity.

```python
#!/usr/bin/env python3
"""eval_tests.py — run pytest and report pass rate."""
import subprocess, json, sys

result = subprocess.run(
    ["pytest", "tests/", "--json-report", "--json-report-file=report.json", "-q"],
    capture_output=True,
    text=True,
)

with open("report.json") as f:
    report = json.load(f)

passed = report["summary"].get("passed", 0)
total = report["summary"].get("total", 0)

if total == 0:
    print("ERROR: no tests found", file=sys.stderr)
    sys.exit(1)

pass_rate = passed / total
print(f"pass_rate: {pass_rate:.4f}")
print(f"passed: {passed}")
print(f"total: {total}")

# Exit 1 only if pytest itself crashed (not if tests failed — that is a valid score)
if result.returncode not in (0, 1):
    sys.exit(1)
```

---

### Pattern 3: External API Scoring (LLM-as-Judge)

Use when: evaluating prompt quality, text quality, or any output that requires semantic judgment.

```python
#!/usr/bin/env python3
"""eval_prompt.py — score a system prompt against 20 test cases using Claude as judge."""
import sys, json, statistics
import anthropic

PROMPT_FILE = sys.argv[1] if len(sys.argv) > 1 else "prompt.txt"
TEST_CASES_FILE = "fixtures/test_cases.json"
JUDGE_PROMPT = """
You are an evaluation judge. Score the following customer support response
on a scale from 0 to 10, where 10 is perfect.
Respond with ONLY a JSON object: {"score": <number>, "reason": "<one sentence>"}
"""

client = anthropic.Anthropic()

with open(PROMPT_FILE) as f:
    system_prompt = f.read().strip()

with open(TEST_CASES_FILE) as f:
    test_cases = json.load(f)

scores = []
for case in test_cases:
    # Get response from the model being evaluated
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        system=system_prompt,
        messages=[{"role": "user", "content": case["question"]}],
    )
    candidate_answer = response.content[0].text

    # Score it with the judge
    judge_input = f"Question: {case['question']}\nResponse: {candidate_answer}"
    judgment = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=128,
        system=JUDGE_PROMPT,
        messages=[{"role": "user", "content": judge_input}],
    )
    try:
        parsed = json.loads(judgment.content[0].text)
        scores.append(float(parsed["score"]))
    except (json.JSONDecodeError, KeyError):
        scores.append(0.0)  # failed parse = 0 for that case

mean_score = statistics.mean(scores)
print(f"score: {mean_score:.3f}")
print(f"min_case_score: {min(scores):.1f}")
print(f"max_case_score: {max(scores):.1f}")
```

---

### Pattern 4: A/B Test Simulator

Use when: optimizing business rules, routing configs, or pricing strategies against historical data.

```python
#!/usr/bin/env python3
"""simulate_deliveries.py — score routing_rules.json against historical orders."""
import json, statistics, sys

with open("routing_rules.json") as f:
    rules = json.load(f)

with open("fixtures/historical_orders.json") as f:
    orders = json.load(f)

def apply_rules(order, rules):
    for rule in rules:
        if (rule["region"] == order["region"] and
                order["weight_kg"] <= rule["max_weight_kg"]):
            return rule["carrier"], rule["delivery_days"]
    return None, None  # no rule matched

delivery_days_list = []
carrier_counts = {}
total_cost = 0.0
baseline_cost = sum(o["baseline_cost"] for o in orders)

for order in orders:
    carrier, days = apply_rules(order, rules)
    if carrier is None:
        print(f"ERROR: unrouted order {order['id']}", file=sys.stderr)
        sys.exit(1)
    delivery_days_list.append(days)
    carrier_counts[carrier] = carrier_counts.get(carrier, 0) + 1
    total_cost += order.get(f"cost_{carrier}", order["baseline_cost"])

mean_days = statistics.mean(delivery_days_list)
max_carrier_share = max(carrier_counts.values()) / len(orders)
cost_delta_pct = (total_cost - baseline_cost) / baseline_cost * 100

if max_carrier_share > 0.40:
    print(f"ERROR: carrier concentration {max_carrier_share:.0%} > 40%", file=sys.stderr)
    sys.exit(1)

if cost_delta_pct > 5.0:
    print(f"ERROR: cost increased by {cost_delta_pct:.1f}% > 5%", file=sys.stderr)
    sys.exit(1)

print(f"mean_delivery_days: {mean_days:.2f}")
print(f"max_carrier_share: {max_carrier_share:.3f}")
print(f"cost_delta_pct: {cost_delta_pct:.2f}")
```

---

### Pattern 5: Static Analysis Score

Use when: improving code quality, readability, or linting compliance.

```bash
#!/usr/bin/env bash
# eval_quality.sh — composite code quality score from multiple linters
set -euo pipefail

FILE=${1:-src/process.py}

# Pylint: outputs a score like "Your code has been rated at 8.42/10"
PYLINT=$(python -m pylint "$FILE" --score=y 2>&1 | grep "rated at" | grep -oP '[\d.]+(?=/10)')

# Radon: cyclomatic complexity (A=1, B=2, C=3, D=4, E=5, F=6 — lower is better)
CC=$(python -m radon cc "$FILE" -a 2>&1 | grep "Average complexity" | grep -oP '[\d.]+')

# Readability (comments-to-code ratio target: >= 0.15)
LINES=$(wc -l < "$FILE")
COMMENTS=$(grep -c '^\s*#' "$FILE" || true)
RATIO=$(python3 -c "print(f'{$COMMENTS/$LINES:.3f}')")

# Composite: pylint dominates, penalize high complexity
COMPOSITE=$(python3 -c "
pylint = float('$PYLINT')
cc = float('${CC:-1}')
score = pylint - max(0, cc - 3) * 0.5  # penalty for complexity > B
print(f'{score:.2f}')
")

echo "composite_score: $COMPOSITE"
echo "pylint_score: $PYLINT"
echo "cyclomatic_complexity: $CC"
echo "comment_ratio: $RATIO"
```

---

## Template: Minimal Python Evaluator

Copy this skeleton and fill in the measurement logic:

```python
#!/usr/bin/env python3
"""
evaluator.py — autoresearch evaluator for [PROJECT NAME]

Output (stdout):
  [metric_key]: <float>

Exit codes:
  0 = success (score emitted)
  1 = evaluator internal error (experiment discarded)
"""
import sys
import statistics

# ── Configuration ────────────────────────────────────────────────────────────
SANDBOX_FILE = "sandbox_file.py"   # the file being optimized
FIXTURE_FILE = "fixtures/data.pkl" # fixed test data
METRIC_KEY   = "score"             # must match program.md
RUNS         = 3                   # repeat for stability
HIGHER_IS_BETTER = True            # document direction here

# ── Load fixtures (once, outside the measurement loop) ────────────────────
try:
    import pickle
    with open(FIXTURE_FILE, "rb") as f:
        fixtures = pickle.load(f)
except Exception as e:
    print(f"ERROR loading fixtures: {e}", file=sys.stderr)
    sys.exit(1)

# ── Load sandbox ──────────────────────────────────────────────────────────
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("sandbox", SANDBOX_FILE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
except Exception as e:
    print(f"ERROR loading sandbox: {e}", file=sys.stderr)
    sys.exit(1)

# ── Measure ───────────────────────────────────────────────────────────────
measurements = []
for i in range(RUNS):
    try:
        value = mod.measure(fixtures)   # replace with your measurement call
        measurements.append(float(value))
    except Exception as e:
        print(f"ERROR during run {i}: {e}", file=sys.stderr)
        sys.exit(1)

result = statistics.median(measurements)

# ── Emit ──────────────────────────────────────────────────────────────────
print(f"{METRIC_KEY}: {result:.4f}")
# Optional secondary metrics:
# print(f"{METRIC_KEY}_p95: {sorted(measurements)[int(RUNS*0.95)]:.4f}")
```

---

## Template: Minimal Bash Evaluator

```bash
#!/usr/bin/env bash
# evaluator.sh — autoresearch evaluator for [PROJECT NAME]
#
# Output (stdout):  metric_key: <number>
# Exit 0 = success; exit 1 = evaluator error
set -euo pipefail

SANDBOX="${1:-config.conf}"
METRIC_KEY="requests_per_sec"

# ── Validate sandbox ──────────────────────────────────────────────────────
if ! validate_command "$SANDBOX" > /dev/null 2>&1; then
    echo "ERROR: sandbox failed validation" >&2
    exit 1
fi

# ── Apply and measure ─────────────────────────────────────────────────────
apply_sandbox "$SANDBOX"   # e.g., reload server config
sleep 1                    # allow server to settle

MEASUREMENTS=()
for i in 1 2 3; do
    VAL=$(measure_command 2>/dev/null | grep -oP '[\d.]+')
    MEASUREMENTS+=("$VAL")
done

# Compute median of 3 values
MEDIAN=$(python3 -c "
import statistics, sys
vals = [float(v) for v in '${MEASUREMENTS[*]}'.split()]
print(f'{statistics.median(vals):.2f}')
")

echo "$METRIC_KEY: $MEDIAN"
```

---

## Validating That an Evaluator is Reliable

Before starting an optimization run, verify the evaluator itself with this checklist:

### 1. Repeatability test

Run the evaluator 5 times on the unmodified baseline.
The coefficient of variation (stdev / mean) should be < 5%.

```bash
for i in $(seq 5); do python evaluator.py; done
```

If CV > 5%, increase RUNS or fix the source of variance before starting.

### 2. Sensitivity test

Make a change you know is better and a change you know is worse.
Verify the evaluator scores them in the right direction with a meaningful difference (> 2x the noise level).

```bash
# apply known-better version
python evaluator.py
# apply known-worse version
python evaluator.py
```

### 3. Speed test

Time a single evaluation run:

```bash
time python evaluator.py
```

If runtime > 60 seconds, profile and optimize the evaluator before using it in the loop.

### 4. Failure mode test

Introduce a syntax error in the sandbox file.
Verify the evaluator exits non-zero (not silently returns a score).

```bash
echo "THIS IS BROKEN" >> sandbox.py
python evaluator.py
echo "Exit code: $?"
# Expected: non-zero
```

### 5. Independence test

Run the evaluator twice back-to-back without changing anything.
The second score must equal the first (for deterministic evaluators) or be within noise bounds.
If the second run is always higher/lower, the evaluator has state that persists between runs — fix this.
