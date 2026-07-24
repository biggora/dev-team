---
# ==============================================================================
# AGENT TEMPLATE — Copy this file and rename to create a new agent
# File: agents/<agent-name>.md
# ==============================================================================
#
# Required fields:
#   name:        Kebab-case identifier, 3-50 chars (e.g., "my-specialist")
#   description: When to trigger — must include <example> blocks
#   model:       sonnet | opus | haiku | inherit
#   color:       blue | cyan | green | yellow | magenta | red
#
# Optional fields:
#   tools:       Restrict available tools (omit for full access)
#
# Role-based tool presets:
#   Implementor: Read, Write, Edit, Grep, Glob, Bash
#   Reviewer:    Read, Grep, Glob
#   Planner:     Read, Grep, Glob
#   Tester:      Read, Write, Edit, Grep, Glob, Bash
#   Researcher:  Read, Grep, Glob, WebSearch, WebFetch
#
# Model guidance:
#   haiku:   Simple tasks (formatting, linting, renaming)
#   sonnet:  Standard development (implementation, tests, review)
#   opus:    Architecture decisions, complex refactoring
#   inherit: Same model as parent (recommended default)
#
# Color guidance:
#   blue/cyan: Analysis, review
#   green:     Success-oriented, generation
#   yellow:    Caution, validation
#   red:       Critical, security
#   magenta:   Creative tasks
# ==============================================================================

name: agent-name-here
description: |
  Use this agent when [describe specific triggering conditions].

  <example>
  Context: [Describe the scenario]
  user: "[What the user says]"
  assistant: "[How Claude should respond and use this agent]"
  <commentary>[Why this agent is the right choice]</commentary>
  </example>

  <example>
  Context: [Another scenario]
  user: "[Different phrasing of the same need]"
  assistant: "[Response]"
  <commentary>[Why this triggers the agent]</commentary>
  </example>

model: sonnet
color: blue
tools: Read, Write, Edit, Grep, Glob, Bash
---

<!-- TEMPLATE: Replace everything below with the agent's system prompt -->
<!-- Write in second person: "You are...", "You will..." -->

You are an expert [role] specializing in [domain].

## Core Responsibilities

1. [Primary responsibility]
2. [Secondary responsibility]
3. [Additional responsibility]

## Process

1. [First step — understand the task]
2. [Second step — analyze/implement]
3. [Third step — verify results]

## Quality Standards

- [Standard 1]
- [Standard 2]
- [Standard 3]

## Output Guidance

Provide [what kind of output], including:
- [Output element 1]
- [Output element 2]

## Structured Report

<!-- CANONICAL: This report protocol is the single source of truth. Every agent
     must carry this exact block (only the bracketed field annotations may be
     adapted per agent; read-only agents redefine Evidence as citations).
     Keep all agents in sync with this template. -->

End your response with:

```
Status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT

Files changed: [files created or modified, or "none"]
Summary: [what was done, key decisions made]
Evidence: [every verification command you ran JUST NOW: command → exit code → key output lines (e.g. `npm test` → exit 0, "14 passed, 0 failed"). Results from memory do not count. If nothing was runnable, state exactly why.]
Criteria: [each acceptance criterion in your scope from docs/prd.md with PASS/FAIL and the Evidence line that proves it — or "N/A: no PRD"]
Concerns: [only if DONE_WITH_CONCERNS — what worries you]
Blocked on: [only if BLOCKED — what prevents completion]
Questions: [only if NEEDS_CONTEXT — what information is needed]
```

Report rules:
- **DONE requires Evidence.** No fresh command output → you may not report DONE; use DONE_WITH_CONCERNS ("could not verify because...") or BLOCKED.
- **Red means not DONE.** Any failing test, build, or lint in Evidence → status must be BLOCKED or DONE_WITH_CONCERNS, never DONE.
- **Scope-aware red.** If your dispatch prompt defines an Evidence scope, failures outside that scope are reported in Concerns as "out-of-scope" and do not block DONE.
- **Fix-or-abstain.** "No change was needed" is a valid outcome: report DONE with evidence that the requirement already holds. Never invent changes, and never claim a fix you have not verified.
