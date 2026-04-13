# Mapped Types

Mapped types transform every property in an existing type, producing a new type. They iterate over keys and apply transformations.

## Basic Syntax

```typescript
type Mapped<T> = {
  [K in keyof T]: T[K];
};
```

This is the identity mapped type — it produces the same type. The power comes from modifying the value type or the key.

## Adding/Removing Modifiers

```typescript
// Add readonly to all properties
type Readonly<T> = {
  readonly [K in keyof T]: T[K];
};

// Remove readonly with -readonly
type Mutable<T> = {
  -readonly [K in keyof T]: T[K];
};

// Make all properties optional
type Partial<T> = {
  [K in keyof T]?: T[K];
};

// Remove optionality with -?
type Required<T> = {
  [K in keyof T]-?: T[K];
};

// Combine: mutable and required
type Concrete<T> = {
  -readonly [K in keyof T]-?: T[K];
};
```

## Key Remapping with `as` (TS 4.1+)

Remap keys during iteration using `as`:

```typescript
// Rename keys with a template literal
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

interface Person { name: string; age: number }
type PersonGetters = Getters<Person>;
// { getName: () => string; getAge: () => number }

// Filter keys by remapping to never
type RemoveFunctions<T> = {
  [K in keyof T as T[K] extends Function ? never : K]: T[K];
};

interface Mixed {
  name: string;
  age: number;
  greet(): void;
}
type DataOnly = RemoveFunctions<Mixed>;
// { name: string; age: number }
```

## Iterating Over Unions

Mapped types can iterate over any union of string literals, not just `keyof`:

```typescript
type EventMap = {
  [K in "click" | "hover" | "focus"]: (e: Event) => void;
};
// { click: (e: Event) => void; hover: (e: Event) => void; focus: (e: Event) => void }

// Using a union of string literals from an enum-like const
const EVENTS = ["click", "hover", "focus"] as const;
type EventHandlers = {
  [K in (typeof EVENTS)[number] as `on${Capitalize<K>}`]: (e: Event) => void;
};
// { onClick: (e: Event) => void; onHover: (e: Event) => void; onFocus: (e: Event) => void }
```

## Practical Patterns

### Making Specific Properties Optional

```typescript
type OptionalBy<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

interface User {
  id: string;
  name: string;
  email: string;
}
type CreateUser = OptionalBy<User, "id">;
// { name: string; email: string; id?: string }
```

### Deep Partial

```typescript
type DeepPartial<T> = {
  [K in keyof T]?: T[K] extends object ? DeepPartial<T[K]> : T[K];
};

interface Config {
  server: { host: string; port: number };
  db: { url: string; pool: { min: number; max: number } };
}

type PartialConfig = DeepPartial<Config>;
// All nested properties are optional
```

### Deep Readonly

```typescript
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object
    ? T[K] extends Function
      ? T[K]
      : DeepReadonly<T[K]>
    : T[K];
};
```

### Nullable Properties

```typescript
type Nullable<T> = {
  [K in keyof T]: T[K] | null;
};
```

### Event Emitter Types

```typescript
type EventEmitter<Events extends Record<string, any[]>> = {
  on<K extends keyof Events>(event: K, handler: (...args: Events[K]) => void): void;
  emit<K extends keyof Events>(event: K, ...args: Events[K]): void;
};

interface MyEvents {
  login: [user: User];
  error: [code: number, message: string];
  logout: [];
}

declare const emitter: EventEmitter<MyEvents>;
emitter.on("login", (user) => { ... });        // user: User
emitter.on("error", (code, msg) => { ... });   // code: number, msg: string
emitter.emit("logout");                         // no args
```

### API Route Types

```typescript
type ApiRoutes = {
  "/users": { GET: User[]; POST: User };
  "/users/:id": { GET: User; PUT: User; DELETE: void };
};

type RouteHandler<
  Routes extends Record<string, Record<string, any>>,
  Path extends keyof Routes,
  Method extends keyof Routes[Path]
> = () => Promise<Routes[Path][Method]>;
```

### Record-Like with Constraints

```typescript
// Like Record, but values depend on the key
type TypedRecord<K extends string, ValueFn extends Record<K, any>> = {
  [P in K]: ValueFn[P];
};

// Each validator returns the type it validates
type Validators = TypedRecord<
  "name" | "age",
  { name: string; age: number }
>;
// { name: string; age: number }
```

## Combining with Conditional Types

```typescript
// Make all function properties async
type Asyncify<T> = {
  [K in keyof T]: T[K] extends (...args: infer A) => infer R
    ? (...args: A) => Promise<R>
    : T[K];
};

interface Sync {
  getData(): string;
  count: number;
}
type Async = Asyncify<Sync>;
// { getData: () => Promise<string>; count: number }
```

## Homomorphic vs Non-Homomorphic

A mapped type is **homomorphic** when it maps over `keyof T` (preserving modifiers from the original):

```typescript
// Homomorphic — preserves optional/readonly from T
type Clone<T> = { [K in keyof T]: T[K] };

// Non-homomorphic — uses an independent key set
type FromKeys<K extends string> = { [P in K]: unknown };
```

Homomorphic mapped types automatically preserve `readonly` and `?` modifiers unless explicitly removed with `-readonly` or `-?`.
