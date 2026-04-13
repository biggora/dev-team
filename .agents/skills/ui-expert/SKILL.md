---
name: ui-expert
description: >
  Build, refine, or review web UI/UX with strong visual taste, interaction
  design, accessibility, and front-end implementation quality. Use whenever
  the user wants a page, component, layout, design system, dashboard, landing
  page, form, navigation, responsive behavior, styling pass, UX polish,
  accessibility improvement, motion pass, or asks to make a web interface look
  or feel better. Framework-independent: think in HTML, CSS, and JavaScript
  primitives first, then adapt to the stack at hand.
---

# Frontend UI/UX

Build interfaces that are clear, fast, expressive, and hard to confuse for generic AI output.

Default to semantic HTML, modern CSS, and small JavaScript. Stay framework-agnostic unless the user or codebase requires otherwise.

## Operating mode

First decide which job you are doing:
- **Build**: create a new page, component, or styling system.
- **Refine**: improve an existing implementation without needless rewrites.
- **Review**: audit UI/UX, accessibility, responsiveness, and interaction quality.

If crucial context is missing, ask only for the minimum:
1. Who is this for?
2. What is the main user task?
3. What should it feel like?
4. Any hard constraints: brand, accessibility, performance, browser support, or existing stack?

If the prompt already implies the answers, do not stall; proceed and state assumptions briefly.

## Workflow

### 1. Choose a direction
Before coding, lock a clear direction:
- **Purpose**: what job the interface helps users do
- **Audience**: who uses it, in what context
- **Tone**: pick a distinct aesthetic direction, not a vague midpoint
- **Differentiator**: one memorable detail or principle that makes it feel intentional

Describe the direction in 1-3 lines before implementation.

### 2. Build from primitives
Prefer this order:
1. semantic structure
2. content hierarchy
3. layout
4. states and interactions
5. visual polish

Use HTML/CSS/JS concepts even when writing framework code:
- semantic landmarks, headings, labels, buttons, inputs, lists
- CSS custom properties for tokens
- progressive enhancement over cleverness
- small state surfaces and event flows

### 3. Make it feel good
Polish the parts users actually touch:
- hierarchy should be obvious at a glance
- spacing should create rhythm, not sameness
- interactions should feel responsive on press, hover, focus, drag, and loading
- copy should be short, specific, and helpful
- empty, error, loading, and success states should feel designed, not tacked on

### 4. Keep it fast and robust
Prefer simple implementations that survive change:
- mobile-first layouts
- fluid type and spacing with `clamp()` where useful
- container-aware components when layout context matters
- CSS variables for color, spacing, radius, shadow, and motion tokens
- animate `transform` and `opacity` first
- minimize JS; use it for state, measurement, and progressive enhancement

### 5. Self-review
Before finishing, check:
- usable without guessing
- visually cohesive
- responsive at narrow and wide widths
- keyboard and focus friendly
- sufficient contrast
- reduced-motion aware
- no gratuitous complexity

## Design rules

### Semantics and structure
- Start with semantic HTML. Good structure makes styling, accessibility, and maintenance easier.
- Make headings, labels, actions, and groups unambiguous.
- Prefer real buttons, inputs, links, dialogs, lists, and tables over `div` soup.
- Make states visible in the DOM and styling model; do not hide core behavior in fragile JS.

### Layout and composition
- Create clear visual hierarchy with size, contrast, spacing, and placement.
- Use asymmetry, overlap, or grid breaks intentionally, not randomly.
- Avoid "card soup": not every section needs a rounded box.
- Avoid nesting boxes inside boxes unless it clarifies hierarchy.
- Left-align long-form content by default; centered layouts are for short, deliberate moments.
- Use dense and loose spacing intentionally to create rhythm.

### Typography
- Typography does most of the design work. Treat it that way.
- Use a clear scale. Let headings lead, body copy recede, metadata stay quiet.
- Avoid generic defaults when the task calls for a distinctive feel, but do not chase novelty at the expense of readability.
- Keep line length, line height, and spacing comfortable.
- Make copy concise. Remove filler, repeated labels, and text that restates the obvious.

### Color and surfaces
- Commit to a palette with a point of view.
- Use neutrals with slight tint rather than dead grayscale when appropriate.
- Make emphasis sparse and meaningful.
- Use shadows, borders, blur, and gradients as support, not decoration spam.
- Avoid overused AI aesthetics unless the user explicitly wants them: purple-blue gradient hero, random glassmorphism, glowing dark dashboard, identical feature cards.

### Interaction and UX
- Make primary actions obvious.
- Use progressive disclosure: start simple, reveal more when needed.
- Prefer inline guidance over hidden rules.
- Design empty states to teach the next step.
- Make loading states preserve context whenever possible.
- Favor optimistic, responsive-feeling interactions when risk is low.
- Never make users work to discover what is clickable or what changed.

## Motion rules

Use motion to clarify state, spatial relationships, and feedback. Do not animate just because you can.

### When to animate
- Frequent actions: reduce or remove animation.
- Occasional actions: use short, clear transitions.
- Rare or celebratory moments: a little delight is fine.
- Keyboard-driven or repeated expert actions: prefer instant response.

### How to animate
- Prefer `ease-out` for entrances and direct responses.
- Use stronger custom curves when needed; default CSS easing is often too weak.
- Keep most UI motion under 300ms.
- Use transitions for interruptible UI.
- Avoid animating from `scale(0)`; start near the resting state and combine with opacity.
- Make anchored elements animate from the right origin.
- Add subtle press feedback to interactive controls.
- Respect `prefers-reduced-motion`; reduce movement, keep clarity.

### Performance
- Animate `transform` and `opacity` first.
- Be cautious with blur, shadows, and large repaint areas.
- Do not animate layout properties unless the tradeoff is clearly worth it.

## Accessibility and quality floor

Always preserve these basics:
- visible focus states
- keyboard reachability
- sufficient color contrast
- labels and affordances that make sense out of context
- touch targets large enough to hit
- hover effects not required for understanding
- forms with helpful errors and recovery paths
- motion that can be reduced

Accessibility is part of polish, not a cleanup pass.

## Anti-patterns

Avoid these unless the prompt clearly calls for them:
- generic template aesthetics with no point of view
- every action styled as primary
- giant hero + three feature cards + testimonial strip by default
- excessive border radius everywhere
- decorative charts, icons, or gradients with no informational role
- center-aligned everything
- hidden scrollbars or low-contrast text for style
- over-abstracted CSS/JS for small interfaces
- rewriting an entire UI when the user asked for targeted polish

## Delivery

### If building
Return:
1. a brief direction statement
2. the implementation
3. any notable UX/accessibility/performance choices

### If refining
Preserve what already works. Change the minimum that meaningfully improves clarity, feel, or maintainability.

### If reviewing
Use a compact table:

| Issue | Change | Why |
| --- | --- | --- |

Prioritize the highest-leverage fixes first.

## Heuristic

A good result should feel:
- obvious to use
- distinctive without being noisy
- fast without feeling abrupt
- polished in the small details
- simple in structure even when visually rich

If the result looks like it could have been generated for any product, push for a clearer point of view.
