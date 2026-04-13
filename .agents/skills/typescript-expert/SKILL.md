---
name: typescript-expert
description: TypeScript language expertise covering the type system, generics, utility types, advanced type patterns, and project configuration. Use this skill whenever writing, reviewing, or refactoring TypeScript code, designing type-safe APIs, working with complex generics, debugging type errors, configuring tsconfig.json, migrating JavaScript to TypeScript, or leveraging TypeScript 5.x features like satisfies, const type parameters, decorators, and the using keyword. Also use when the user asks about type narrowing, conditional types, mapped types, template literal types, branded types, discriminated unions, or any TypeScript type system question — even seemingly simple ones, because TypeScript's type system has subtle gotchas that catch experienced developers.
---

# TypeScript Expert

> Covers TypeScript through 5.8 (latest stable as of March 2026). The official handbook at https://www.typescriptlang.org/docs/handbook/ is the canonical reference.

TypeScript is a typed superset of JavaScript that compiles to plain JavaScript. Its type system is structural (not nominal), meaning type compatibility is determined by shape rather than declaration. This has profound implications for how you design types and APIs.

## Quick Decision Guide

| You need to... | Read |
|----------------|------|
| Understand primitives, inference, narrowing | [core-type-system](references/core-type-system.md) |
| Choose between `interface` and `type` | [core-interfaces-types](references/core-interfaces-types.md) |
| Write generic functions, classes, constraints | [core-generics](references/core-generics.md) |
| Use `Partial`, `Pick`, `Omit`, `Record`, etc. | [core-utility-types](references/core-utility-types.md) |
| Build conditional types with `infer` | [advanced-conditional-types](references/advanced-conditional-types.md) |
| Create mapped types and key remapping | [advanced-mapped-types](references/advanced-mapped-types.md) |
| Use template literal types for string patterns | [advanced-template-literals](references/advanced-template-literals.md) |
| Narrow types with guards and discriminated unions | [advanced-type-guards](references/advanced-type-guards.md) |
| Use TC39 decorators (TS 5.0+) | [advanced-decorators](references/advanced-decorators.md) |
| Configure `tsconfig.json` properly | [best-practices-tsconfig](references/best-practices-tsconfig.md) |
| Apply common patterns (branded types, error handling, immutability) | [best-practices-patterns](references/best-practices-patterns.md) |
| Optimize type-level performance | [best-practices-performance](references/best-practices-performance.md) |
| Use TS 5.0-5.8 features (`satisfies`, `const` params, `using`) | [features-ts5x](references/features-ts5x.md) |

## Core Principles

### 1. Let TypeScript Infer

TypeScript's inference is powerful. Don't annotate what TypeScript can figure out on its own:

```typescript
// Unnecessary — TypeScript infers `number`
const count: number = 5;

// Good — let inference work
const count = 5;

// DO annotate function signatures (parameters + return types for public APIs)
function getUser(id: string): Promise<User> { ... }

// Return type annotation catches accidental returns
function parse(input: string): ParseResult {
  if (!input) return null; // Error! null isn't ParseResult — good, we caught a bug
}
```

### 2. Prefer `unknown` over `any`

`any` disables type checking. `unknown` is type-safe — you must narrow it before use:

```typescript
// Bad — silently breaks type safety
function process(data: any) {
  data.foo.bar; // No error, but might crash at runtime
}

// Good — forces you to check before using
function process(data: unknown) {
  if (typeof data === "object" && data !== null && "foo" in data) {
    // Now TypeScript knows data has a foo property
  }
}
```

### 3. Use Strict Mode

Always enable `"strict": true` in tsconfig.json. It enables all strict type-checking flags including `strictNullChecks`, `noImplicitAny`, and `strictFunctionTypes`. Projects that skip strict mode accumulate hidden bugs that surface painfully later. See [best-practices-tsconfig](references/best-practices-tsconfig.md) for the full recommended configuration.

### 4. Model Your Domain with Types

The type system is a tool for encoding business rules. Use discriminated unions to model states, branded types for domain identifiers, and `readonly` to enforce immutability:

```typescript
// Model states explicitly — impossible to access data in loading/error state
type AsyncState<T> =
  | { status: "loading" }
  | { status: "error"; error: Error }
  | { status: "success"; data: T };

// Branded types prevent ID mixups at compile time
type UserId = string & { readonly __brand: "UserId" };
type OrderId = string & { readonly __brand: "OrderId" };

function getOrder(orderId: OrderId): Order { ... }
getOrder(userId); // Error! UserId is not assignable to OrderId
```

### 5. Structural Typing Implications

TypeScript uses structural typing — if two types have the same shape, they're compatible:

```typescript
interface Point { x: number; y: number }
interface Coordinate { x: number; y: number }

const p: Point = { x: 1, y: 2 };
const c: Coordinate = p; // OK — same shape

// This means excess property checks only apply to object literals
function plot(point: Point) { ... }
plot({ x: 1, y: 2, z: 3 }); // Error — excess property check on literal
const obj = { x: 1, y: 2, z: 3 };
plot(obj); // OK — no excess check on variable
```

## Common Gotchas

| Gotcha | Explanation |
|--------|-------------|
| `object` vs `Object` vs `{}` | Use `object` for non-primitives. Never use `Object` or `{}` as types — `{}` matches everything except `null`/`undefined`. |
| `T[]` vs `readonly T[]` | Arrays are mutable by default. Use `readonly T[]` or `ReadonlyArray<T>` when mutation isn't intended. |
| `enum` vs union | Prefer union types (`type Dir = "N" \| "S" \| "E" \| "W"`) over enums. Enums produce runtime code and have subtle nominal typing behavior. Use `as const` objects if you need runtime values. |
| Optional vs `undefined` | `{ x?: number }` means x may be missing entirely. `{ x: number \| undefined }` means x must be present but can be undefined. These behave differently with `in` checks and spread. |
| `as` casts | Type assertions (`as`) override the compiler. Prefer type guards for runtime narrowing. Use `as` only when you genuinely know more than TypeScript. |
| `any` propagation | A single `any` silently infects surrounding types. Use `unknown` and narrow, or use `// @ts-expect-error` for known edge cases. |

## TypeScript 5.x Highlights

Key features added in TypeScript 5.0-5.8 (see [features-ts5x](references/features-ts5x.md) for details):

| Version | Feature | Why it matters |
|---------|---------|----------------|
| 5.0 | TC39 Decorators | Standard decorator syntax, no `experimentalDecorators` needed |
| 5.0 | `const` type parameters | `<const T>` gives const-like inference without `as const` at call site |
| 5.1 | Easier implicit returns | `undefined`-returning functions can omit `return` |
| 5.2 | `using` declarations | Deterministic resource cleanup (like C# `using` / Python `with`) |
| 5.4 | `NoInfer<T>` | Prevents unwanted inference from specific positions |
| 5.5 | Inferred type predicates | `filter(Boolean)` and arrow guards just work |
| 5.6 | Iterator helper methods | `.map()`, `.filter()`, `.take()` on iterators |
| 5.7 | `--squash` for project refs | Faster composite project builds |
| 5.8 | `--erasableSyntaxOnly` | Strip types without full compilation (Node.js `--strip-types` support) |

## When to Read the References

- **Writing a new module/library**: Read [core-generics](references/core-generics.md) and [best-practices-patterns](references/best-practices-patterns.md)
- **Debugging a confusing type error**: Read [advanced-type-guards](references/advanced-type-guards.md) and [core-type-system](references/core-type-system.md)
- **Designing a type-safe API**: Read [advanced-conditional-types](references/advanced-conditional-types.md) and [advanced-mapped-types](references/advanced-mapped-types.md)
- **Setting up a new project**: Read [best-practices-tsconfig](references/best-practices-tsconfig.md)
- **Migrating from JS or older TS**: Read [features-ts5x](references/features-ts5x.md) and [best-practices-tsconfig](references/best-practices-tsconfig.md)
- **Performance issues with types**: Read [best-practices-performance](references/best-practices-performance.md)
