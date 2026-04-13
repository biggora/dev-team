# Common TypeScript Patterns

## Branded Types (Nominal Typing)

TypeScript's structural typing means two identical shapes are interchangeable. Branded types add a phantom property to create distinct types:

```typescript
// Brand type helper
type Brand<T, B extends string> = T & { readonly __brand: B };

// Create distinct ID types
type UserId = Brand<string, "UserId">;
type OrderId = Brand<string, "OrderId">;
type ProductId = Brand<string, "ProductId">;

// Constructor functions
function UserId(id: string): UserId { return id as UserId; }
function OrderId(id: string): OrderId { return id as OrderId; }

// Now they can't be mixed up
function getOrder(orderId: OrderId): Order { ... }

const userId = UserId("user-123");
const orderId = OrderId("order-456");

getOrder(orderId);  // OK
getOrder(userId);   // Error! UserId not assignable to OrderId
```

### Validated Branded Types

Brands can enforce invariants at construction time:

```typescript
type Email = Brand<string, "Email">;
type PositiveNumber = Brand<number, "PositiveNumber">;

function Email(input: string): Email {
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input)) {
    throw new Error(`Invalid email: ${input}`);
  }
  return input as Email;
}

function PositiveNumber(n: number): PositiveNumber {
  if (n <= 0) throw new Error(`Must be positive: ${n}`);
  return n as PositiveNumber;
}
```

## Result Type (Error Handling Without Exceptions)

```typescript
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };

function ok<T>(data: T): Result<T, never> {
  return { success: true, data };
}

function err<E>(error: E): Result<never, E> {
  return { success: false, error };
}

// Usage
function parseJSON(input: string): Result<unknown, string> {
  try {
    return ok(JSON.parse(input));
  } catch {
    return err("Invalid JSON");
  }
}

const result = parseJSON('{"a": 1}');
if (result.success) {
  console.log(result.data); // unknown
} else {
  console.log(result.error); // string
}
```

## Builder Pattern

```typescript
class RequestBuilder {
  private config: Partial<RequestConfig> = {};

  url(url: string): this {
    this.config.url = url;
    return this;
  }

  method(method: "GET" | "POST" | "PUT" | "DELETE"): this {
    this.config.method = method;
    return this;
  }

  header(key: string, value: string): this {
    this.config.headers = { ...this.config.headers, [key]: value };
    return this;
  }

  build(): RequestConfig {
    if (!this.config.url) throw new Error("URL is required");
    return this.config as RequestConfig;
  }
}

// Type-safe builder with required fields tracked in the type
type Builder<T, Required extends keyof T = never> = {
  [K in keyof T]-?: (value: T[K]) => Builder<T, Required | K>;
} & ([Required] extends [keyof T]
  ? { build(): T }
  : { build: never });
```

## Discriminated Union State Machines

```typescript
type ConnectionState =
  | { state: "disconnected" }
  | { state: "connecting"; attempt: number }
  | { state: "connected"; socket: WebSocket }
  | { state: "error"; error: Error; retryAfter: number };

// Transition functions enforce valid state transitions
function connect(state: ConnectionState & { state: "disconnected" }): ConnectionState {
  return { state: "connecting", attempt: 1 };
}

function onConnected(
  state: ConnectionState & { state: "connecting" },
  socket: WebSocket
): ConnectionState {
  return { state: "connected", socket };
}
```

## Immutable Data

```typescript
// Readonly utility for shallow immutability
type Config = Readonly<{
  host: string;
  port: number;
  options: string[];
}>;

// as const for deep immutability of literals
const ROUTES = {
  home: "/",
  users: "/users",
  userDetail: "/users/:id",
} as const;

type Route = (typeof ROUTES)[keyof typeof ROUTES];
// "/" | "/users" | "/users/:id"

// Readonly collections
function processItems(items: readonly string[]): void {
  // items.push("x"); // Error! push doesn't exist on readonly array
  items.forEach(console.log); // Reading is fine
}
```

## Type-Safe Event Emitter

```typescript
type EventMap = Record<string, any[]>;

class TypedEmitter<Events extends EventMap> {
  private handlers = new Map<keyof Events, Set<Function>>();

  on<K extends keyof Events>(event: K, handler: (...args: Events[K]) => void): void {
    if (!this.handlers.has(event)) this.handlers.set(event, new Set());
    this.handlers.get(event)!.add(handler);
  }

  emit<K extends keyof Events>(event: K, ...args: Events[K]): void {
    this.handlers.get(event)?.forEach(fn => fn(...args));
  }

  off<K extends keyof Events>(event: K, handler: (...args: Events[K]) => void): void {
    this.handlers.get(event)?.delete(handler);
  }
}

// Usage
interface AppEvents {
  login: [user: User];
  logout: [];
  error: [code: number, message: string];
}

const emitter = new TypedEmitter<AppEvents>();
emitter.on("login", (user) => console.log(user.name));
emitter.on("error", (code, msg) => console.error(code, msg));
emitter.emit("login", currentUser);
```

## Exhaustive Map/Object

```typescript
// Ensure all enum/union members are mapped
type Status = "active" | "inactive" | "pending" | "archived";

const STATUS_LABELS: Record<Status, string> = {
  active: "Active",
  inactive: "Inactive",
  pending: "Pending",
  archived: "Archived",
  // Missing a key = compile error
};

// Function version
function getStatusColor(status: Status): string {
  const colors = {
    active: "#00ff00",
    inactive: "#999999",
    pending: "#ffaa00",
    archived: "#ff0000",
  } satisfies Record<Status, string>;

  return colors[status];
}
```

## Opaque Type Pattern

For when you want nominal types that are assignable from their base type in specific contexts:

```typescript
declare const __opaque: unique symbol;
type Opaque<T, Token> = T & { readonly [__opaque]: Token };

type Seconds = Opaque<number, "Seconds">;
type Milliseconds = Opaque<number, "Milliseconds">;

function wait(duration: Milliseconds): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, duration));
}

function toMilliseconds(seconds: Seconds): Milliseconds {
  return (seconds * 1000) as Milliseconds;
}

const sec = 5 as Seconds;
wait(sec);                    // Error! Seconds not assignable to Milliseconds
wait(toMilliseconds(sec));    // OK
```

## Safe Dictionary Access

```typescript
// With noUncheckedIndexedAccess (recommended)
const dict: Record<string, string> = { a: "hello" };
const val = dict["a"]; // string | undefined — forces null check

// Safe access pattern
function getOrThrow<T>(dict: Record<string, T>, key: string): T {
  const value = dict[key];
  if (value === undefined) throw new Error(`Missing key: ${key}`);
  return value;
}
```

## Const Assertions for Enum-Like Objects

Prefer `as const` objects over TypeScript enums:

```typescript
// Instead of:
enum Direction { North, South, East, West }

// Use:
const Direction = {
  North: "north",
  South: "south",
  East: "east",
  West: "west",
} as const;

type Direction = (typeof Direction)[keyof typeof Direction];
// "north" | "south" | "east" | "west"

// Benefits:
// - No runtime code beyond the object
// - Values are string literals (not numbers)
// - Easily iterable with Object.values()
// - Works with JSON serialization
```

## Assertion Signatures for Validation

```typescript
function assertNotNull<T>(value: T, message?: string): asserts value is NonNullable<T> {
  if (value == null) throw new Error(message ?? "Unexpected null");
}

function assertType<T>(value: unknown, check: (v: unknown) => v is T): asserts value is T {
  if (!check(value)) throw new Error("Type assertion failed");
}

// Chain assertions for parsing
function parseConfig(raw: unknown): Config {
  assertType(raw, isObject);
  assertNotNull(raw.host);
  assertType(raw.host, isString);
  assertType(raw.port, isNumber);
  return raw as Config;
}
```
