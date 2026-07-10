# PRD: slugify utility

## 1. Product Overview
A small Node.js utility that converts arbitrary titles into URL-safe slugs for a blogging platform.

## 3. Functional Requirements

FR-001: Slugify function
  Description: `slugify(title: string): string` in `src/slugify.js` converts a title to a URL-safe slug
  Priority: Must Have
  Acceptance Criteria:
    - AC-001: Given the title "Hello World", When slugify is called, Then it returns "hello-world"
    - AC-002: Given a title with punctuation "Rock & Roll, Baby!", When slugify is called, Then it returns "rock-roll-baby" (punctuation removed, spaces collapsed to single hyphens)
    - AC-003: Given a non-string input, When slugify is called, Then it throws a TypeError

FR-002: Trim and normalize
  Description: slugify trims whitespace and lowercases the result
  Priority: Must Have
  Acceptance Criteria:
    - AC-004: Given the title "  Mixed CASE  ", When slugify is called, Then it returns "mixed-case"

## 7. Out of Scope
Unicode transliteration, i18n.

## 8. Success Metrics
All acceptance criteria AC-001..AC-004 pass as automated tests (node --test).
