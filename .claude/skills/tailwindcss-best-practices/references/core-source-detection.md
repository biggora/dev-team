---
name: core-source-detection
description: How Tailwind v4 detects classes in source files, @source directives, @source not, and @source inline() for safelisting
---

# Source Detection & Configuration

Tailwind v4 automatically scans your project for utility classes. This page covers how detection works and how to customize it.

## Automatic Detection

By default, Tailwind scans all files in your project except:

- Files matching `.gitignore` patterns
- `node_modules/` directory (ignored since v4.1)
- Binary files (images, videos, zips)
- CSS files
- Package manager lock files

Files are scanned as **plain text** — Tailwind does not parse your code. It looks for token patterns that match utility class names.

## Source Configuration

### Register additional sources

Scan files outside the project root (e.g., UI library in node_modules):

```css
@import "tailwindcss";
@source "../node_modules/@acmecorp/ui-lib";
```

### Set a base path

Restrict scanning to a specific directory (useful for monorepos):

```css
@import "tailwindcss" source("../src");
```

### Disable automatic detection

Scan only explicitly listed paths:

```css
@import "tailwindcss" source(none);
@source "../admin";
@source "../shared";
```

## Excluding Sources (v4.1+)

Exclude paths from scanning:

```css
@source not "../src/components/legacy";
@source not "./generated";
```

## Safelisting with @source inline() (v4.1+)

Force generation of classes not found in source files. This replaces the v3 `safelist` config option.

```css
/* Single utility */
@source inline("underline");

/* With variants */
@source inline("{hover:,focus:,}underline");

/* Color palette with brace expansion */
@source inline("{hover:,}bg-red-{50,{100..900..100},950}");

/* Exclude specific classes */
@source not inline("{hover:,focus:,}bg-red-{50,{100..900..100},950}");
```

Brace expansion follows shell-style syntax:
- `{a,b,c}` — list of values
- `{100..900..100}` — range with step (100, 200, 300, ..., 900)

## Dynamic Class Names

Because Tailwind scans files as plain text, it cannot detect dynamically constructed class names:

```jsx
// BAD — Tailwind won't detect these
const color = 'red';
<div className={`bg-${color}-500`} />

// GOOD — Use complete class names
const colorClasses = {
  red: 'bg-red-500',
  blue: 'bg-blue-500',
};
<div className={colorClasses[color]} />
```

If you must use dynamic classes, safelist them with `@source inline()`.

## Key Points

- Automatic detection scans all non-ignored, non-binary files
- `@source "path"` adds additional scan paths
- `@source not "path"` excludes paths (v4.1+)
- `@source inline("classes")` safelists classes (v4.1+), replaces v3 `safelist`
- `source(none)` on the import disables auto-detection
- Always use complete class names — never string-interpolate utility names

<!--
Source references:
- https://tailwindcss.com/docs/detecting-classes-in-source-files
- https://tailwindcss.com/blog/tailwindcss-v4-1
-->
