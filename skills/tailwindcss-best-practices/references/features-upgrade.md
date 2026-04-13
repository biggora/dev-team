---
name: features-upgrade
description: Migrating from Tailwind CSS v3 to v4, all renamed utilities, scale shifts, config migration, and v4.1/v4.2 changes
---

# Upgrade Guide (v3 → v4)

Key changes when upgrading from Tailwind CSS v3 to v4. Use the automated upgrade tool when possible.

## Upgrade Tool

```bash
npx @tailwindcss/upgrade
```

Requires Node.js 20+. Run in a new branch, review diff, test. Handles most migration automatically.

## Installation Changes

- **PostCSS**: Use `@tailwindcss/postcss`; remove `postcss-import` and `autoprefixer` (handled by v4)
- **Vite**: Prefer `@tailwindcss/vite` over PostCSS (supports Vite 8+ as of v4.2.2)
- **Webpack**: Use `@tailwindcss/webpack` (new in v4.2)
- **CLI**: Use `npx @tailwindcss/cli` instead of `npx tailwindcss`

## Import Change

```css
/* v3 */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* v4 */
@import "tailwindcss";
```

## Renamed Utilities — Scale Shifts

These are the most commonly missed renames because the entire scale shifted down by one step:

| v3 | v4 | What happened |
|----|-----|---------------|
| `shadow-sm` | `shadow-xs` | Scale shifted down |
| `shadow` | `shadow-sm` | Scale shifted down |
| `rounded-sm` | `rounded-xs` | Scale shifted down |
| `rounded` | `rounded-sm` | Scale shifted down |
| `blur-sm` | `blur-xs` | Scale shifted down |
| `blur` | `blur-sm` | Scale shifted down |

## Renamed Utilities — Other

| v3 | v4 |
|----|-----|
| `outline-none` | `outline-hidden` |
| `ring` | `ring-3` (default width changed from 3px to 1px) |

## Important Modifier

```html
<!-- v3: ! at start -->
<div class="!bg-red-500">

<!-- v4: ! at end -->
<div class="bg-red-500!">
```

## Removed / Replaced

| v3 | v4 |
|----|-----|
| `bg-opacity-*`, `text-opacity-*`, etc. | `bg-black/50`, `text-black/50` (slash syntax) |
| `flex-shrink-*` | `shrink-*` |
| `flex-grow-*` | `grow-*` |
| `overflow-ellipsis` | `text-ellipsis` |
| `decoration-slice` / `decoration-clone` | `box-decoration-slice` / `box-decoration-clone` |

## Ring & Border Defaults

- `ring` width: 3px → 1px; use `ring-3` for v3 behavior
- `ring` / `border` default color: `currentColor` (was gray-200 / blue-500 in v3)
- Always specify color: `ring-3 ring-blue-500`, `border border-gray-200`

## Configuration Migration

| v3 Concept | v4 Equivalent |
|------------|---------------|
| `tailwind.config.js` | Removed. Use CSS directives. |
| `darkMode: 'class'` | `@custom-variant dark (&:where(.dark, .dark *));` |
| `darkMode: 'media'` | Default in v4 (uses `prefers-color-scheme`). No config needed. |
| `theme.extend.colors` | `@theme { --color-*: value; }` |
| `theme.extend.screens` | `@theme { --breakpoint-*: value; }` |
| `theme.extend.fontFamily` | `@theme { --font-*: value; }` |
| `content: [...]` | Automatic detection. Use `@source` to add/exclude paths. |
| `safelist: [...]` | `@source inline("classes")` (v4.1+) |
| `@layer utilities { }` | `@utility name { }` |
| `plugins: [...]` | `@plugin "./my-plugin.js"` |

## CSS Variable Syntax Change

```html
<!-- v3: square brackets for CSS variables -->
<div class="bg-[--my-var]">

<!-- v4: parentheses for CSS variables -->
<div class="bg-(--my-var)">
```

## Theme Function Change

```css
/* v3 */
@media (min-width: theme(screens.xl)) { ... }

/* v4 */
@media (min-width: theme(--breakpoint-xl)) { ... }
```

## Other Breaking Changes

- **Variant stacking**: Left-to-right in v4 (was right-to-left in v3)
- **Transform reset**: `transform-none` no longer resets rotate/scale/translate; use `scale-none`, `rotate-none`, etc.
- **Hover on mobile**: `hover` only applies when device supports hover; override with `@custom-variant hover (&:hover)` if needed
- **Space/divide selectors**: Changed from `:not([hidden]) ~ :not([hidden])` to `:not(:last-child)`
- **Sass/Less/Stylus**: v4 not designed for use with CSS preprocessors

## Deprecations in v4.2

- `start-*` / `end-*` → use `inset-s-*` / `inset-e-*`
- `bg-left-top` style → use `bg-top-left` (position order reversed)
- `object-left-top` style → use `object-top-left` (position order reversed)

## Browser Support

v4 targets Safari 16.4+, Chrome 111+, Firefox 128+. For older browsers, stay on v3.4.

## Post-v4.0 Feature Additions

### v4.1 (April 2025)
- Text shadow utilities (`text-shadow-*`)
- Mask utilities (`mask-*`)
- Colored drop shadows (`drop-shadow-<color>`)
- Text wrapping (`wrap-break-word`, `wrap-anywhere`)
- Pointer device variants (`pointer-fine:`, `pointer-coarse:`)
- Safe alignment (`justify-center-safe`, `items-center-safe`)
- New variants: `details-content`, `inverted-colors`, `noscript`, `user-valid`, `user-invalid`
- `@source not` and `@source inline()` directives

### v4.2 (February 2025)
- New colors: mauve, olive, mist, taupe
- Webpack plugin (`@tailwindcss/webpack`)
- Block logical property utilities (`pbs-*`, `mbs-*`, `border-bs-*`, `inline-*`, `block-*`)
- Logical inset utilities (`inset-s-*`, `inset-e-*`, `inset-bs-*`, `inset-be-*`)
- Font feature settings (`font-features-*`)

<!--
Source references:
- https://tailwindcss.com/docs/upgrade-guide
- https://tailwindcss.com/blog/tailwindcss-v4-1
- https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.2.0
-->
