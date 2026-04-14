#!/bin/bash
# =============================================================================
# Tier 2: Single-Agent Dispatch — 1 API call per case
# Tests agent selection via Claude CLI with coordinator context
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVALS_DIR="$(dirname "$SCRIPT_DIR")"
PLUGIN_DIR="$(dirname "$EVALS_DIR")"
RESULTS_DIR="$EVALS_DIR/results"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
RESULT_FILE="$RESULTS_DIR/tier2-$TIMESTAMP.json"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m'

REPEAT_RUNS=$(jq '.tier_config.tier2.repeat_runs' "$EVALS_DIR/config.json")

# Build agent descriptions list for the prompt
build_agent_list() {
  local agent_list=""
  for agent_file in "$PLUGIN_DIR"/agents/*.md; do
    local name
    name=$(basename "$agent_file" .md)
    [[ "$name" == "_template" ]] && continue
    # Extract full description including examples (everything between description: and model:)
    local desc
    desc=$(sed -n '/^description:/,/^model:/p' "$agent_file" | sed '1s/^description: *|//;/^model:/d' | sed 's/^  //' | tr '\n' ' ' | sed 's/  */ /g;s/^ *//;s/ *$//')
    agent_list="$agent_list- $name: $desc\n\n"
  done
  echo -e "$agent_list"
}

AGENT_LIST=$(build_agent_list)

# Build fixture description
describe_fixture() {
  local fixture="$1"
  local fixture_dir="$EVALS_DIR/fixtures/$fixture"
  if [[ ! -d "$fixture_dir" ]]; then
    echo "Empty project (greenfield)"
    return
  fi
  echo "Files in project:"
  find "$fixture_dir" -type f -not -name '.gitkeep' | sed "s|$fixture_dir/||" | sort
}

# =============================================================================
# RUN CASES
# =============================================================================

run_tier2_cases() {
  local total=0 passed=0 total_api_calls=0
  local results="[]"

  # Collect tier 2 cases from agent-triggering and coordinator-dispatch
  local cases_files=("$EVALS_DIR/cases/agent-triggering.json" "$EVALS_DIR/cases/coordinator-dispatch.json")

  for cases_file in "${cases_files[@]}"; do
    local category
    category=$(jq -r '.category' "$cases_file")
    local count
    count=$(jq '.evals | length' "$cases_file")

    for i in $(seq 0 $((count - 1))); do
      local tier
      tier=$(jq -r ".evals[$i].tier" "$cases_file")
      [[ "$tier" != "2" ]] && continue

      local id prompt fixture
      id=$(jq -r ".evals[$i].id" "$cases_file")
      prompt=$(jq -r ".evals[$i].prompt" "$cases_file")
      fixture=$(jq -r ".evals[$i].context.fixture // \"greenfield\"" "$cases_file")

      local expected_agents not_agents
      expected_agents=$(jq -r '.evals['"$i"'].expected.agents // [] | .[]' "$cases_file" 2>/dev/null || true)
      not_agents=$(jq -r '.evals['"$i"'].expected.not_agents // [] | .[]' "$cases_file" 2>/dev/null || true)

      local fixture_desc
      fixture_desc=$(describe_fixture "$fixture")

      # Build evaluation prompt
      local eval_prompt
      eval_prompt="You are a coordinator for a dev-team plugin. Given the project context and user request, decide which specialist agent(s) to dispatch.

Available agents:
${AGENT_LIST}

Project context ($fixture):
${fixture_desc}

User request: \"${prompt}\"

Respond with ONLY a JSON object (no markdown, no explanation):
{\"agents\": [\"agent-name\", ...], \"reasoning\": \"brief explanation\"}

Choose the minimum set of agents needed. Use exact agent names from the list above."

      printf "  %s: %s ... " "$id" "$prompt"

      # Run multiple times for variance
      local run_scores=()
      for run in $(seq 1 "$REPEAT_RUNS"); do
        local response
        # Run from a temp dir to avoid picking up current project context
        local tmpdir
        tmpdir=$(mktemp -d)
        local fixture_dir="$EVALS_DIR/fixtures/$fixture"
        if [[ -d "$fixture_dir" ]]; then
          cp -r "$fixture_dir"/* "$tmpdir/" 2>/dev/null || true
        fi
        local raw_response
        raw_response=$(cd "$tmpdir" && claude -p "$eval_prompt" --output-format json --max-turns 1 2>/dev/null || echo '[]')
        rm -rf "$tmpdir" 2>/dev/null || true
        total_api_calls=$((total_api_calls + 1))

        # Extract the result text from the JSONL stream (last object with type=result)
        local result_text
        result_text=$(echo "$raw_response" | jq -r '.[] | select(.type == "result") | .result // ""' 2>/dev/null || echo "")
        # If array parsing fails, try line-by-line
        if [[ -z "$result_text" ]]; then
          result_text=$(echo "$raw_response" | grep '"type":"result"' | jq -r '.result // ""' 2>/dev/null || echo "")
        fi

        # Parse agents from the result text
        # Result might be: raw JSON, markdown-wrapped JSON, or plain text
        local predicted_agents=""
        # Try direct JSON parse
        predicted_agents=$(echo "$result_text" | jq -r '.agents // [] | .[]' 2>/dev/null || true)
        # Try extracting JSON from markdown code block
        if [[ -z "$predicted_agents" ]]; then
          local json_block
          json_block=$(echo "$result_text" | sed -n 's/.*```json\{0,1\}\(.*\)```.*/\1/p' | head -1)
          if [[ -n "$json_block" ]]; then
            predicted_agents=$(echo "$json_block" | jq -r '.agents // [] | .[]' 2>/dev/null || true)
          fi
        fi
        # Fallback: extract agent names from text
        if [[ -z "$predicted_agents" ]]; then
          predicted_agents=$(echo "$result_text" | grep -oE '(backend-dev|frontend-dev|implementor|tester|code-reviewer|architect|planner|product-analyst|ui-ux-designer)' | sort -u || true)
        fi

        # Score this run
        local run_passed=true
        for exp in $expected_agents; do
          if ! echo "$predicted_agents" | grep -qw "$exp"; then
            run_passed=false
          fi
        done
        for nexp in $not_agents; do
          if echo "$predicted_agents" | grep -qw "$nexp" 2>/dev/null; then
            run_passed=false
          fi
        done

        $run_passed && run_scores+=("1") || run_scores+=("0")
      done

      # Average score across runs
      local sum=0
      for s in "${run_scores[@]}"; do
        sum=$((sum + s))
      done
      local avg_score
      avg_score=$(awk "BEGIN {printf \"%.2f\", $sum / $REPEAT_RUNS}")

      total=$((total + 1))
      local case_passed=false
      if awk "BEGIN {exit !($avg_score >= 0.5)}"; then
        case_passed=true
        passed=$((passed + 1))
        printf "${GREEN}PASS${NC} (%.2f)\n" "$avg_score"
      else
        printf "${RED}FAIL${NC} (%.2f)\n" "$avg_score"
      fi

      results=$(echo "$results" | jq \
        --arg id "$id" \
        --arg cat "$category" \
        --arg avg "$avg_score" \
        --argjson passed "$($case_passed && echo true || echo false)" \
        '. + [{"id": $id, "category": $cat, "avg_score": ($avg | tonumber), "passed": $passed}]')
    done
  done

  local accuracy
  if (( total > 0 )); then
    accuracy=$(awk "BEGIN {printf \"%.3f\", $passed / $total}")
  else
    accuracy="0.000"
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
      "tier": 2,
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
  echo -e "${CYAN}Tier 2 Results: ${passed}/${total} (${accuracy})${NC}"
  echo -e "  API calls: $total_api_calls"
  echo -e "  Saved to: $RESULT_FILE"
}

echo -e "${CYAN}=== dev-team Eval — Tier 2: Single-Agent Dispatch ===${NC}"
echo ""
run_tier2_cases
