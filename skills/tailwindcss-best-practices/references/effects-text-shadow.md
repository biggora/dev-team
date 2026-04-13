---
name: effects-text-shadow
description: Text shadow utilities added in Tailwind CSS v4.1 — sizes, colors, and opacity modifiers
---

# Text Shadow (v4.1+)

Text shadow utilities for adding shadows to text content. Added in Tailwind CSS v4.1.

## Sizes

Five default sizes:

```html
<p class="text-shadow-2xs">Extra extra small shadow</p>
<p class="text-shadow-xs">Extra small shadow</p>
<p class="text-shadow-sm">Small shadow</p>
<p class="text-shadow-md">Medium shadow</p>
<p class="text-shadow-lg">Large shadow</p>
```

Remove text shadow:

```html
<p class="text-shadow-none">No shadow</p>
```

## Colors

Apply a color to the text shadow:

```html
<p class="text-shadow-lg text-shadow-blue-500">Blue shadow</p>
<p class="text-shadow-md text-shadow-gray-900">Dark shadow</p>
```

## Opacity Modifiers

Control shadow opacity with the slash modifier:

```html
<p class="text-shadow-lg/50">50% opacity shadow</p>
<p class="text-shadow-md text-shadow-sky-300/25">Sky shadow at 25%</p>
```

## Common Patterns

### Readable text over images

```html
<div class="relative">
  <img src="/hero.jpg" class="w-full" />
  <h1 class="absolute text-white text-shadow-lg text-shadow-black/50">
    Hero Title
  </h1>
</div>
```

### Subtle heading enhancement

```html
<h2 class="text-4xl font-bold text-shadow-sm text-shadow-gray-300">
  Section Title
</h2>
```

## Key Points

- Text shadows are separate from box shadows (`shadow-*`)
- Size and color are independent utilities that combine
- Opacity modifier goes on the size: `text-shadow-lg/50`
- Use `text-shadow-none` to remove shadows
- Works with all variants: `hover:text-shadow-lg`, `dark:text-shadow-md`

<!--
Source references:
- https://tailwindcss.com/blog/tailwindcss-v4-1
-->
