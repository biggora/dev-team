# Domain Examples: Autoresearch Pattern in Practice

This reference shows how the autonomous optimization loop applies across 10 distinct domains.
Each example defines the four components of the pattern:
- **Sandbox** — the mutable file or asset being mutated
- **Evaluator** — the script that scores the current state
- **Metric** — the scalar value extracted from evaluator output
- **Program** — the rules constraining valid mutations

---

## 1. Python Function Optimization

**Goal:** Speed up a pure Python function without changing its public interface or output.

| Component | Definition |
|---|---|
| Sandbox | `src/process.py` — a single function `process(data: list) -> list` |
| Evaluator | `bench.py` — runs the function 1000 times on a fixed dataset, reports median wall time |
| Metric | `time_ms` (lower is better) |
| Program | Do not change the function signature; output must remain identical to the reference output stored in `expected.pkl`; no C extensions; standard library only |

**Atomic mutation example:**
Replace `[x for x in items if x > 0]` with `list(filter(lambda x: x > 0, items))`, or convert a nested loop to `itertools.chain`.

**Example `results.tsv`:**
```
experiment_id	time_ms	notes
0001	142.3	baseline — naive double loop
0002	98.7	replaced inner loop with list comprehension
0003	61.2	switched to numpy vectorized filter
```

---

## 2. Prompt Engineering

**Goal:** Improve the quality of LLM outputs by iterating on a system prompt against a fixed test suite.

| Component | Definition |
|---|---|
| Sandbox | `prompt.txt` — the system prompt sent to the model |
| Evaluator | `eval_prompt.py` — sends 20 fixed user messages to the model, scores each response with an LLM judge (0–10), returns mean score |
| Metric | `score` (higher is better, 0–10) |
| Program | Prompt must stay under 800 tokens; must not include any test case content verbatim; must not instruct the model to output JSON unless the task requires it |

**Atomic mutation example:**
Add "Think step by step before answering." as the last sentence of the prompt, or replace "You are an assistant" with "You are an expert ${DOMAIN} consultant".

**Example `results.tsv`:**
```
experiment_id	score	notes
0001	6.1	baseline — generic assistant prompt
0002	7.4	added chain-of-thought instruction
0003	8.2	added domain expertise framing + output length constraint
```

---

## 3. Email Marketing

**Goal:** Maximize email open rate by iterating on subject lines and preview text against a simulated audience model.

| Component | Definition |
|---|---|
| Sandbox | `email_template.json` — contains `subject`, `preview_text`, and `body` fields |
| Evaluator | `simulate_opens.py` — runs subject + preview through a trained open-rate predictor model; returns predicted open rate |
| Metric | `predicted_open_rate` (higher is better, 0.0–1.0) |
| Program | Subject must be 6–60 characters; no ALL CAPS words; no spam trigger words from `blocklist.txt`; preview text must not duplicate the subject word-for-word |

**Atomic mutation example:**
Change subject from "Your weekly update" to "3 things you missed this week", or add an emoji to the start of the subject line.

**Example `results.tsv`:**
```
experiment_id	predicted_open_rate	notes
0001	0.187	baseline — generic subject
0002	0.241	added number + curiosity gap
0003	0.268	personalization token + urgency word
```

---

## 4. CSS / Frontend Performance

**Goal:** Improve the Lighthouse Performance score of a static HTML page.

| Component | Definition |
|---|---|
| Sandbox | `public/styles.css` — the stylesheet for the page |
| Evaluator | `run_lighthouse.sh` — runs `lighthouse http://localhost:3000 --output=json`, extracts `categories.performance.score` |
| Metric | `lighthouse_score` (higher is better, 0–100) |
| Program | All existing visual elements must remain visible; no inline styles in HTML; no removing semantic elements; page must still pass HTML validation |

**Atomic mutation example:**
Add `font-display: swap` to a `@font-face` rule, or move a large background image to lazy-load via a CSS class added by IntersectionObserver.

**Example `results.tsv`:**
```
experiment_id	lighthouse_score	notes
0001	54	baseline — unoptimized stylesheet
0002	61	added will-change hints for animated elements
0003	73	inlined critical CSS, deferred rest
```

---

## 5. SQL Query Optimization

**Goal:** Reduce query execution time on a fixed PostgreSQL dataset.

| Component | Definition |
|---|---|
| Sandbox | `query.sql` — a single SELECT query |
| Evaluator | `bench_query.sh` — runs the query 10 times via `psql`, reports median execution time in ms using `EXPLAIN ANALYZE` |
| Metric | `exec_time_ms` (lower is better) |
| Program | Query must return identical result set as `baseline_results.csv`; no changing table schema; no adding persistent indexes (temporary ones are allowed); must complete within 30 s |

**Atomic mutation example:**
Replace a correlated subquery with a `LEFT JOIN`, or add `WHERE` clause to push a filter before a `GROUP BY`.

**Example `results.tsv`:**
```
experiment_id	exec_time_ms	notes
0001	4320	baseline — nested correlated subquery
0002	1870	replaced with JOIN
0003	890	added covering index hint via CTE materialization
```

---

## 6. Config Tuning (nginx)

**Goal:** Maximize request throughput on a local nginx server under a fixed load pattern.

| Component | Definition |
|---|---|
| Sandbox | `nginx.conf` — the server configuration file |
| Evaluator | `bench_nginx.sh` — runs `wrk -t4 -c100 -d10s http://localhost:8080/`, parses `Requests/sec` from output |
| Metric | `requests_per_sec` (higher is better) |
| Program | Server must still return HTTP 200 for all test URLs; SSL must remain enabled; no disabling access logging entirely; `worker_processes` must not exceed CPU count |

**Atomic mutation example:**
Change `keepalive_timeout 65;` to `keepalive_timeout 30;`, or set `gzip_comp_level` from 6 to 3, or add `sendfile on;`.

**Example `results.tsv`:**
```
experiment_id	requests_per_sec	notes
0001	3420	baseline — default config
0002	4810	enabled sendfile + tcp_nopush
0003	5930	tuned worker_connections + added keepalive upstream
```

---

## 7. Text / Copywriting

**Goal:** Improve the readability of a piece of text by increasing its Flesch Reading Ease score.

| Component | Definition |
|---|---|
| Sandbox | `article.md` — a blog post or product description in Markdown |
| Evaluator | `score_readability.py` — strips Markdown, runs `textstat.flesch_reading_ease()`, outputs score |
| Metric | `flesch_score` (higher is better; 60–70 = standard; 70–80 = fairly easy) |
| Program | Factual claims must not be altered; named entities (brands, people, places) must not change; word count must stay within ±10% of original; no deleting entire paragraphs |

**Atomic mutation example:**
Split a sentence longer than 30 words into two, or replace "utilize" with "use", or change a passive construction to active voice.

**Example `results.tsv`:**
```
experiment_id	flesch_score	notes
0001	38.4	baseline — dense academic prose
0002	47.1	split 5 long sentences
0003	58.9	replaced Latinate words + active voice rewrite
```

---

## 8. API Response Optimization

**Goal:** Reduce the JSON payload size of a REST API endpoint without breaking the contract.

| Component | Definition |
|---|---|
| Sandbox | `serializer.py` — a Python function `serialize(record: dict) -> dict` that shapes the API response |
| Evaluator | `measure_payload.py` — runs `serialize()` on 100 fixture records, reports mean byte size of JSON output |
| Metric | `mean_bytes` (lower is better) |
| Program | All required fields from `api_contract.json` must be present; no lossy compression of numeric fields; response must deserialize without error; no changing field names |

**Atomic mutation example:**
Remove a field that exists in the serializer output but is not listed in `api_contract.json` as required, or convert a verbose ISO timestamp to a Unix integer.

**Example `results.tsv`:**
```
experiment_id	mean_bytes	notes
0001	2840	baseline — all fields included
0002	2210	removed 3 deprecated optional fields
0003	1780	timestamps as integers + omit null fields
```

---

## 9. Logistics / Business Rules

**Goal:** Reduce average delivery time by tuning a rule-based routing configuration.

| Component | Definition |
|---|---|
| Sandbox | `routing_rules.json` — priority-ordered list of routing rules (carrier, region, weight threshold, cutoff time) |
| Evaluator | `simulate_deliveries.py` — runs 500 historical orders through the rule engine, computes mean delivery days |
| Metric | `mean_delivery_days` (lower is better) |
| Program | Every order must be assigned a carrier; no carrier may handle more than 40% of orders (anti-monopoly constraint); total shipping cost estimate must not increase by more than 5% vs. baseline |

**Atomic mutation example:**
Move a regional carrier rule higher in the priority list, or adjust a weight threshold from 2 kg to 1.5 kg for a faster carrier tier.

**Example `results.tsv`:**
```
experiment_id	mean_delivery_days	notes
0001	4.2	baseline — default rules
0002	3.8	promoted regional carrier for zone 3
0003	3.5	tightened weight cutoff + added express tier for priority flag
```

---

## 10. ML Hyperparameter Tuning

**Goal:** Maximize validation accuracy of a model by tuning hyperparameters in a config file.

| Component | Definition |
|---|---|
| Sandbox | `hparams.json` — learning rate, batch size, dropout, scheduler type, weight decay |
| Evaluator | `train_eval.py` — trains for 5 epochs on a fixed train/val split, outputs validation accuracy |
| Metric | `val_accuracy` (higher is better, 0.0–1.0) |
| Program | Training must complete within 10 minutes on the target hardware; batch size must be a power of 2; learning rate must be in range [1e-5, 1e-1]; no changing the model architecture file |

**Atomic mutation example:**
Change `learning_rate` from `0.01` to `0.003`, or switch `scheduler` from `"constant"` to `"cosine"`.

**Example `results.tsv`:**
```
experiment_id	val_accuracy	notes
0001	0.821	baseline — default hparams
0002	0.847	lr reduced to 0.003
0003	0.871	cosine scheduler + dropout 0.2 → 0.3
```
