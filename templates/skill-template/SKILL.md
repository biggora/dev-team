---
# ==============================================================================
# SKILL TEMPLATE — Copy this directory and rename to create a new skill
# Directory: skills/<skill-name>/
# File: skills/<skill-name>/SKILL.md
# ==============================================================================
#
# Required fields:
#   name:        Skill display name
#   description: Third-person trigger description ("This skill should be used when...")
#                This is the ONLY triggering mechanism — Claude Code surfaces
#                skills to the model by description. Make it specific: name the
#                exact phrases, file types, and situations that should trigger it.
#
# Progressive disclosure:
#   SKILL.md    → Loaded when triggered (~1500-2000 words max)
#   references/ → Read by the agent on demand (detailed docs, patterns, examples)
# ==============================================================================

name: Skill Name Here
description: >
  This skill should be used when the user asks to
  "specific phrase 1", "specific phrase 2", "specific phrase 3",
  or needs guidance on [topic area].
---


<!-- TEMPLATE: Replace everything below with the skill content -->
<!-- Keep under 2000 words. Move detailed docs to references/ -->

# Skill Name Here

## Overview

Brief description of what this skill provides and when it applies.

**Key concepts:**
- [Concept 1]: [Brief explanation]
- [Concept 2]: [Brief explanation]

## Workflow

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Best Practices

- [Practice 1]
- [Practice 2]
- [Practice 3]

## Common Patterns

### Pattern 1: [Name]

**When to use**: [Conditions]

[Description and usage example]

### Pattern 2: [Name]

**When to use**: [Conditions]

[Description and usage example]

## Anti-Patterns

- [Anti-pattern 1]: [Why it's bad and what to do instead]
- [Anti-pattern 2]: [Why it's bad and what to do instead]

## Additional Resources

For detailed guidance, consult:
- **`references/patterns.md`** — Detailed pattern documentation
- **`references/examples.md`** — Working code examples
