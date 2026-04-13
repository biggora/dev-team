# Core Type System

## Primitive Types

TypeScript has the same primitive types as JavaScript, plus a few extras:

```typescript
// JavaScript primitives
let str: string = "hello";
let num: number = 42;
let big: bigint = 100n;
let bool: boolean = true;
let sym: symbol = Symbol("key");
let undef: undefined = undefined;
let nul: null = null;

// TypeScript additions
let any_val: any;        // Opts out of type checking — avoid
let unknown_val: unknown; // Type-safe alternative to any
let never_val: never;     // Represents values that never occur
let void_val: void;       // Functions that don't return a value
```

### `never` — The Bottom Type

`never` is the type of values that never occur. It's the return type of functions that always throw or have infinite loops, and it's what you get when you exhaust all possibilities in a union:

```typescript
function fail(message: string): never {
  throw new Error(message);
}

// Exhaustiveness checking — never catches missing cases
type Shape = "circle" | "square" | "triangle";
function area(shape: Shape): number {
  switch (shape) {
    case "circle": return Math.PI;
    case "square": return 1;
    case "triangle": return 0.5;
    default:
      // If we add a new shape to the union and forget to handle it,
      // this line will show a compile error
      const _exhaustive: never = shape;
      return _exhaustive;
  }
}
```

### `void` vs `undefined`

`void` means a function doesn't return a meaningful value. `undefined` is a specific value:

```typescript
// void — callback return value is ignored
type Callback = () => void;
const cb: Callback = () => 42; // OK! void means "return value ignored"

// undefined — must literally return undefined
type UndefinedFn = () => undefined;
const fn: UndefinedFn = () => 42; // Error!
```

## Type Annotations vs Inference

TypeScript infers types from initialization, return statements, and context:

```typescript
// Inference works for:
const x = 10;                    // number
const arr = [1, 2, 3];           // number[]
const obj = { a: 1, b: "hi" };  // { a: number; b: string }

// Contextual typing — parameter types inferred from context
const names = ["Alice", "Bob"];
names.forEach(name => {
  console.log(name.toUpperCase()); // name inferred as string
});

// Annotate when inference isn't enough:
// 1. Function parameters (always annotate)
function greet(name: string) { ... }

// 2. Empty collections
const items: string[] = [];

// 3. Public API return types (documentation + refactoring safety)
export function parse(input: string): AST { ... }
```

## Type Narrowing

TypeScript narrows types based on control flow analysis:

```typescript
function process(value: string | number) {
  // typeof guard
  if (typeof value === "string") {
    value.toUpperCase(); // value is string here
  } else {
    value.toFixed(2);    // value is number here
  }
}

// Truthiness narrowing
function printName(name: string | null) {
  if (name) {
    console.log(name.toUpperCase()); // name is string (null removed)
  }
}

// instanceof narrowing
function logDate(date: Date | string) {
  if (date instanceof Date) {
    date.getFullYear(); // Date
  } else {
    Date.parse(date);   // string
  }
}

// in narrowing
interface Fish { swim(): void }
interface Bird { fly(): void }
function move(animal: Fish | Bird) {
  if ("swim" in animal) {
    animal.swim(); // Fish
  } else {
    animal.fly();  // Bird
  }
}

// Equality narrowing
function compare(a: string | number, b: string | boolean) {
  if (a === b) {
    // Both must be string (only common type)
    a.toUpperCase();
    b.toUpperCase();
  }
}
```

## Literal Types

TypeScript can narrow types to exact values:

```typescript
// String literal types
type Direction = "north" | "south" | "east" | "west";

// Numeric literal types
type DiceRoll = 1 | 2 | 3 | 4 | 5 | 6;

// Boolean literal types
type True = true;

// const assertions freeze literals
const config = {
  endpoint: "/api",
  retries: 3,
} as const;
// Type: { readonly endpoint: "/api"; readonly retries: 3 }

// let vs const inference
let x = "hello";   // type: string
const y = "hello";  // type: "hello" (literal)
```

## Tuple Types

Fixed-length arrays with known types at each position:

```typescript
// Basic tuple
type Point = [number, number];
const p: Point = [10, 20];

// Named tuple elements (documentation only, no runtime effect)
type Range = [start: number, end: number];

// Optional elements
type FlexPoint = [number, number, number?];
const p2: FlexPoint = [1, 2];    // OK
const p3: FlexPoint = [1, 2, 3]; // OK

// Rest elements
type StringsThenNumber = [...string[], number];
const val: StringsThenNumber = ["a", "b", 42]; // OK

// Readonly tuples
type ReadonlyPair = readonly [string, number];
```

## Arrays

```typescript
// Two equivalent syntaxes
let nums: number[] = [1, 2, 3];
let strs: Array<string> = ["a", "b"];

// Readonly arrays — prevent mutation
let frozen: readonly number[] = [1, 2, 3];
frozen.push(4); // Error! Property 'push' does not exist on readonly number[]

// ReadonlyArray<T> is equivalent
let frozen2: ReadonlyArray<number> = [1, 2, 3];
```

## Object Types

```typescript
// Inline object type
function printCoord(pt: { x: number; y: number }) {
  console.log(pt.x, pt.y);
}

// Optional properties
function printName(obj: { first: string; last?: string }) {
  console.log(obj.first);
  console.log(obj.last?.toUpperCase()); // Optional chaining
}

// Index signatures
interface StringMap {
  [key: string]: string;
}

// Intersection types — combine shapes
type Named = { name: string };
type Aged = { age: number };
type Person = Named & Aged; // { name: string; age: number }
```

## Union Types

```typescript
// Union of primitives
type StringOrNumber = string | number;

// Union of object types
type Result<T> = { ok: true; value: T } | { ok: false; error: Error };

// Narrowing unions
function handle(result: Result<string>) {
  if (result.ok) {
    console.log(result.value); // string
  } else {
    console.log(result.error.message); // Error
  }
}
```

## Special Types Reference

| Type | Meaning | Use for |
|------|---------|---------|
| `any` | Disables checking | Migration from JS (temporarily) |
| `unknown` | Must narrow before use | Safe alternative to `any` |
| `never` | No possible value | Exhaustiveness, impossible branches |
| `void` | No meaningful return | Callbacks whose return is ignored |
| `object` | Any non-primitive | Constraining to objects |
| `{}` | Any non-nullish value | Almost never — too permissive |
| `Object` | Like `{}` | Never use this |
