#!/bin/bash
# Deterministic contract checks for the isolated adversarial-planning v1 suite.
# This suite is intentionally not included in run-all.sh until a behavioral baseline exists.
# Keep this runner LF-only; .gitattributes enforces LF for Windows checkouts.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVALS_DIR="$(dirname "$SCRIPT_DIR")"
PLUGIN_DIR="$(dirname "$EVALS_DIR")"
CASES_FILE="$EVALS_DIR/cases/adversarial-planning-v1.json"

MODE="${1:-}"
if [[ "$MODE" != "--static-only" && "$MODE" != "--model-manifest" ]]; then
  echo "Usage: $0 --static-only|--model-manifest" >&2
  echo "Model-backed judging is defined in adversarial-judge-v1.md and requires a separately recorded baseline." >&2
  exit 2
fi

PYTHON=""
for candidate in python3 python python.exe py.exe; do
  if command -v "$candidate" >/dev/null 2>&1; then
    PYTHON="$candidate"
    break
  fi
done

if [[ -z "$PYTHON" ]]; then
  echo "FAIL suite no Python interpreter found (tried python3, python, python.exe, py.exe)" >&2
  exit 127
fi

"$PYTHON" - "$PLUGIN_DIR" "$CASES_FILE" "$MODE" <<'PY'
import json
import re
import sys
from pathlib import Path

plugin_dir = Path(sys.argv[1])
cases_file = Path(sys.argv[2])
mode = sys.argv[3]
with cases_file.open(encoding="utf-8") as handle:
    suite = json.load(handle)

if suite.get("version") != 1 or suite.get("category") != "adversarial-planning" or not suite.get("evals"):
    print("FAIL suite invalid-version-or-category", file=sys.stderr)
    raise SystemExit(1)

allowed_suite = {"category", "version", "baseline_status", "evals"}
allowed_case = {"id", "kind", "execution", "target", "prompt", "context", "expected", "tags"}
allowed_static = {"required_tokens", "forbidden_tokens", "ordered_tokens", "exact_frontmatter_tools", "glob_absent"}
allowed_model_expected = {"status", "debate_verdict", "required_dispositions", "carried_challenge_ids", "required_challenge_categories", "review_mode", "arbitration_decisions", "full_review_performed", "next_action", "ownership", "restart_policy", "ordered_agents"}
allowed_context = {"fixture", "artifact", "artifact_version", "mode", "pass", "cycle", "original_request", "prior_challenge_transcript"}
allowed_ownership = {"expected_mutated_paths", "forbidden_artifacts"}

unknown_suite = set(suite) - allowed_suite
if unknown_suite:
    print(f"FAIL suite unknown-fields:{sorted(unknown_suite)}", file=sys.stderr)
    raise SystemExit(1)

schema_errors = []
for case in suite["evals"]:
    case_id = case.get("id", "<missing-id>")
    execution = case.get("execution")
    expected = case.get("expected", {})
    if execution not in (None, "model-backed"):
        schema_errors.append(f"{case_id}:unsupported-execution:{execution}")
    if execution == "model-backed":
        if "static" in expected:
            schema_errors.append(f"{case_id}:static-assertions-on-model-case")
        categories = expected.get("required_challenge_categories")
        if categories is not None and (
            not isinstance(categories, list)
            or not categories
            or not all(isinstance(item, str) and item for item in categories)
        ):
            schema_errors.append(f"{case_id}:invalid-required-challenge-categories")
    else:
        model_fields = set(expected) & allowed_model_expected
        if model_fields:
            schema_errors.append(f"{case_id}:model-assertions-on-static-case:{sorted(model_fields)}")

if schema_errors:
    for error in schema_errors:
        print(f"FAIL schema {error}", file=sys.stderr)
    raise SystemExit(1)

model_cases = [case for case in suite["evals"] if case.get("execution") == "model-backed"]
if mode == "--model-manifest":
    print(json.dumps({"suite": "adversarial-planning-v1", "judge": "evals/runner/adversarial-judge-v1.md", "cases": model_cases}, indent=2))
    raise SystemExit(0)

passed = 0
failed = 0
unverified = 0
for case in suite["evals"]:
    case_id = case["id"]
    target = case["target"]
    target_path = plugin_dir / target
    static = case.get("expected", {}).get("static", {})
    details = []

    unknown_case = set(case) - allowed_case
    unknown_static = set(static) - allowed_static
    unknown_expected = set(case.get("expected", {})) - ({"static"} | allowed_model_expected)
    if unknown_case:
        details.append(f"unknown-case-fields:{sorted(unknown_case)}")
    if unknown_static:
        details.append(f"unknown-static-assertions:{sorted(unknown_static)}")
    if unknown_expected:
        details.append(f"unknown-expected-assertions:{sorted(unknown_expected)}")

    if case.get("execution") == "model-backed":
        context = case.get("context", {})
        expected = case.get("expected", {})
        unknown_context = set(context) - allowed_context
        ownership = expected.get("ownership", {})
        if unknown_context:
            details.append(f"unknown-context-fields:{sorted(unknown_context)}")
        unknown_ownership = set(ownership) - allowed_ownership
        if unknown_ownership:
            details.append(f"unknown-ownership-assertions:{sorted(unknown_ownership)}")
        required_context = {"fixture", "artifact", "artifact_version", "mode", "original_request", "prior_challenge_transcript"}
        missing_context = required_context - set(context)
        if missing_context:
            details.append(f"missing-model-context:{sorted(missing_context)}")
        if not case.get("prompt") or not (set(expected) & allowed_model_expected):
            details.append("missing-model-prompt-or-expectations")
        fixture_path = plugin_dir / "evals" / "fixtures" / str(context.get("fixture", "")) / str(context.get("artifact", ""))
        if not fixture_path.is_file():
            details.append(f"missing-model-artifact:{fixture_path.relative_to(plugin_dir)}")

        if details:
            failed += 1
            print(f"FAIL {case_id} {' '.join(details)}", file=sys.stderr)
        else:
            unverified += 1
            print(f"UNVERIFIED {case_id} model-backed; emit with --model-manifest")
        continue

    if not target_path.is_file():
        details.append(f"missing-target:{target}")
        content = ""
    else:
        content = target_path.read_text(encoding="utf-8")
        for token in static.get("required_tokens", []):
            if token not in content:
                details.append(f"missing-token:{token}")
        for token in static.get("forbidden_tokens", []):
            if token in content:
                details.append(f"forbidden-token:{token}")
        position = -1
        for token in static.get("ordered_tokens", []):
            next_position = content.find(token, position + 1)
            if next_position < 0:
                details.append(f"ordered-token-missing-or-out-of-order:{token}")
                break
            position = next_position
        expected_tools = static.get("exact_frontmatter_tools")
        if expected_tools is not None:
            frontmatter = content.split("---", 2)[1] if content.startswith("---") else ""
            match = re.search(r"^tools:\s*(.+)$", frontmatter, re.MULTILINE)
            actual_tools = [item.strip() for item in match.group(1).split(",")] if match else []
            if actual_tools != expected_tools:
                details.append(f"tools:{actual_tools}!={expected_tools}")

    for pattern in static.get("glob_absent", []):
        if any(plugin_dir.glob(pattern)):
            details.append(f"forbidden-artifact:{pattern}")

    if details:
        failed += 1
        print(f"FAIL {case_id} {' '.join(details)}", file=sys.stderr)
    else:
        passed += 1
        print(f"PASS {case_id}")

total = passed + failed
print(f"adversarial-planning-v1 static: {passed}/{total} passed")
print(f"adversarial-planning-v1 model-backed: {unverified} UNVERIFIED")
raise SystemExit(1 if failed else 0)
PY
