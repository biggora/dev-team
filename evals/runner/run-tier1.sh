#!/bin/bash
# =============================================================================
# Tier 1: Static Analysis — Zero API calls
# Tests: skill-injection (metadata matching) + agent-triggering (keyword overlap)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVALS_DIR="$(dirname "$SCRIPT_DIR")"
PLUGIN_DIR="$(dirname "$EVALS_DIR")"
RESULTS_DIR="$EVALS_DIR/results"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
RESULT_FILE="$RESULTS_DIR/tier1-$TIMESTAMP.json"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# =============================================================================
# SKILL METADATA EXTRACTION
# =============================================================================

extract_yaml_list() {
  # Extract a YAML list field from a SKILL.md metadata block
  local file="$1" field="$2"
  sed -n "/^---/,/^---/p" "$file" | \
    sed -n "/^  *${field}:/,/^  [a-zA-Z]/p" | \
    grep '^ *- ' | sed 's/^ *- *"\{0,1\}//;s/"\{0,1\} *$//'
}

extract_prompt_phrases() {
  local file="$1"
  sed -n "/^---/,/^---/p" "$file" | \
    sed -n '/promptSignals:/,/^  [a-zA-Z]/p' | \
    sed -n '/phrases:/,/^ *[a-z]/p' | \
    grep '^ *- ' | sed 's/^ *- *"\{0,1\}//;s/"\{0,1\} *$//'
}

extract_prompt_allof() {
  local file="$1"
  sed -n "/^---/,/^---/p" "$file" | \
    sed -n '/promptSignals:/,/^  [a-zA-Z]/p' | \
    sed -n '/allOf:/,/^ *[a-z]/p' | \
    grep '^ *- \[' | sed 's/^ *- *\[//;s/\] *$//;s/"//g'
}

extract_prompt_noneof() {
  local file="$1"
  sed -n "/^---/,/^---/p" "$file" | \
    sed -n '/promptSignals:/,/^  [a-zA-Z]/p' | \
    sed -n '/noneOf:/,/^ *[a-z]/p' | \
    grep '^ *- ' | sed 's/^ *- *"\{0,1\}//;s/"\{0,1\} *$//'
}

extract_min_score() {
  local file="$1"
  sed -n "/^---/,/^---/p" "$file" | grep 'minScore:' | awk '{print $2}'
}

# =============================================================================
# SKILL MATCHING ENGINE
# =============================================================================

match_skill() {
  # Returns: score for a given skill against a signal
  local skill_dir="$1" signal_type="$2" signal_value="$3"
  local skill_file="$skill_dir/SKILL.md"
  local score=0

  if [[ ! -f "$skill_file" ]]; then
    echo "0"
    return
  fi

  local signal_lower
  signal_lower=$(echo "$signal_value" | tr '[:upper:]' '[:lower:]')

  case "$signal_type" in
    path)
      # Check pathPatterns — glob match
      while IFS= read -r pattern; do
        [[ -z "$pattern" ]] && continue
        # Convert glob to simple match: strip leading **/ and check suffix
        local suffix
        suffix=$(echo "$pattern" | sed 's|^\*\*/||')
        # Check if signal matches the suffix pattern (simple glob)
        local match_pattern
        match_pattern=$(echo "$suffix" | sed 's/\./\\./g;s/\*/.*/g')
        if echo "$signal_value" | grep -qE "(^|/)${match_pattern}$"; then
          score=100  # pathPattern match is definitive
          break
        fi
      done < <(extract_yaml_list "$skill_file" "pathPatterns")
      ;;

    bash)
      # Check bashPatterns — prefix match
      while IFS= read -r pattern; do
        [[ -z "$pattern" ]] && continue
        local pat_base
        pat_base=$(echo "$pattern" | sed 's/ \*$//')
        if [[ "$signal_value" == "$pat_base"* ]]; then
          score=100
          break
        fi
      done < <(extract_yaml_list "$skill_file" "bashPatterns")
      ;;

    import)
      # Check importPatterns — substring match
      while IFS= read -r pattern; do
        [[ -z "$pattern" ]] && continue
        if echo "$signal_lower" | grep -qi "$pattern"; then
          score=100
          break
        fi
      done < <(extract_yaml_list "$skill_file" "importPatterns")
      ;;

    prompt)
      # Check promptSignals — phrase scoring
      local blocked=false

      # noneOf: hard block
      while IFS= read -r phrase; do
        [[ -z "$phrase" ]] && continue
        local phrase_lower
        phrase_lower=$(echo "$phrase" | tr '[:upper:]' '[:lower:]')
        if echo "$signal_lower" | grep -qi "$phrase_lower"; then
          blocked=true
          break
        fi
      done < <(extract_prompt_noneof "$skill_file")

      if $blocked; then
        echo "0"
        return
      fi

      # phrases: +6 per match
      while IFS= read -r phrase; do
        [[ -z "$phrase" ]] && continue
        local phrase_lower
        phrase_lower=$(echo "$phrase" | tr '[:upper:]' '[:lower:]')
        if echo "$signal_lower" | grep -qi "$phrase_lower"; then
          score=$((score + 6))
        fi
      done < <(extract_prompt_phrases "$skill_file")

      # allOf: +4 per group if ALL words present
      while IFS= read -r group; do
        [[ -z "$group" ]] && continue
        local all_present=true
        IFS=',' read -ra words <<< "$group"
        for word in "${words[@]}"; do
          word=$(echo "$word" | sed 's/^ *//;s/ *$//' | tr '[:upper:]' '[:lower:]')
          if ! echo "$signal_lower" | grep -qi "$word"; then
            all_present=false
            break
          fi
        done
        if $all_present; then
          score=$((score + 4))
        fi
      done < <(extract_prompt_allof "$skill_file")

      # Check minScore threshold
      local min_score
      min_score=$(extract_min_score "$skill_file")
      min_score=${min_score:-6}
      if (( score < min_score )); then
        score=0
      fi
      ;;
  esac

  echo "$score"
}

# =============================================================================
# AGENT KEYWORD MATCHING
# =============================================================================

extract_agent_text() {
  # Extract description + examples from agent .md for keyword matching
  local agent_file="$1"
  sed -n '/^description:/,/^[a-z]*:/p' "$agent_file" | head -n -1 | tr '[:upper:]' '[:lower:]'
}

match_agent() {
  # Score: count keyword overlap between prompt and agent description
  local agent_file="$1" prompt="$2"
  local prompt_lower
  prompt_lower=$(echo "$prompt" | tr '[:upper:]' '[:lower:]')
  local agent_text
  agent_text=$(extract_agent_text "$agent_file")

  local score=0
  for word in $prompt_lower; do
    # Skip short/common words
    [[ ${#word} -lt 4 ]] && continue
    if echo "$agent_text" | grep -qw "$word"; then
      score=$((score + 1))
    fi
  done
  echo "$score"
}

find_best_agent() {
  local prompt="$1"
  local best_agent=""
  local best_score=0

  for agent_file in "$PLUGIN_DIR"/agents/*.md; do
    local name
    name=$(basename "$agent_file" .md)
    [[ "$name" == "_template" ]] && continue

    local score
    score=$(match_agent "$agent_file" "$prompt")
    if (( score > best_score )); then
      best_score=$score
      best_agent=$name
    fi
  done
  echo "$best_agent"
}

# =============================================================================
# RUN SKILL INJECTION TESTS
# =============================================================================

run_skill_injection_tests() {
  local cases_file="$EVALS_DIR/cases/skill-injection.json"
  local total=0 passed=0 failed=0
  local results="[]"

  local count
  count=$(jq '.evals | length' "$cases_file")

  for i in $(seq 0 $((count - 1))); do
    local id signal_type signal_value
    id=$(jq -r ".evals[$i].id" "$cases_file")
    signal_type=$(jq -r ".evals[$i].signal_type" "$cases_file")
    signal_value=$(jq -r ".evals[$i].signal_value" "$cases_file")

    local expected_injected expected_not_injected
    expected_injected=$(jq -r ".evals[$i].expected.injected[]" "$cases_file" 2>/dev/null || true)
    expected_not_injected=$(jq -r ".evals[$i].expected.not_injected[]" "$cases_file" 2>/dev/null || true)

    # Score each skill
    local nodejs_score python_score
    nodejs_score=$(match_skill "$PLUGIN_DIR/skills/nodejs-stack" "$signal_type" "$signal_value")
    python_score=$(match_skill "$PLUGIN_DIR/skills/python-stack" "$signal_type" "$signal_value")

    # Determine which would be injected (score > 0)
    local injected=()
    [[ "$nodejs_score" -gt 0 ]] && injected+=("nodejs-stack")
    [[ "$python_score" -gt 0 ]] && injected+=("python-stack")

    # Check expectations
    local case_passed=true
    local details=""

    # Check expected injected
    for exp in $expected_injected; do
      local found=false
      if (( ${#injected[@]} > 0 )); then
        for inj in "${injected[@]}"; do
          [[ "$inj" == "$exp" ]] && found=true
        done
      fi
      if ! $found; then
        case_passed=false
        details="$details MISS:$exp"
      fi
    done

    # Check not expected
    for nexp in $expected_not_injected; do
      if (( ${#injected[@]} > 0 )); then
        for inj in "${injected[@]}"; do
          if [[ "$inj" == "$nexp" ]]; then
            case_passed=false
            details="$details FALSE_POS:$nexp"
          fi
        done
      fi
    done

    total=$((total + 1))
    if $case_passed; then
      passed=$((passed + 1))
      printf "  ${GREEN}PASS${NC} %s (%s=%s) nodejs=%d python=%d\n" "$id" "$signal_type" "$signal_value" "$nodejs_score" "$python_score" >&2
    else
      failed=$((failed + 1))
      printf "  ${RED}FAIL${NC} %s (%s=%s) nodejs=%d python=%d %s\n" "$id" "$signal_type" "$signal_value" "$nodejs_score" "$python_score" "$details" >&2
    fi

    local inj_json
    if (( ${#injected[@]} > 0 )); then
      inj_json=$(printf '%s\n' "${injected[@]}" | jq -R 'select(length > 0)' | jq -s .)
    else
      inj_json="[]"
    fi
    results=$(echo "$results" | jq \
      --arg id "$id" \
      --argjson passed "$($case_passed && echo true || echo false)" \
      --argjson ns "$nodejs_score" \
      --argjson ps "$python_score" \
      --argjson inj "$inj_json" \
      '. + [{"id": $id, "passed": $passed, "nodejs_score": $ns, "python_score": $ps, "injected": $inj}]')
  done

  local accuracy
  if (( total > 0 )); then
    accuracy=$(awk "BEGIN {printf \"%.3f\", $passed / $total}")
  else
    accuracy="0.000"
  fi

  echo "$results" | jq --argjson t "$total" --argjson p "$passed" --arg a "$accuracy" \
    '{"total": $t, "passed": $p, "accuracy": ($a | tonumber), "cases": .}'
}

# =============================================================================
# RUN AGENT TRIGGERING TESTS (Tier 1 only)
# =============================================================================

run_agent_triggering_tests() {
  local cases_file="$EVALS_DIR/cases/agent-triggering.json"
  local total=0 passed=0 failed=0
  local results="[]"

  local count
  count=$(jq '.evals | length' "$cases_file")

  for i in $(seq 0 $((count - 1))); do
    local tier
    tier=$(jq -r ".evals[$i].tier" "$cases_file")
    [[ "$tier" != "1" ]] && continue  # Only tier 1 for static analysis

    local id prompt
    id=$(jq -r ".evals[$i].id" "$cases_file")
    prompt=$(jq -r ".evals[$i].prompt" "$cases_file")

    local expected_agents
    expected_agents=$(jq -r ".evals[$i].expected.agents[]" "$cases_file")
    local not_agents
    not_agents=$(jq -r ".evals[$i].expected.not_agents[]" "$cases_file" 2>/dev/null || true)

    # Find best matching agent
    local predicted
    predicted=$(find_best_agent "$prompt")

    # Check if predicted is in expected
    local case_passed=false
    for exp in $expected_agents; do
      [[ "$predicted" == "$exp" ]] && case_passed=true
    done

    # Also fail if predicted is in not_agents
    for nexp in $not_agents; do
      [[ "$predicted" == "$nexp" ]] && case_passed=false
    done

    total=$((total + 1))
    if $case_passed; then
      passed=$((passed + 1))
      printf "  ${GREEN}PASS${NC} %s → %s (expected: %s)\n" "$id" "$predicted" "$(echo $expected_agents | tr '\n' ',')" >&2
    else
      failed=$((failed + 1))
      printf "  ${RED}FAIL${NC} %s → %s (expected: %s)\n" "$id" "$predicted" "$(echo $expected_agents | tr '\n' ',')" >&2
    fi

    results=$(echo "$results" | jq \
      --arg id "$id" \
      --arg predicted "$predicted" \
      --arg expected "$(echo $expected_agents | tr '\n' ',')" \
      --argjson passed "$($case_passed && echo true || echo false)" \
      '. + [{"id": $id, "predicted": $predicted, "expected": $expected, "passed": $passed}]')
  done

  local accuracy
  if (( total > 0 )); then
    accuracy=$(awk "BEGIN {printf \"%.3f\", $passed / $total}")
  else
    accuracy="0.000"
  fi

  echo "$results" | jq --argjson t "$total" --argjson p "$passed" --arg a "$accuracy" \
    '{"total": $t, "passed": $p, "accuracy": ($a | tonumber), "cases": .}'
}

# =============================================================================
# MAIN
# =============================================================================

echo -e "${CYAN}=== dev-team Eval — Tier 1: Static Analysis ===${NC}"
echo ""

echo -e "${YELLOW}Skill Injection Tests${NC}"
si_results=$(run_skill_injection_tests)
echo ""

echo -e "${YELLOW}Agent Triggering Tests (Tier 1)${NC}"
at_results=$(run_agent_triggering_tests)
echo ""

# Aggregate
si_accuracy=$(echo "$si_results" | jq '.accuracy')
at_accuracy=$(echo "$at_results" | jq '.accuracy')
si_total=$(echo "$si_results" | jq '.total')
at_total=$(echo "$at_results" | jq '.total')
si_passed=$(echo "$si_results" | jq '.passed')
at_passed=$(echo "$at_results" | jq '.passed')

total=$((si_total + at_total))
total_passed=$((si_passed + at_passed))
if (( total > 0 )); then
  overall=$(awk "BEGIN {printf \"%.3f\", $total_passed / $total}")
else
  overall="0.000"
fi

# Write result
jq -n \
  --arg ts "$(date -Iseconds)" \
  --arg commit "$(cd "$PLUGIN_DIR" && git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" \
  --argjson si "$si_results" \
  --argjson at "$at_results" \
  --arg overall "$overall" \
  '{
    "timestamp": $ts,
    "tier": 1,
    "commit": $commit,
    "skill_injection": $si,
    "agent_triggering": $at,
    "summary": {
      "total": ($si.total + $at.total),
      "passed": ($si.passed + $at.passed),
      "accuracy": ($overall | tonumber),
      "api_calls": 0
    }
  }' > "$RESULT_FILE"

echo -e "${CYAN}=== Results ===${NC}"
echo -e "  Skill Injection:  ${si_passed}/${si_total} (${si_accuracy})"
echo -e "  Agent Triggering: ${at_passed}/${at_total} (${at_accuracy})"
echo -e "  Overall:          ${total_passed}/${total} (${overall})"
echo ""
echo -e "  Saved to: ${RESULT_FILE}"
