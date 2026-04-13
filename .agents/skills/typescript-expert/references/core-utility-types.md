# Built-in Utility Types

TypeScript ships with utility types that transform existing types. These are invaluable for deriving new types without repetition.

## Object Transformation

### `Partial<T>` — Make All Properties Optional

```typescript
interface User {
  name: string;
  email: string;
  age: number;
}

type PartialUser = Partial<User>;
// { name?: string; email?: string; age?: number }

// Common use: update functions that accept partial data
function updateUser(id: string, updates: Partial<User>): User { ... }
updateUser("1", { name: "Alice" }); // OK — only updating name
```

### `Required<T>` — Make All Properties Required

```typescript
interface Config {
  host?: string;
  port?: number;
  debug?: boolean;
}

type FullConfig = Required<Config>;
// { host: string; port: number; debug: boolean }
```

### `Readonly<T>` — Make All Properties Readonly

```typescript
type FrozenUser = Readonly<User>;
// { readonly name: string; readonly email: string; readonly age: number }

const user: FrozenUser = { name: "Alice", email: "a@b.com", age: 30 };
user.name = "Bob"; // Error!

// Note: Readonly is shallow — nested objects are still mutable
```

### `Pick<T, K>` — Select Specific Properties

```typescript
type UserPreview = Pick<User, "name" | "email">;
// { name: string; email: string }
```

### `Omit<T, K>` — Remove Specific Properties

```typescript
type UserWithoutEmail = Omit<User, "email">;
// { name: string; age: number }

// Common: creating input types from entity types
type CreateUserInput = Omit<User, "id" | "createdAt">;
```

### `Record<K, V>` — Object with Known Keys and Value Type

```typescript
// String-keyed dictionary
type UserMap = Record<string, User>;

// Enum/union-keyed object (ensures all keys are covered)
type RolePermissions = Record<"admin" | "user" | "guest", string[]>;
const perms: RolePermissions = {
  admin: ["read", "write", "delete"],
  user: ["read", "write"],
  guest: ["read"],
};
// Missing a key would be an error
```

## Union Manipulation

### `Exclude<T, U>` — Remove Types from Union

```typescript
type T = "a" | "b" | "c";
type WithoutA = Exclude<T, "a">;     // "b" | "c"
type OnlyStrings = Exclude<string | number | boolean, number | boolean>; // string
```

### `Extract<T, U>` — Keep Only Matching Types

```typescript
type T = string | number | (() => void);
type Funcs = Extract<T, Function>;    // () => void
type Primitives = Extract<T, string | number>; // string | number
```

### `NonNullable<T>` — Remove `null` and `undefined`

```typescript
type MaybeString = string | null | undefined;
type DefiniteString = NonNullable<MaybeString>; // string
```

## Function Utilities

### `ReturnType<T>` — Extract Return Type

```typescript
function getUser() {
  return { id: "1", name: "Alice", roles: ["admin"] };
}

type User = ReturnType<typeof getUser>;
// { id: string; name: string; roles: string[] }

// Works with generics via conditional types
type AsyncReturn<T extends (...args: any) => any> =
  ReturnType<T> extends Promise<infer R> ? R : ReturnType<T>;
```

### `Parameters<T>` — Extract Parameter Types as Tuple

```typescript
function createUser(name: string, age: number, admin: boolean): User { ... }

type CreateUserParams = Parameters<typeof createUser>;
// [name: string, age: number, admin: boolean]

// Access individual parameters
type FirstParam = Parameters<typeof createUser>[0]; // string
```

### `ConstructorParameters<T>` — Constructor Parameter Types

```typescript
class User {
  constructor(public name: string, public age: number) {}
}

type UserCtorParams = ConstructorParameters<typeof User>;
// [name: string, age: number]
```

### `InstanceType<T>` — Instance Type from Constructor

```typescript
type UserInstance = InstanceType<typeof User>; // User
```

## String Manipulation Types

```typescript
type Upper = Uppercase<"hello">;      // "HELLO"
type Lower = Lowercase<"HELLO">;      // "hello"
type Cap = Capitalize<"hello">;       // "Hello"
type Uncap = Uncapitalize<"Hello">;   // "hello"

// Powerful with template literals
type EventName<T extends string> = `on${Capitalize<T>}`;
type ClickEvent = EventName<"click">; // "onClick"
```

## Promise Utilities

### `Awaited<T>` — Unwrap Promise Types (TS 4.5+)

```typescript
type A = Awaited<Promise<string>>;              // string
type B = Awaited<Promise<Promise<number>>>;     // number (recursive unwrap)
type C = Awaited<boolean | Promise<string>>;    // boolean | string
```

## `NoInfer<T>` (TS 5.4+)

Prevents a type parameter position from being used for inference:

```typescript
function createStreetLight<C extends string>(
  colors: C[],
  defaultColor?: NoInfer<C>
) { ... }

createStreetLight(["red", "yellow", "green"], "blue");
// Error! "blue" is not "red" | "yellow" | "green"
// Without NoInfer, TypeScript would widen C to include "blue"
```

## Composing Utility Types

Utility types compose naturally:

```typescript
// Readonly partial (for frozen default configs)
type Defaults<T> = Readonly<Partial<T>>;

// Pick and make required
type RequiredPick<T, K extends keyof T> = Required<Pick<T, K>>;

// Omit and make readonly
type ProtectedOmit<T, K extends keyof T> = Readonly<Omit<T, K>>;

// Make some properties optional, keep the rest
type PartialBy<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

type UserOptionalEmail = PartialBy<User, "email">;
// { name: string; age: number; email?: string }

// Make some properties required, keep the rest optional
type RequiredBy<T, K extends keyof T> = Partial<Omit<T, K>> & Required<Pick<T, K>>;
```

## Quick Reference Table

| Utility | Input | Output |
|---------|-------|--------|
| `Partial<T>` | `{ a: string; b: number }` | `{ a?: string; b?: number }` |
| `Required<T>` | `{ a?: string; b?: number }` | `{ a: string; b: number }` |
| `Readonly<T>` | `{ a: string }` | `{ readonly a: string }` |
| `Pick<T, K>` | `{ a: string; b: number }, "a"` | `{ a: string }` |
| `Omit<T, K>` | `{ a: string; b: number }, "a"` | `{ b: number }` |
| `Record<K, V>` | `"a" \| "b", number` | `{ a: number; b: number }` |
| `Exclude<T, U>` | `"a" \| "b" \| "c", "a"` | `"b" \| "c"` |
| `Extract<T, U>` | `string \| number, string` | `string` |
| `NonNullable<T>` | `string \| null` | `string` |
| `ReturnType<T>` | `() => string` | `string` |
| `Parameters<T>` | `(a: string, b: number) => void` | `[string, number]` |
| `Awaited<T>` | `Promise<string>` | `string` |
| `NoInfer<T>` | Prevents inference at position | Same type, no inference |
| `Uppercase<S>` | `"hello"` | `"HELLO"` |
| `Lowercase<S>` | `"HELLO"` | `"hello"` |
| `Capitalize<S>` | `"hello"` | `"Hello"` |
| `Uncapitalize<S>` | `"Hello"` | `"hello"` |
