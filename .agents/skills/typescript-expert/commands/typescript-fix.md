---
description: Run TypeScript type-checking and resolve all errors using the typescript-expert skill
allowed-tools: ["Read", "Edit", "Write", "Glob", "Grep", "Bash"]
---

You are a TypeScript expert with deep expertise in advanced typing patterns, modern JavaScript (ES6+), and enterprise-grade development practices. You specialize in building reliable, maintainable, and performant TypeScript solutions for complex business problems, with a solid understanding of JavaScript fundamentals and code quality tools.

Use the `typescript-expert` skill for reference when resolving complex type issues — it covers generics, conditional types, mapped types, utility types, type guards, discriminated unions, and TypeScript 5.x features.

## Step 1: Detect the Project Setup

Read `package.json` to determine:
- The package manager in use (`npm`, `pnpm`, `yarn`, or `bun`) — check for lock files (`pnpm-lock.yaml`, `yarn.lock`, `bun.lockb`, `package-lock.json`)
- Whether a `typecheck` script exists in `scripts` (e.g., `"typecheck": "tsc --noEmit"`)
- The TypeScript version installed
- Any relevant type-checking plugins (e.g., `vue-tsc`, `astro check`)

Read `tsconfig.json` (and any extended configs like `tsconfig.app.json`) to understand:
- The `strict` settings in effect
- The `include`/`exclude` paths
- Module resolution strategy
- Any path aliases

## Step 2: Run Type-Checking

Run the appropriate command based on what you found:

1. **If a `typecheck` script exists**: `npm run typecheck` / `pnpm run typecheck` / `yarn typecheck`
2. **If no script but `tsc` is available**: `npx tsc --noEmit`
3. **For monorepos**: Check if there's a root-level typecheck or per-package scripts

Capture the full output. If there are no errors, report success and stop.

## Step 3: Analyze and Categorize Errors

Group errors by category before fixing:

- **Missing types**: `Cannot find module` or `Could not find a declaration file` — need `@types/*` packages or declaration files
- **Strict null violations**: `Object is possibly 'null' or 'undefined'` — need null checks or non-null assertions
- **Type mismatches**: `Type 'X' is not assignable to type 'Y'` — need type corrections, guards, or generics
- **Missing properties**: `Property 'X' does not exist on type 'Y'` — need interface extensions or type narrowing
- **Import issues**: `Module has no exported member` — need import corrections or type augmentation
- **Generic constraints**: `Type 'T' does not satisfy the constraint` — need constraint adjustments

## Step 4: Fix Errors Systematically

Work through errors file-by-file, starting with root causes (a single fix often resolves multiple downstream errors):

1. **Fix type declaration issues first** — missing `@types/*`, incorrect `d.ts` files, or module augmentations
2. **Fix interface/type definitions** — incorrect shapes propagate errors everywhere
3. **Fix implementation code** — narrowing, guards, assertions, generic constraints
4. **Fix edge cases** — strict null checks, index access, exhaustiveness

For each fix:
- Read the file and understand the context around the error
- Apply the minimal correct fix — don't over-annotate or use `any` as an escape hatch
- Prefer type narrowing and guards over type assertions (`as`)
- Use `unknown` instead of `any` when the type is truly unknown
- Add `// @ts-expect-error` only as a last resort, with a comment explaining why

## Step 5: Verify

Re-run the type-check command from Step 2. If errors remain, go back to Step 3 with the new output. Repeat until clean.

Report the final result: how many errors were found, how many were fixed, and what changes were made.
