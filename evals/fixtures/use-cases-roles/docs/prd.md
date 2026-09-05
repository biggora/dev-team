# PRD — Community Blog

## 1. Overview

A small blogging product. Readers browse published posts, authors write and publish them, moderators keep comment threads clean, and a scheduler publishes posts queued for a future time.

## 2. Target Audience

Hobby writers publishing to a public audience, plus a small volunteer moderation group.

### 3. Actors & Roles

| ROLE-ID | Name | Kind | Authentication | Trust boundary | Source |
|---------|------|------|----------------|----------------|--------|
| ROLE-001 | Anonymous reader | human | none | public | request quote: "anyone can read what is published" |
| ROLE-002 | Registered author | human | session cookie | own posts and comment threads | request quote: "authors write, publish and clean up their threads" |
| ROLE-003 | Moderator | human | session cookie | own posts and comment threads |  | <!-- DEFECT: invented-role -->
| ROLE-004 | Scheduled publisher | system | internal scheduler token | internal | request quote: "let me queue a post for tomorrow morning" |

- ROLE-004 is a system actor and is not counted by the use-case rule.
- Every action this release permits ROLE-002 to perform is also permitted to ROLE-003, and no action is permitted to one and not the other. <!-- DEFECT: duplicate-role -->
- Two or more human roles are listed, so the scenarios live in `docs/use-cases.md`.

### 4. Functional Requirements

FR-001: Read published posts
  Priority: Must Have
  - AC-001: Given a published post, When any visitor requests its URL, Then the post body is returned with HTTP 200.
  - AC-002: Given an unpublished draft, When ROLE-001 requests its URL, Then the response is HTTP 404 and no draft content is disclosed.

FR-002: Write and publish posts
  Priority: Must Have
  - AC-003: Given an authenticated ROLE-002, When they submit a title and a non-empty body, Then a draft is stored and appears in their own post list.
  - AC-004: Given a draft owned by the requester, When they confirm publication, Then the post is readable by ROLE-001 within 5 seconds.

FR-003: Scheduled publication
  Priority: Should Have
  - AC-005: Given a draft with a publish time in the future, When that time is reached, Then ROLE-004 publishes it exactly once and a second scheduler run produces no duplicate publication.

FR-004: Moderate comments
  Priority: Should Have
  - AC-006: Given a visible comment, When ROLE-002 or ROLE-003 hides it, Then the comment is no longer returned to ROLE-001 and an audit entry records the acting ROLE-ID.

FR-005: Access control
  Priority: Must Have
  - AC-041: Given ROLE-001, When it submits a draft, Then the response is HTTP 403, no draft is stored, and the sign-in view is rendered instead of the editor.
  - AC-042: Given ROLE-001, When it schedules a post, Then the response is HTTP 403, no schedule is stored, and the sign-in view is rendered instead of the scheduling control.
  - AC-043: Given ROLE-001, When it hides a comment on its own behalf, Then the response is HTTP 403, the comment stays visible, and the sign-in view is rendered instead of the hide control.
  - AC-044: Given ROLE-001, When it hides a comment through the moderator surface, Then the response is HTTP 403, the comment stays visible, and the sign-in view is rendered instead of the hide control. <!-- DEFECT: criteria-inflation -->

### 5. Non-Functional Requirements

- Performance: a published post page responds in under 300 ms at the 95th percentile with 50 concurrent readers.
- Security: session cookies are HttpOnly and SameSite=Lax; draft content is never served to unauthenticated requests.
- Accessibility: the reader, editor, and moderation views meet WCAG 2.1 AA.

### 6. User Stories & Use Cases

- As a ROLE-001, I want to read published posts, so that I can follow the blog without an account.
- As a ROLE-002, I want to write and publish posts, so that my writing reaches readers.
- As a ROLE-003, I want to hide abusive comments, so that threads stay readable.

Index — the full catalogue is `docs/use-cases.md`:

- UC-001 | Read a published post | ROLE-001 | Covers: AC-001, AC-002
- UC-002 | Write and publish a post | ROLE-002 | Covers: AC-003, AC-004
- UC-003 | Schedule a post for later publication | ROLE-002 | Covers: —
- UC-004 | Hide a comment | ROLE-002 | Covers: AC-006
- UC-005 | Hide a comment | ROLE-003 | Covers: AC-006

### 7. Constraints, Assumptions & Open Questions

- Constraint: one database, no multi-tenancy (request quote: "just my blog, one server").
- OQ-001: Does scheduled publication use the author's timezone or UTC? Affects AC-005. Confirm before: slice 2.

### 11. Out of Scope

Paid subscriptions, newsletters, and full-text search.
