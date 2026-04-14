#!/bin/bash
# =============================================================================
# Tier 3: Full Coordinator Flow — expensive (5-15 API calls per case)
# Tests full /dev-team dispatch with LLM-as-judge scoring
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVALS_DIR="$(dirname "$SCRIPT_DIR")"
PLUGIN_DIR="$(dirname "$EVALS_DIR")"
RESULTS_DIR="$EVALS_DIR/results"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
RESULT_FILE="$RESULTS_DIR/tier3-$TIMESTAMP.json"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m'

REPEAT_RUNS=$(jq '.tier_config.tier3.repeat_runs' "$EVALS_DIR/config.json")
JUDGE_PROMPT=$(cat "$SCRIPT_DIR/judge.md")

run_tier3_cases() {
  local cases_file="$EVALS_DIR/cases/coordinator-dispatch.json"
  local total=0 passed=0 total_api_calls=0
  local results="[]"

  local count
  count=$(jq '.evals | length' "$cases_file")

  for i in $(seq 0 $((count - 1))); do
    local tier
    tier=$(jq -r ".evals[$i].tier" "$cases_file")
    [[ "$tier" != "3" ]] && continue

    local id prompt fixture
    id=$(jq -r ".evals[$i].id" "$cases_file")
    prompt=$(jq -r ".evals[$i].prompt" "$cases_file")
    fixture=$(jq -r ".evals[$i].context.fixture // \"greenfield\"" "$cases_file")

    local expected
    expected=$(jq ".evals[$i].expected" "$cases_file")

    printf "  %s: %s\n" "$id" "$prompt"

    local run_scores=()
    for run in $(seq 1 "$REPEAT_RUNS"); do
      printf "    Run %d/%d ... " "$run" "$REPEAT_RUNS"

      # Create temp directory with fixture
      local tmpdir
      tmpdir=$(mktemp -d)
      local fixture_dir="$EVALS_DIR/fixtures/$fixture"
      if [[ -d "$fixture_dir" ]]; then
        cp -r "$fixture_dir"/* "$tmpdir/" 2>/dev/null || true
      fi

      # Run coordinator via Claude CLI (analyze only)
      local raw_coord
      raw_coord=$(cd "$tmpdir" && claude -p "You are the dev-team coordinator. Analyze this task and describe your dispatch plan in detail. Do NOT execute anything, just describe: which agents you would dispatch, in what order (parallel vs sequential), what context each agent gets, and what stack-specific phrases you would include in their prompts.

Task: $prompt

Respond with your complete analysis and dispatch plan." --output-format json --max-turns 3 2>/dev/null || echo '[]')
      total_api_calls=$((total_api_calls + 1))

      # Extract result text from JSONL stream
      local coordinator_response
      coordinator_response=$(echo "$raw_coord" | jq -r '.[] | select(.type == "result") | .result // ""' 2>/dev/null || echo "")
      if [[ -z "$coordinator_response" ]]; then
        coordinator_response=$(echo "$raw_coord" | grep '"type":"result"' | jq -r '.result // ""' 2>/dev/null || echo "ERROR: no result")
      fi

      # Score with LLM-as-judge
      local judge_input="## Test Case
ID: $id
Prompt: $prompt
Fixture: $fixture
Expected behavior: $expected

## Actual Coordinator Response
$coordinator_response"

      local raw_judge
      raw_judge=$(claude -p "${JUDGE_PROMPT}

${judge_input}

IMPORTANT: Reply with ONLY a JSON object, no markdown or explanation." --output-format json --max-turns 1 2>/dev/null || echo '[]')
      total_api_calls=$((total_api_calls + 1))

      # Extract judge result
      local judge_result
      judge_result=$(echo "$raw_judge" | jq -r '.[] | select(.type == "result") | .result // ""' 2>/dev/null || echo "")
      if [[ -z "$judge_result" ]]; then
        judge_result=$(echo "$raw_judge" | grep '"type":"result"' | jq -r '.result // ""' 2>/dev/null || echo '{"overall": 0}')
      fi

      local overall_score
      overall_score=$(echo "$judge_result" | jq -r '.overall // 0' 2>/dev/null || echo "0")

      printf "score=%.2f\n" "$overall_score"
      run_scores+=("$overall_score")

      rm -rf "$tmpdir"
    done

    # Average across runs
    local sum=0
    for s in "${run_scores[@]}"; do
      sum=$(awk "BEGIN {printf \"%.3f\", $sum + $s}")
    done
    local avg_score
    avg_score=$(awk "BEGIN {printf \"%.3f\", $sum / $REPEAT_RUNS}")

    total=$((total + 1))
    local case_passed=false
    if awk "BEGIN {exit !($avg_score >= 0.5)}"; then
      case_passed=true
      passed=$((passed + 1))
      printf "    ${GREEN}AVG: %.3f PASS${NC}\n" "$avg_score"
    else
      printf "    ${RED}AVG: %.3f FAIL${NC}\n" "$avg_score"
    fi

    results=$(echo "$results" | jq \
      --arg id "$id" \
      --arg avg "$avg_score" \
      --argjson passed "$($case_passed && echo true || echo false)" \
      '. + [{"id": $id, "avg_score": ($avg | tonumber), "passed": $passed}]')
  done

  local accuracy
  if (( total > 0 )); then
    accuracy=$(awk "BEGIN {printf \"%.3f\", $passed / $total}")
  else
    accuracy="0"
  fi

  jq -n \
    --arg ts "$(date -Iseconds)" \
    --arg commit "$(cd "$PLUGIN_DIR" && git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" \
    --argjson cases "$results" \
    --argjson total "$total" \
    --argjson passed "$passed" \
    --arg accuracy "$accuracy" \
    --argjson api "$total_api_calls" \
    '{
      "timestamp": $ts,
      "tier": 3,
      "commit": $commit,
      "cases": $cases,
      "summary": {
        "total": $total,
        "passed": $passed,
        "accuracy": ($accuracy | tonumber),
        "api_calls": $api
      }
    }' > "$RESULT_FILE"

  echo ""
  echo -e "${CYAN}Tier 3 Results: ${passed}/${total} (${accuracy})${NC}"
  echo -e "  API calls: $total_api_calls"
  echo -e "  Saved to: $RESULT_FILE"
}

echo -e "${CYAN}=== dev-team Eval — Tier 3: Full Coordinator Flow ===${NC}"
echo -e "${YELLOW}WARNING: This tier is expensive (~\$1-4 per run)${NC}"
echo ""
run_tier3_cases
