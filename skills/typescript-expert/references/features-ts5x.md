# TypeScript 5.x Features

A comprehensive guide to features added in TypeScript 5.0 through 5.8.

## TypeScript 5.0

### TC39 Decorators

Standard decorators without `experimentalDecorators`. See [advanced-decorators](advanced-decorators.md) for full details.

```typescript
function log(target: Function, context: ClassMethodDecoratorContext) {
  return function (...args: any[]) {
    console.log(`Calling ${String(context.name)}`);
    return target.apply(this, args);
  };
}

class Api {
  @log
  fetchData() { ... }
}
```

### `const` Type Parameters

Add `const` modifier to type parameters for const-like inference:

```typescript
function createConfig<const T extends Record<string, unknown>>(config: T): T {
  return config;
}

// Infers literal types without 'as const' at call site
const config = createConfig({
  env: "production",
  port: 3000,
  features: ["auth", "logging"],
});
// Type: { readonly env: "production"; readonly port: 3000; readonly features: readonly ["auth", "logging"] }
```

### `--verbatimModuleSyntax`

Forces explicit `type` annotations on type-only imports/exports:

```typescript
import type { User } from "./models";       // Erased
import { type Role, createUser } from "./models"; // Role erased, createUser kept
export type { User };                        // Erased
```

Replaces the older `importsNotUsedAsValues` and `preserveValueImports` flags.

### `export type *`

Re-export all types from a module as type-only:

```typescript
export type * from "./internal-types";
export type * as models from "./models";
```

### Bundler Module Resolution

`"moduleResolution": "bundler"` — use when a bundler handles resolution:

```jsonc
{
  "compilerOptions": {
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true // Optional: allow .ts imports
  }
}
```

## TypeScript 5.1

### Easier Implicit Returns for `undefined`

Functions returning `undefined` no longer need an explicit `return` statement:

```typescript
// Before 5.1: needed 'return;' or 'return undefined;'
function logMessage(msg: string): undefined {
  console.log(msg);
  // No return needed — implicitly returns undefined
}
```

### Unrelated Types for Getters and Setters

Getters and setters can have different types:

```typescript
class State {
  #value: number = 0;

  get value(): number {
    return this.#value;
  }

  set value(input: string | number) {
    this.#value = typeof input === "string" ? parseInt(input) : input;
  }
}

const s = new State();
s.value = "42";    // Setter accepts string | number
const n = s.value; // Getter returns number
```

### JSX Improvements

Support for different JSX element types per-tag. Enables React Server Components to be typed differently from client components.

## TypeScript 5.2

### `using` Declarations (Explicit Resource Management)

Deterministic cleanup with `Symbol.dispose` and `Symbol.asyncDispose`:

```typescript
class TempFile implements Disposable {
  #path: string;

  constructor(path: string) {
    this.#path = path;
    writeFileSync(path, "");
  }

  write(data: string) {
    appendFileSync(this.#path, data);
  }

  [Symbol.dispose]() {
    unlinkSync(this.#path);
    console.log(`Cleaned up ${this.#path}`);
  }
}

function processData() {
  using file = new TempFile("/tmp/data.txt");
  file.write("processing...");
  // file is automatically disposed when scope exits
  // Even if an exception is thrown
}

// Async version
class DatabaseConnection implements AsyncDisposable {
  async [Symbol.asyncDispose]() {
    await this.close();
  }
}

async function query() {
  await using conn = await connect();
  return await conn.query("SELECT ...");
  // conn.close() called automatically
}
```

### Decorator Metadata

Access shared metadata object from decorator context:

```typescript
function route(path: string) {
  return (target: any, context: ClassMethodDecoratorContext) => {
    context.metadata[String(context.name)] = { path };
  };
}

class Controller {
  @route("/users")
  getUsers() { ... }
}

const meta = Controller[Symbol.metadata];
// { getUsers: { path: "/users" } }
```

## TypeScript 5.3

### `import` Attributes

```typescript
import data from "./data.json" with { type: "json" };
import styles from "./styles.css" with { type: "css" };
```

### `switch (true)` Narrowing

TypeScript now properly narrows types in `switch (true)` patterns:

```typescript
function process(value: string | number | boolean) {
  switch (true) {
    case typeof value === "string":
      value.toUpperCase(); // value is string
      break;
    case typeof value === "number":
      value.toFixed(2);    // value is number
      break;
  }
}
```

## TypeScript 5.4

### `NoInfer<T>` Utility Type

Prevents a position from contributing to type inference:

```typescript
function createStreetLight<C extends string>(
  colors: C[],
  defaultColor?: NoInfer<C>
) { ... }

createStreetLight(["red", "yellow", "green"], "blue");
// Error! "blue" not in "red" | "yellow" | "green"
// Without NoInfer, C would widen to include "blue"
```

### Closure Narrowing in `Array.isArray`

```typescript
function process(value: string | string[]) {
  if (Array.isArray(value)) {
    value.map(s => s.toUpperCase()); // value is string[]
  }
}
```

## TypeScript 5.5

### Inferred Type Predicates

TypeScript can now infer type guard return types:

```typescript
// Before: needed explicit annotation
function isString(x: unknown): x is string {
  return typeof x === "string";
}

// TS 5.5: inferred automatically for simple cases
const isString = (x: unknown) => typeof x === "string";
// Return type inferred as: x is string

// filter(Boolean) just works now
const items = [1, null, 2, undefined, 3];
const numbers = items.filter(Boolean); // number[]
// Previously: (number | null | undefined)[]
```

### Regular Expression Syntax Checking

TypeScript now validates regex syntax at the type level:

```typescript
const re = /\p{Letter}/u; // OK
const bad = /[/;           // Error: Unterminated character class
```

## TypeScript 5.6

### Iterator Helper Methods

Built-in iterator methods like `.map()`, `.filter()`, `.take()`:

```typescript
function* naturals() {
  let n = 0;
  while (true) yield n++;
}

const evens = naturals()
  .filter(n => n % 2 === 0)
  .take(5)
  .toArray();
// [0, 2, 4, 6, 8]

// Works with any Iterable
const map = new Map([["a", 1], ["b", 2]]);
const keys = map.keys().filter(k => k !== "a").toArray();
// ["b"]
```

### Disallowed Nullish and Truthy Checks

```typescript
// New errors for always-truthy or always-nullish comparisons
function process(x: string) {
  if (x) { }          // OK — string can be falsy ("")
}

function process(x: () => void) {
  if (x) { }          // Error! Function is always truthy — did you mean x()?
}
```

## TypeScript 5.7

### `--squash` for Project References

Faster `--build` by squashing intermediate outputs.

### Relative Path Rewriting in Declaration Files

Declaration files now preserve relative path structure, improving monorepo support.

### Initialized `Symbol.dispose` in `using` Declarations

```typescript
using _ = {
  [Symbol.dispose]() {
    console.log("cleanup");
  }
};
```

## TypeScript 5.8

### `--erasableSyntaxOnly`

Ensures only erasable TypeScript syntax is used — no enums, namespaces, or parameter properties:

```jsonc
{
  "compilerOptions": {
    "erasableSyntaxOnly": true
  }
}
```

This flag is designed for use with Node.js `--strip-types` (Node 22.6+), which strips TypeScript annotations but doesn't transform:

```typescript
// Allowed: type annotations are erasable
const x: string = "hello";
function greet(name: string): void { }

// Disallowed: these need transformation, not just erasure
enum Color { Red, Green, Blue }          // Error
namespace Foo { export const x = 1; }    // Error
class C { constructor(public x: number) {} } // Error (parameter property)
```

### Granular Checks on Branches in Return Expressions

TypeScript 5.8 checks individual branches of ternary expressions against the return type:

```typescript
function process(value: string | null): string {
  return value ?? 42;
  // Error on 42 specifically — previous versions gave a less helpful error
}
```

## Migration Tips

When upgrading TypeScript versions:

1. **Read the release notes** — each version has breaking changes
2. **Update `@types/*` packages** — they often need matching versions
3. **Run `tsc --noEmit` first** — check for new errors before building
4. **Enable new strict flags gradually** — add one at a time
5. **Use `// @ts-expect-error`** — for known issues you'll fix later (not `@ts-ignore`)
