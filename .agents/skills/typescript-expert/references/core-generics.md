# Generics

Generics enable writing reusable, type-safe code that works with multiple types while preserving type information through the call chain.

## Basic Generic Functions

```typescript
// Without generics — loses type information
function firstElement(arr: any[]): any {
  return arr[0];
}

// With generics — preserves the type
function firstElement<T>(arr: T[]): T | undefined {
  return arr[0];
}

const n = firstElement([1, 2, 3]);    // number | undefined
const s = firstElement(["a", "b"]);    // string | undefined
```

TypeScript infers the type argument from the argument you pass. You rarely need to specify it explicitly:

```typescript
// Explicit (rarely needed)
firstElement<string>(["a", "b"]);

// Implicit (preferred — let inference work)
firstElement(["a", "b"]);
```

## Multiple Type Parameters

```typescript
function map<T, U>(arr: T[], fn: (item: T) => U): U[] {
  return arr.map(fn);
}

const lengths = map(["hello", "world"], s => s.length);
// T = string, U = number, result: number[]

// Swapping
function swap<A, B>(pair: [A, B]): [B, A] {
  return [pair[1], pair[0]];
}
```

## Generic Constraints

Use `extends` to constrain what types are accepted:

```typescript
// T must have a length property
function longest<T extends { length: number }>(a: T, b: T): T {
  return a.length >= b.length ? a : b;
}

longest("hello", "world");   // OK — string has length
longest([1, 2], [1, 2, 3]);  // OK — array has length
longest(10, 20);              // Error — number has no length

// Constraining to a key of another type
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

const user = { name: "Alice", age: 30 };
getProperty(user, "name");  // string
getProperty(user, "age");   // number
getProperty(user, "email"); // Error — "email" is not a key of user
```

## Default Type Parameters

```typescript
// Default to unknown if not specified
type Container<T = unknown> = { value: T };

const a: Container<string> = { value: "hello" };
const b: Container = { value: 42 }; // T defaults to unknown

// Defaults with constraints
interface Paginated<T, P extends number = 20> {
  items: T[];
  pageSize: P;
  page: number;
}
```

## Generic Classes

```typescript
class Stack<T> {
  private items: T[] = [];

  push(item: T): void {
    this.items.push(item);
  }

  pop(): T | undefined {
    return this.items.pop();
  }

  peek(): T | undefined {
    return this.items[this.items.length - 1];
  }
}

const numStack = new Stack<number>();
numStack.push(1);
numStack.push("hello"); // Error!

// Static members cannot reference class type parameters
class Factory<T> {
  // static defaultValue: T; // Error!
  static create<U>(): Factory<U> { return new Factory<U>(); } // OK — own parameter
}
```

## Generic Interfaces

```typescript
interface Repository<T> {
  findById(id: string): Promise<T | null>;
  save(entity: T): Promise<T>;
}

// Implementing a generic interface
class UserRepo implements Repository<User> {
  async findById(id: string): Promise<User | null> { ... }
  async save(user: User): Promise<User> { ... }
}
```

## `const` Type Parameters (TS 5.0+)

Adding `const` to a type parameter gives const-like inference without requiring `as const` at the call site:

```typescript
// Without const — infers broad types
function routes<T extends readonly { path: string; method: string }[]>(r: T): T {
  return r;
}
const r1 = routes([{ path: "/api", method: "GET" }]);
// Type: { path: string; method: string }[]

// With const — infers literal types
function routes<const T extends readonly { path: string; method: string }[]>(r: T): T {
  return r;
}
const r2 = routes([{ path: "/api", method: "GET" }]);
// Type: readonly [{ readonly path: "/api"; readonly method: "GET" }]
```

## Variance Annotations (TS 4.7+)

Explicit variance annotations help TypeScript check generic type compatibility more efficiently:

```typescript
// out = covariant (produces T)
interface Producer<out T> {
  get(): T;
}

// in = contravariant (consumes T)
interface Consumer<in T> {
  accept(value: T): void;
}

// in out = invariant (both produces and consumes T)
interface Processor<in out T> {
  process(value: T): T;
}
```

## Common Patterns

### Factory Pattern

```typescript
function create<T>(ctor: new (...args: any[]) => T, ...args: any[]): T {
  return new ctor(...args);
}
```

### Builder Pattern

```typescript
class QueryBuilder<T extends Record<string, unknown>> {
  private conditions: Partial<T> = {};

  where<K extends keyof T>(key: K, value: T[K]): this {
    this.conditions[key] = value;
    return this;
  }

  build(): Partial<T> {
    return { ...this.conditions };
  }
}

const query = new QueryBuilder<User>()
  .where("name", "Alice")
  .where("age", 30)
  .build();
```

### Constraining to Specific Shapes

```typescript
// Accept any object with a specific method
function serialize<T extends { toJSON(): string }>(item: T): string {
  return item.toJSON();
}

// Accept functions with specific signatures
function apply<T, R>(fn: (arg: T) => R, arg: T): R {
  return fn(arg);
}
```

## Guidelines

1. **Don't use generics when a concrete type works** — generics add complexity. If a function only ever works with strings, use `string`, not `T extends string`.

2. **Type parameters should appear at least twice** — if `T` only appears once in a signature, you probably don't need it:
   ```typescript
   // Bad — T is used only once
   function greet<T extends string>(name: T): string { ... }
   // Good — just use string
   function greet(name: string): string { ... }
   ```

3. **Prefer constraints over manual narrowing** — let the type system enforce requirements:
   ```typescript
   // Bad
   function process<T>(item: T) {
     if (typeof item !== "object") throw new Error("Must be object");
   }
   // Good
   function process<T extends object>(item: T) { ... }
   ```

4. **Use descriptive names for complex generics** — `T` is fine for simple cases, but use `TKey`, `TValue`, `TInput`, `TOutput` for clarity in complex signatures.

5. **Avoid deep generic nesting** — if you have `Foo<Bar<Baz<T>>>`, consider simplifying with intermediate type aliases.
