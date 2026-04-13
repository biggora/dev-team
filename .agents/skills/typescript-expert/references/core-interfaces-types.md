# Interfaces vs Type Aliases

## Declaration Syntax

```typescript
// Interface — declares a named object shape
interface User {
  id: string;
  name: string;
  email: string;
}

// Type alias — names any type expression
type User = {
  id: string;
  name: string;
  email: string;
};
```

## When to Use Which

**Use `interface` when:**
- Defining object shapes that might be extended
- Creating public API contracts (libraries, modules)
- You want declaration merging (adding fields across files)

**Use `type` when:**
- Creating unions, intersections, tuples, mapped types
- Aliasing primitives or complex type expressions
- You need computed properties or template literals

```typescript
// Only type can do these
type ID = string | number;                    // Union
type Pair<T> = [T, T];                        // Tuple
type Keys = keyof User;                       // Keyof
type Nullable<T> = T | null;                  // Generic alias
type EventName = `on${Capitalize<string>}`;   // Template literal
```

In practice, both work for object shapes. Pick one convention per project and be consistent.

## Extending and Composing

### Interface Extension

```typescript
interface Animal {
  name: string;
}

interface Dog extends Animal {
  breed: string;
}

// Multiple extension
interface ServiceDog extends Dog, Trainable {
  handler: string;
}

// Interfaces can extend type aliases
type HasId = { id: string };
interface User extends HasId {
  name: string;
}
```

### Type Intersection

```typescript
type Animal = { name: string };
type Dog = Animal & { breed: string };

// Intersections work with interfaces too
interface HasId { id: string }
type User = HasId & { name: string };
```

### Key Difference — Conflict Resolution

```typescript
// Interface extension: conflicts are errors
interface A { x: number }
interface B extends A { x: string } // Error! Type 'string' is not assignable to 'number'

// Type intersection: conflicts create never
type A = { x: number };
type B = A & { x: string }; // x is never (number & string = never)
// No error at definition — but you can never create a valid B
```

## Declaration Merging

Interfaces with the same name in the same scope merge automatically. Type aliases cannot merge:

```typescript
// Declaration merging — both declarations combine
interface Window {
  myCustomProp: string;
}
// Now Window has myCustomProp in addition to all standard properties

// This is how library augmentation works:
declare module "express" {
  interface Request {
    user?: User;  // Adds user to Express Request
  }
}
```

Type aliases produce an error if you declare the same name twice:

```typescript
type Foo = { a: string };
type Foo = { b: number }; // Error! Duplicate identifier 'Foo'
```

## Implementing Interfaces

Classes can implement interfaces to ensure they satisfy a contract:

```typescript
interface Serializable {
  serialize(): string;
  deserialize(data: string): void;
}

class Config implements Serializable {
  serialize() { return JSON.stringify(this); }
  deserialize(data: string) { Object.assign(this, JSON.parse(data)); }
}

// Classes can implement multiple interfaces
class User implements Serializable, Comparable<User> { ... }

// Classes can also implement type aliases (if they describe object shapes)
type Printable = { print(): void };
class Report implements Printable {
  print() { console.log("Report"); }
}
```

## Callable and Constructable Types

```typescript
// Callable interface
interface SearchFunc {
  (query: string, limit: number): SearchResult[];
}

// Equivalent type
type SearchFunc = (query: string, limit: number) => SearchResult[];

// Hybrid — object with call signature
interface Counter {
  (): number;          // Callable
  count: number;       // Property
  reset(): void;       // Method
}

// Constructable
interface ClockConstructor {
  new (hour: number, minute: number): Clock;
}
```

## Index Signatures

```typescript
interface StringDictionary {
  [key: string]: string;
  name: string;         // OK — string is assignable to string
  // count: number;     // Error — number not assignable to string
}

// Record is often cleaner than index signatures
type StringDict = Record<string, string>;

// Symbol index signatures (TS 4.4+)
interface SymbolMap {
  [key: symbol]: unknown;
}
```

## Readonly and Optional

```typescript
interface Config {
  readonly host: string;    // Cannot be reassigned after creation
  readonly port: number;
  debug?: boolean;          // Optional
}

const config: Config = { host: "localhost", port: 3000 };
config.host = "0.0.0.0"; // Error! Cannot assign to 'host'

// Deeply readonly with utility type
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K];
};
```

## Generic Interfaces and Types

```typescript
// Generic interface
interface Repository<T> {
  findById(id: string): Promise<T | null>;
  findAll(): Promise<T[]>;
  save(entity: T): Promise<T>;
  delete(id: string): Promise<void>;
}

// Usage
class UserRepository implements Repository<User> { ... }

// Generic type with default
type Container<T = unknown> = {
  value: T;
  metadata: Record<string, string>;
};
```

## Best Practices

1. **Don't use `I` prefix** — `IUser` is a C# convention, not TypeScript. Use `User`.
2. **Prefer narrow types** — `string` is usually too broad. Use literals or branded types.
3. **Avoid empty interfaces** — `interface Empty {}` matches almost everything due to structural typing.
4. **Use `readonly` by default** — Make properties mutable only when mutation is required.
5. **Single responsibility** — Keep interfaces focused. Compose with `extends` or `&`.
