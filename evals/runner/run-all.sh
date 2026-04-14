#!/bin/bash
# =============================================================================
# dev-team Eval — Run all tiers and aggregate results
# Usage: bash run-all.sh [--skip-tier2] [--skip-tier3] [--save-baseline]
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVALS_DIR="$(dirname "$SCRIPT_DIR")"
PLUGIN_DIR="$(dirname "$EVALS_DIR")"
RESULTS_DIR="$EVALS_DIR/results"
BASELINE_FILE="$RESULTS_DIR/baseline.json"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

SKIP_TIER2=false
SKIP_TIER3=false
SAVE_BASELINE=false

for arg in "$@"; do
  case "$arg" in
    --skip-tier2) SKIP_TIER2=true ;;
    --skip-tier3) SKIP_TIER3=true ;;
    --save-baseline) SAVE_BASELINE=true ;;
  esac
done

echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${CYAN}║     dev-team Eval Framework v1.0         ║${NC}"
echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════╝${NC}"
echo ""

# Load scoring weights
WEIGHT_AT=$(jq '.scoring_weights.agent_triggering' "$EVALS_DIR/config.json")
WEIGHT_SI=$(jq '.scoring_weights.skill_injection' "$EVALS_DIR/config.json")
WEIGHT_CD=$(jq '.scoring_weights.coordinator_dispatch' "$EVALS_DIR/config.json")

# =============================================================================
# Tier 1 (always runs)
# =============================================================================
echo -e "${BOLD}--- Tier 1: Static Analysis (0 API calls) ---${NC}"
bash "$SCRIPT_DIR/run-tier1.sh"
TIER1_FILE=$(ls -t "$RESULTS_DIR"/tier1-*.json 2>/dev/null | head -1)
TIER1_ACCURACY=$(jq '.summary.accuracy' "$TIER1_FILE")
SI_ACCURACY=$(jq '.skill_injection.accuracy' "$TIER1_FILE")
AT_ACCURACY_T1=$(jq '.agent_triggering.accuracy' "$TIER1_FILE")
echo ""

# =============================================================================
# Tier 2 (optional)
# =============================================================================
TIER2_ACCURACY="null"
AT_ACCURACY_T2="null"
CD_ACCURACY_T2="null"
if ! $SKIP_TIER2; then
  echo -e "${BOLD}--- Tier 2: Single-Agent Dispatch ---${NC}"
  bash "$SCRIPT_DIR/run-tier2.sh"
  TIER2_FILE=$(ls -t "$RESULTS_DIR"/tier2-*.json 2>/dev/null | head -1)
  if [[ -n "$TIER2_FILE" ]]; then
    TIER2_ACCURACY=$(jq '.summary.accuracy' "$TIER2_FILE")
  fi
  echo ""
else
  echo -e "${YELLOW}Skipping Tier 2 (--skip-tier2)${NC}"
  echo ""
fi

# =============================================================================
# Tier 3 (optional)
# =============================================================================
TIER3_ACCURACY="null"
if ! $SKIP_TIER3; then
  echo -e "${BOLD}--- Tier 3: Full Coordinator Flow ---${NC}"
  bash "$SCRIPT_DIR/run-tier3.sh"
  TIER3_FILE=$(ls -t "$RESULTS_DIR"/tier3-*.json 2>/dev/null | head -1)
  if [[ -n "$TIER3_FILE" ]]; then
    TIER3_ACCURACY=$(jq '.summary.accuracy' "$TIER3_FILE")
  fi
  echo ""
else
  echo -e "${YELLOW}Skipping Tier 3 (--skip-tier3)${NC}"
  echo ""
fi

# =============================================================================
# Aggregate
# =============================================================================

# Compute category scores (use best available tier)
# Agent triggering: combine Tier 1 + Tier 2
if [[ "$TIER2_ACCURACY" != "null" ]]; then
  AT_SCORE=$(awk "BEGIN {printf \"%.3f\", $AT_ACCURACY_T1 * 0.4 + $TIER2_ACCURACY * 0.6}")
else
  AT_SCORE="$AT_ACCURACY_T1"
fi

# Skill injection: Tier 1 only
SI_SCORE="$SI_ACCURACY"

# Coordinator dispatch: Tier 2 + Tier 3
if [[ "$TIER3_ACCURACY" != "null" && "$TIER2_ACCURACY" != "null" ]]; then
  CD_SCORE=$(awk "BEGIN {printf \"%.3f\", $TIER2_ACCURACY * 0.5 + $TIER3_ACCURACY * 0.5}")
elif [[ "$TIER2_ACCURACY" != "null" ]]; then
  CD_SCORE="$TIER2_ACCURACY"
else
  CD_SCORE="0.000"
fi

TOTAL_SCORE=$(awk "BEGIN {printf \"%.3f\", $WEIGHT_AT * $AT_SCORE + $WEIGHT_SI * $SI_SCORE + $WEIGHT_CD * $CD_SCORE}")

# Compare with baseline
BASELINE_DIFF=""
GATES_PASSED=true
if [[ -f "$BASELINE_FILE" ]]; then
  BASELINE_SCORE=$(jq '.total_score' "$BASELINE_FILE")
  DIFF=$(awk "BEGIN {if ($BASELINE_SCORE > 0) printf \"%.1f\", ($TOTAL_SCORE - $BASELINE_SCORE) * 100 / $BASELINE_SCORE; else print \"0.0\"}")
  BASELINE_DIFF=" (${DIFF}% vs baseline)"

  # Hard gate: must not degrade
  MIN_GATE=$(jq '.hard_gates.min_accuracy_vs_baseline' "$EVALS_DIR/config.json")
  if awk "BEGIN {exit !($TOTAL_SCORE < $BASELINE_SCORE + $MIN_GATE)}"; then
    GATES_PASSED=false
  fi
fi

# =============================================================================
# Report
# =============================================================================

echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${CYAN}║          EVAL REPORT                     ║${NC}"
echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Plugin:  @biggora/dev-team"
echo -e "  Commit:  $(cd "$PLUGIN_DIR" && git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"
echo -e "  Date:    $(date +%Y-%m-%d)"
echo ""
echo -e "  ${BOLD}Tier 1 (Static):${NC}  ${TIER1_ACCURACY}"
[[ "$TIER2_ACCURACY" != "null" ]] && echo -e "  ${BOLD}Tier 2 (Single):${NC}  ${TIER2_ACCURACY}"
[[ "$TIER3_ACCURACY" != "null" ]] && echo -e "  ${BOLD}Tier 3 (Full):${NC}    ${TIER3_ACCURACY}"
echo ""
echo -e "  ${BOLD}Agent Triggering:${NC}      ${AT_SCORE}  (weight: ${WEIGHT_AT})"
echo -e "  ${BOLD}Skill Injection:${NC}       ${SI_SCORE}  (weight: ${WEIGHT_SI})"
echo -e "  ${BOLD}Coordinator Dispatch:${NC}  ${CD_SCORE}  (weight: ${WEIGHT_CD})"
echo ""
echo -e "  ${BOLD}Total Score: ${TOTAL_SCORE}${BASELINE_DIFF}${NC}"
echo ""

if $GATES_PASSED; then
  echo -e "  Hard Gates: ${GREEN}ALL PASSED${NC}"
else
  echo -e "  Hard Gates: ${RED}FAILED — score below baseline${NC}"
fi

# Save aggregate result
AGGREGATE_FILE="$RESULTS_DIR/aggregate-$(date +%Y%m%d-%H%M%S).json"
jq -n \
  --arg ts "$(date -Iseconds)" \
  --arg commit "$(cd "$PLUGIN_DIR" && git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" \
  --arg at "$AT_SCORE" \
  --arg si "$SI_SCORE" \
  --arg cd "$CD_SCORE" \
  --arg total "$TOTAL_SCORE" \
  --argjson gates "$($GATES_PASSED && echo true || echo false)" \
  '{
    "timestamp": $ts,
    "commit": $commit,
    "categories": {
      "agent_triggering": ($at | tonumber),
      "skill_injection": ($si | tonumber),
      "coordinator_dispatch": ($cd | tonumber)
    },
    "total_score": ($total | tonumber),
    "hard_gates_passed": $gates
  }' > "$AGGREGATE_FILE"

# Save as baseline if requested
if $SAVE_BASELINE; then
  cp "$AGGREGATE_FILE" "$BASELINE_FILE"
  echo ""
  echo -e "  ${GREEN}Saved as baseline: $BASELINE_FILE${NC}"
fi

echo ""
echo -e "  Saved to: $AGGREGATE_FILE"
