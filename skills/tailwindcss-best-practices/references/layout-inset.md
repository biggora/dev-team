---
name: layout-inset
description: Controlling placement of positioned elements with top, right, bottom, left, and inset utilities
---

# Top / Right / Bottom / Left

Utilities for controlling the placement of positioned elements.

## Usage

### Basic positioning

Use `top-<number>`, `right-<number>`, `bottom-<number>`, `left-<number>` to position elements:

```html
<!-- Pin to top left corner -->
<div class="relative size-32">
  <div class="absolute top-0 left-0 size-16">01</div>
</div>

<!-- Span top edge -->
<div class="relative size-32">
  <div class="absolute inset-x-0 top-0 h-16">02</div>
</div>

<!-- Fill entire parent -->
<div class="relative size-32">
  <div class="absolute inset-0">05</div>
</div>
```

### Inset utilities

Use `inset-<number>` for all sides, `inset-x-<number>` for horizontal, `inset-y-<number>` for vertical:

```html
<div class="absolute inset-0">Fill parent</div>
<div class="absolute inset-x-0 top-0">Span top</div>
<div class="absolute inset-y-0 left-0">Span left</div>
```

### Negative values

Prefix with a dash for negative values:

```html
<div class="relative size-32">
  <div class="absolute -top-4 -left-4 size-14"></div>
</div>
```

### Logical properties (inline direction)

Use `inset-s-<number>` and `inset-e-<number>` for RTL-aware inline positioning:

```html
<div dir="ltr">
  <div class="absolute inset-s-0 top-0">Left in LTR</div>
</div>
<div dir="rtl">
  <div class="absolute inset-s-0 top-0">Right in RTL</div>
</div>
```

> **Deprecation (v4.2):** `start-*` and `end-*` are deprecated. Use `inset-s-*` and `inset-e-*` instead.

### Logical properties (block direction, v4.2+)

Use `inset-bs-<number>` and `inset-be-<number>` for writing-mode-aware block positioning:

```html
<div class="absolute inset-bs-0">Block-start: 0</div>
<div class="absolute inset-be-4">Block-end: 1rem</div>
```

### Percentage and custom values

Use fractions for percentages or arbitrary values:

```html
<div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
  Centered
</div>
<div class="absolute top-[117px] left-[20%]">
  Custom position
</div>
```

## Key Points

- `inset-0` sets all sides to 0 (equivalent to `top-0 right-0 bottom-0 left-0`)
- `inset-x-0` sets left and right to 0
- `inset-y-0` sets top and bottom to 0
- Use `inset-s-*`/`inset-e-*` for inline logical properties (`start-*`/`end-*` deprecated in v4.2)
- Use `inset-bs-*`/`inset-be-*` for block logical properties (v4.2+)
- Negative values use dash prefix: `-top-4`, `-left-8`
- Combine with `position` utilities (`absolute`, `fixed`, `relative`, `sticky`)

<!--
Source references:
- https://tailwindcss.com/docs/top-right-bottom-left
-->
