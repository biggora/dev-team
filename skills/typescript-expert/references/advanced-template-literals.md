# Template Literal Types

Template literal types build string types from other types using template literal syntax. They're TypeScript's most powerful tool for type-safe string manipulation.

## Basic Syntax

```typescript
type Greeting = `Hello, ${string}`;
// Matches "Hello, Alice", "Hello, Bob", "Hello, " — any string after "Hello, "

type HttpMethod = "GET" | "POST" | "PUT" | "DELETE";
type Endpoint = `/api/${string}`;
type ApiCall = `${HttpMethod} ${Endpoint}`;
// "GET /api/..." | "POST /api/..." | "PUT /api/..." | "DELETE /api/..."
```

## Union Expansion

When unions appear in template literal positions, the result is the cross product:

```typescript
type Suit = "hearts" | "diamonds" | "clubs" | "spades";
type Rank = "A" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" | "10" | "J" | "Q" | "K";
type Card = `${Rank} of ${Suit}`;
// "A of hearts" | "A of diamonds" | ... | "K of spades" (52 members)

type Size = "sm" | "md" | "lg";
type Color = "red" | "blue" | "green";
type Variant = `${Size}-${Color}`;
// "sm-red" | "sm-blue" | "sm-green" | "md-red" | ... (9 members)
```

## Intrinsic String Manipulation Types

TypeScript provides four built-in types that transform string literals:

```typescript
type A = Uppercase<"hello">;       // "HELLO"
type B = Lowercase<"HELLO">;       // "hello"
type C = Capitalize<"hello">;      // "Hello"
type D = Uncapitalize<"Hello">;    // "hello"

// Combined with template literals
type EventHandler<T extends string> = `on${Capitalize<T>}`;
type Click = EventHandler<"click">;     // "onClick"
type KeyDown = EventHandler<"keyDown">; // "onKeyDown"
```

## Pattern Matching with `infer`

Template literals can extract parts of string types:

```typescript
// Extract the event name from "on{Event}"
type ExtractEvent<T> = T extends `on${infer E}` ? Uncapitalize<E> : never;
type A = ExtractEvent<"onClick">;   // "click"
type B = ExtractEvent<"onKeyDown">; // "keyDown"
type C = ExtractEvent<"submit">;    // never

// Parse dot-separated paths
type FirstSegment<T extends string> = T extends `${infer Head}.${string}` ? Head : T;
type D = FirstSegment<"user.address.city">; // "user"
type E = FirstSegment<"name">;               // "name"

// Split a string type
type Split<S extends string, D extends string> =
  S extends `${infer Head}${D}${infer Tail}`
    ? [Head, ...Split<Tail, D>]
    : [S];

type F = Split<"a.b.c", ".">;  // ["a", "b", "c"]
```

## Practical Patterns

### Type-Safe Event System

```typescript
type EventMap = {
  click: { x: number; y: number };
  keydown: { key: string };
  resize: { width: number; height: number };
};

type EventHandlerName<T extends string> = `on${Capitalize<T>}`;

type EventHandlers<E extends Record<string, any>> = {
  [K in keyof E as EventHandlerName<string & K>]?: (event: E[K]) => void;
};

type MyHandlers = EventHandlers<EventMap>;
// { onClick?: (event: { x: number; y: number }) => void;
//   onKeydown?: (event: { key: string }) => void;
//   onResize?: (event: { width: number; height: number }) => void; }
```

### Type-Safe CSS Properties

```typescript
type CSSUnit = "px" | "em" | "rem" | "%" | "vh" | "vw";
type CSSValue = `${number}${CSSUnit}` | "auto" | "inherit";

function setWidth(el: HTMLElement, width: CSSValue) {
  el.style.width = width;
}

setWidth(el, "100px");   // OK
setWidth(el, "2.5rem");  // OK
setWidth(el, "auto");    // OK
setWidth(el, "100");     // Error — missing unit
```

### Route Parameter Extraction

```typescript
type ExtractParams<T extends string> =
  T extends `${string}:${infer Param}/${infer Rest}`
    ? Param | ExtractParams<`/${Rest}`>
    : T extends `${string}:${infer Param}`
      ? Param
      : never;

type Params = ExtractParams<"/users/:userId/posts/:postId">;
// "userId" | "postId"

type RouteParams<T extends string> = {
  [K in ExtractParams<T>]: string;
};

type UserPostParams = RouteParams<"/users/:userId/posts/:postId">;
// { userId: string; postId: string }
```

### SQL Column Type Mapping

```typescript
type SQLType = "TEXT" | "INTEGER" | "BOOLEAN" | "TIMESTAMP";

type TSTypeMap = {
  TEXT: string;
  INTEGER: number;
  BOOLEAN: boolean;
  TIMESTAMP: Date;
};

type ColumnDef<Name extends string, Type extends SQLType> = `${Name} ${Type}`;

type ParseColumn<T> = T extends `${infer Name} ${infer Type extends SQLType}`
  ? { name: Name; type: TSTypeMap[Type] }
  : never;

type Col = ParseColumn<"username TEXT">;
// { name: "username"; type: string }
```

### Deep Property Paths

```typescript
type PropPath<T, Prefix extends string = ""> = {
  [K in keyof T & string]: T[K] extends object
    ? PropPath<T[K], `${Prefix}${K}.`>
    : `${Prefix}${K}`;
}[keyof T & string];

interface User {
  name: string;
  address: {
    city: string;
    zip: string;
  };
}

type UserPaths = PropPath<User>;
// "name" | "address.city" | "address.zip"
```

## Template Literals as Discriminants (TS 4.5+)

Template literal types can serve as discriminants in unions:

```typescript
interface SuccessResponse {
  type: `${string}Success`;
  data: unknown;
}

interface ErrorResponse {
  type: `${string}Error`;
  message: string;
}

function handle(r: SuccessResponse | ErrorResponse) {
  if (r.type === "ApiSuccess") {
    r.data;  // SuccessResponse narrowed
  }
}
```

## Performance Considerations

Template literal unions grow multiplicatively. A cross product of two unions with 10 members each creates 100 members. TypeScript limits union sizes (around 100,000 members), so avoid unbounded cross products:

```typescript
// This is fine — 3 x 3 = 9 members
type Small = `${1 | 2 | 3}-${"a" | "b" | "c"}`;

// This would be problematic — string has infinite members
// type Bad = `${string}-${string}`; // Works but can't enumerate
```
