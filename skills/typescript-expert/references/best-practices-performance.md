# Type-Level Performance

When TypeScript becomes slow, it's usually because complex types cause the compiler to do excessive work. This guide covers how to diagnose and fix type-level performance issues.

## Diagnosing Slow Types

### Compiler Flags for Profiling

```bash
# Generate a trace for analysis
tsc --generateTrace ./trace-output

# Show time spent on each file
tsc --extendedDiagnostics

# Show which types are being checked
tsc --listFiles
```

The trace output can be loaded in Chrome DevTools (Performance tab) or `@typescript/analyze-trace`:

```bash
npx @typescript/analyze-trace ./trace-output
```

### Common Symptoms

- IDE autocompletion is slow or laggy
- `tsc` takes significantly longer than expected
- Hover types show `...` (type too complex to display)
- "Type instantiation is excessively deep" errors

## Rules for Fast Types

### 1. Prefer Interfaces Over Intersections

```typescript
// Slower — creates anonymous intersection each time
type User = BaseEntity & { name: string; email: string };

// Faster — interfaces are cached by name
interface User extends BaseEntity {
  name: string;
  email: string;
}
```

Interfaces are cached by identity. Intersections create new anonymous types on every use.

### 2. Limit Union Size

Unions beyond ~25-50 members start impacting performance. Large unions from template literals are a common cause:

```typescript
// This creates a union of 10,000 members — very slow
type Color = `#${HexDigit}${HexDigit}${HexDigit}${HexDigit}${HexDigit}${HexDigit}`;

// Better: use a branded string
type Color = string & { readonly __brand: "Color" };
```

### 3. Avoid Deep Recursive Types

```typescript
// Slow — recursion depth grows with path length
type DeepGet<T, Path extends string> =
  Path extends `${infer Head}.${infer Tail}`
    ? Head extends keyof T
      ? DeepGet<T[Head], Tail>
      : never
    : Path extends keyof T
      ? T[Path]
      : never;

// If this is slow, consider:
// 1. Limiting recursion depth with a counter
// 2. Using a simpler type and casting at the boundary
// 3. Moving the logic to runtime validation
```

### Tail-Call Optimization for Recursive Types

TypeScript optimizes tail-position conditional types. Structure recursion to be tail-recursive:

```typescript
// Not tail-recursive — wraps result before returning
type BadReverse<T extends any[]> =
  T extends [infer Head, ...infer Tail]
    ? [...BadReverse<Tail>, Head]
    : [];

// Tail-recursive — accumulator pattern
type Reverse<T extends any[], Acc extends any[] = []> =
  T extends [infer Head, ...infer Tail]
    ? Reverse<Tail, [Head, ...Acc]>
    : Acc;
```

### 4. Use `skipLibCheck: true`

Skip type-checking `.d.ts` files from `node_modules`. This dramatically speeds up compilation:

```jsonc
{
  "compilerOptions": {
    "skipLibCheck": true
  }
}
```

### 5. Use Project References for Monorepos

Break large codebases into smaller projects with `composite` and project references. This enables incremental compilation:

```bash
tsc --build --incremental
```

### 6. Avoid Conditional Types in Hot Paths

Conditional types that TypeScript can't resolve eagerly (because they involve generic parameters) stay deferred and get re-evaluated at every use site:

```typescript
// This stays deferred inside generic functions — expensive
function process<T>(value: T): T extends string ? number : boolean {
  // ...
}

// Better: use overloads for finite cases
function process(value: string): number;
function process(value: number): boolean;
function process(value: string | number): number | boolean {
  // ...
}
```

### 7. Simplify Mapped Types

```typescript
// Slow — maps, remaps, and conditionally transforms every key
type Complex<T> = {
  [K in keyof T as T[K] extends Function
    ? `handle${Capitalize<string & K>}`
    : K
  ]: T[K] extends Function
    ? (...args: Parameters<T[K]>) => Promise<ReturnType<T[K]>>
    : Readonly<T[K]>;
};

// Faster — split into smaller, composable types
type Methods<T> = {
  [K in keyof T as T[K] extends Function ? K : never]: T[K];
};
type Data<T> = {
  [K in keyof T as T[K] extends Function ? never : K]: Readonly<T[K]>;
};
type AsyncMethods<T> = {
  [K in keyof T]: T[K] extends (...args: infer A) => infer R
    ? (...args: A) => Promise<R>
    : never;
};
```

## When to Give Up on Types

Sometimes the cost of perfect types outweighs the benefit:

1. **Cast at the boundary**: Type complex external data at the edges and trust it internally
2. **Use `as` strategically**: A well-placed assertion is better than a deep recursive type
3. **Simplify to branded strings/numbers**: When template literal types create too many members
4. **Use `// @ts-expect-error`**: For known type system limitations (with a comment explaining why)

The goal is to catch real bugs, not to prove theorems. If a type takes 500ms to check and catches a bug once a year, simplify it.

## Quick Performance Checklist

- [ ] `strict: true` (catches bugs without complex types)
- [ ] `skipLibCheck: true` (skip `.d.ts` checking)
- [ ] `incremental: true` (cache between builds)
- [ ] Interfaces over intersections for object types
- [ ] Union types under ~50 members
- [ ] Recursive types use accumulator pattern
- [ ] No deeply nested conditional types in generic functions
- [ ] Project references for monorepos
- [ ] `--generateTrace` if still slow — find the hotspot
