# Type Guards and Discriminated Unions

Type guards let you narrow a type within a conditional block. Discriminated unions combine literal types with exhaustive checking for robust state modeling.

## Built-in Narrowing

TypeScript narrows types automatically in many control flow patterns:

```typescript
// typeof
function process(x: string | number) {
  if (typeof x === "string") {
    x.toUpperCase(); // x is string
  }
}

// instanceof
function handle(err: Error | string) {
  if (err instanceof Error) {
    err.message; // err is Error
  }
}

// in operator
function move(animal: { swim?: () => void; fly?: () => void }) {
  if ("swim" in animal) {
    animal.swim!();
  }
}

// Truthiness
function print(name: string | null | undefined) {
  if (name) {
    name.toUpperCase(); // string (null and undefined removed)
  }
}

// Equality
function compare(a: string | number, b: string | boolean) {
  if (a === b) {
    a; // string (only common type)
  }
}
```

## User-Defined Type Guards

When built-in narrowing isn't enough, write custom type guard functions:

```typescript
// Type predicate — return type is `paramName is Type`
function isString(value: unknown): value is string {
  return typeof value === "string";
}

function process(value: unknown) {
  if (isString(value)) {
    value.toUpperCase(); // TypeScript knows value is string
  }
}

// Checking object shapes
interface User { type: "user"; name: string; email: string }
interface Admin { type: "admin"; name: string; permissions: string[] }

function isAdmin(person: User | Admin): person is Admin {
  return person.type === "admin";
}

// Array filtering with type guards
const items: (string | null)[] = ["hello", null, "world", null];
const strings: string[] = items.filter((x): x is string => x !== null);
```

### Inferred Type Predicates (TS 5.5+)

TypeScript 5.5 can infer type predicates for simple arrow functions:

```typescript
// Before 5.5: needed explicit annotation
const strings = items.filter((x): x is string => x !== null);

// TS 5.5+: inferred automatically
const strings = items.filter(x => x !== null); // string[]

// Also works with Boolean
const truthy = items.filter(Boolean); // string[] (nulls removed)
```

## Assertion Functions

Assertion functions narrow the type for all subsequent code (not just the if-block):

```typescript
function assertIsString(value: unknown): asserts value is string {
  if (typeof value !== "string") {
    throw new Error(`Expected string, got ${typeof value}`);
  }
}

function process(value: unknown) {
  assertIsString(value);
  // From here on, value is string
  value.toUpperCase();
}

// Assert non-null
function assertDefined<T>(value: T): asserts value is NonNullable<T> {
  if (value == null) {
    throw new Error("Value must be defined");
  }
}
```

## Discriminated Unions

A discriminated union is a union where each member has a literal property (the "discriminant") that uniquely identifies it:

```typescript
interface Circle {
  kind: "circle";
  radius: number;
}
interface Rectangle {
  kind: "rectangle";
  width: number;
  height: number;
}
interface Triangle {
  kind: "triangle";
  base: number;
  height: number;
}

type Shape = Circle | Rectangle | Triangle;

function area(shape: Shape): number {
  switch (shape.kind) {
    case "circle":
      return Math.PI * shape.radius ** 2;
    case "rectangle":
      return shape.width * shape.height;
    case "triangle":
      return 0.5 * shape.base * shape.height;
  }
}
```

### Exhaustive Checking

Ensure all union members are handled:

```typescript
// Method 1: never in default
function area(shape: Shape): number {
  switch (shape.kind) {
    case "circle":
      return Math.PI * shape.radius ** 2;
    case "rectangle":
      return shape.width * shape.height;
    case "triangle":
      return 0.5 * shape.base * shape.height;
    default:
      // If Shape gains a new member, this line errors
      const _exhaustive: never = shape;
      return _exhaustive;
  }
}

// Method 2: Helper function
function assertNever(x: never): never {
  throw new Error(`Unexpected value: ${x}`);
}

// Method 3: satisfies never
function area(shape: Shape): number {
  switch (shape.kind) {
    case "circle": return Math.PI * shape.radius ** 2;
    case "rectangle": return shape.width * shape.height;
    case "triangle": return 0.5 * shape.base * shape.height;
    default: return shape satisfies never;
  }
}
```

### Modeling Application State

```typescript
type RequestState<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error"; error: Error };

function renderUser(state: RequestState<User>) {
  switch (state.status) {
    case "idle":
      return "Click to load";
    case "loading":
      return "Loading...";
    case "success":
      return `Hello, ${state.data.name}`;  // data is available
    case "error":
      return `Error: ${state.error.message}`; // error is available
  }
}
```

### Result Type Pattern

```typescript
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

function divide(a: number, b: number): Result<number, string> {
  if (b === 0) return { ok: false, error: "Division by zero" };
  return { ok: true, value: a / b };
}

const result = divide(10, 3);
if (result.ok) {
  console.log(result.value); // number
} else {
  console.log(result.error); // string
}
```

## Narrowing with Control Flow

TypeScript tracks narrowing through assignments, returns, and throws:

```typescript
function process(value: string | null) {
  if (value === null) {
    return; // Early return narrows the rest
  }
  // value is string from here
  value.toUpperCase();
}

function validate(value: unknown): string {
  if (typeof value !== "string") {
    throw new Error("Not a string");
  }
  // value is string from here
  return value.trim();
}

// Assignment narrowing
let x: string | number;
x = "hello";
x.toUpperCase(); // OK — x is string after assignment
x = 42;
x.toFixed(2);    // OK — x is number after assignment
```

## Narrowing Gotchas

### Narrowing Doesn't Survive Callbacks

```typescript
function process(value: string | null) {
  if (value !== null) {
    // value is string here
    setTimeout(() => {
      value.toUpperCase(); // Still OK — value is const in closure
    }, 100);
  }
}

// But with reassignable variables:
let value: string | null = "hello";
if (value !== null) {
  setTimeout(() => {
    value.toUpperCase(); // Error! value might have been reassigned
  }, 100);
}
```

### Objects and Aliased Conditions

```typescript
// This doesn't narrow:
function isValid(obj: { x?: string }) {
  const hasX = obj.x !== undefined;
  if (hasX) {
    obj.x.toUpperCase(); // Error! TypeScript doesn't track aliased conditions
  }

  // This works:
  if (obj.x !== undefined) {
    obj.x.toUpperCase(); // OK
  }
}
```

### Narrowing with Generics

```typescript
// TypeScript can't narrow generic types well
function process<T extends string | number>(value: T) {
  if (typeof value === "string") {
    // value is still T, not string — narrowing is limited with generics
    // Use overloads or conditional types instead
  }
}
```
