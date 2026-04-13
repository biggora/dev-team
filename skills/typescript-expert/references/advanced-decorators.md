# TC39 Decorators (TypeScript 5.0+)

TypeScript 5.0 introduced support for the TC39 Stage 3 decorator proposal. These are **not** the same as legacy `experimentalDecorators` — they have different semantics, no `reflect-metadata`, and work without any compiler flag.

## When to Use Which

- **TC39 decorators** (default, no flag): The standard going forward. Use for new code.
- **`experimentalDecorators`** (tsconfig flag): Legacy. Required by Angular, NestJS, TypeORM, and other frameworks that depend on `reflect-metadata`. Keep using if your framework requires it.

Check your framework's documentation — many are migrating to TC39 decorators.

## Class Decorators

```typescript
// A class decorator receives the class itself and an optional context
function sealed(target: Function, context: ClassDecoratorContext) {
  Object.seal(target);
  Object.seal(target.prototype);
}

@sealed
class Greeter {
  greeting: string;
  constructor(message: string) {
    this.greeting = message;
  }
}
```

### Adding Functionality

```typescript
function withTimestamp<T extends new (...args: any[]) => any>(
  target: T,
  context: ClassDecoratorContext
) {
  return class extends target {
    createdAt = new Date();
  };
}

@withTimestamp
class User {
  name: string;
  constructor(name: string) { this.name = name; }
}
```

## Method Decorators

```typescript
function log(
  target: Function,
  context: ClassMethodDecoratorContext
) {
  const methodName = String(context.name);
  return function (this: any, ...args: any[]) {
    console.log(`Calling ${methodName} with`, args);
    const result = target.call(this, ...args);
    console.log(`${methodName} returned`, result);
    return result;
  };
}

class Calculator {
  @log
  add(a: number, b: number): number {
    return a + b;
  }
}
```

### Bound Method Decorator

```typescript
function bound(
  target: Function,
  context: ClassMethodDecoratorContext
) {
  const methodName = context.name;
  context.addInitializer(function (this: any) {
    this[methodName] = this[methodName].bind(this);
  });
}

class Button {
  label = "Click me";

  @bound
  handleClick() {
    console.log(this.label); // Always correct `this`
  }
}
```

## Field Decorators

```typescript
function min(minValue: number) {
  return function (
    target: undefined, // field decorators receive undefined
    context: ClassFieldDecoratorContext
  ) {
    return function (initialValue: number) {
      if (initialValue < minValue) {
        throw new Error(`${String(context.name)} must be >= ${minValue}`);
      }
      return initialValue;
    };
  };
}

class Product {
  @min(0)
  price: number;

  constructor(price: number) {
    this.price = price;
  }
}
```

## Accessor Decorators

The `accessor` keyword (TS 5.0+) creates auto-accessor fields with implicit getter/setter:

```typescript
class Person {
  accessor name: string;

  constructor(name: string) {
    this.name = name;
  }
}

// Decorator for accessors
function validate(
  target: ClassAccessorDecoratorTarget<any, string>,
  context: ClassAccessorDecoratorContext
) {
  return {
    set(value: string) {
      if (!value.trim()) throw new Error(`${String(context.name)} cannot be empty`);
      target.set.call(this, value);
    },
    get() {
      return target.get.call(this);
    },
  };
}

class User {
  @validate
  accessor name: string = "";
}
```

## Decorator Factories

Most real-world decorators are factories — functions that return decorators:

```typescript
function retry(attempts: number) {
  return function (
    target: Function,
    context: ClassMethodDecoratorContext
  ) {
    return async function (this: any, ...args: any[]) {
      for (let i = 0; i < attempts; i++) {
        try {
          return await target.call(this, ...args);
        } catch (err) {
          if (i === attempts - 1) throw err;
        }
      }
    };
  };
}

class ApiClient {
  @retry(3)
  async fetchData(url: string): Promise<Response> {
    return fetch(url);
  }
}
```

## Decorator Context Types

Each decorator kind has a specific context type:

| Decorator Target | Context Type |
|------------------|-------------|
| Class | `ClassDecoratorContext` |
| Method | `ClassMethodDecoratorContext` |
| Getter | `ClassGetterDecoratorContext` |
| Setter | `ClassSetterDecoratorContext` |
| Field | `ClassFieldDecoratorContext` |
| Auto-accessor | `ClassAccessorDecoratorContext` |

All context types include:
- `name`: The name of the decorated element
- `kind`: "class", "method", "getter", "setter", "field", or "accessor"
- `static`: Whether the element is static
- `private`: Whether the element is private
- `addInitializer()`: Register a callback to run during construction
- `metadata`: Shared metadata object (replaces `reflect-metadata`)

## Metadata (TC39 Decorator Metadata)

TC39 decorators have a built-in metadata mechanism:

```typescript
function meta(key: string, value: any) {
  return function (_target: any, context: ClassMethodDecoratorContext) {
    context.metadata[key] = value;
  };
}

class Routes {
  @meta("path", "/users")
  @meta("method", "GET")
  getUsers() { ... }
}

// Access metadata
const metadata = Routes[Symbol.metadata];
// { path: "/users", method: "GET" }
```

## Migration from `experimentalDecorators`

Key differences:

| `experimentalDecorators` | TC39 Decorators |
|--------------------------|-----------------|
| Receives `(target, key, descriptor)` | Receives `(value, context)` |
| Uses `reflect-metadata` for metadata | Uses `context.metadata` |
| Parameter decorators supported | No parameter decorators |
| `emitDecoratorMetadata` flag | No equivalent (use `context.metadata`) |
| Runs at class definition time | Runs at class definition time |

Parameter decorators are **not** part of TC39 decorators. Frameworks that need them (like NestJS for DI) still require `experimentalDecorators`.
