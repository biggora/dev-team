# PRD — Personal Reading List

## 1. Overview

A single-user web app for saving article links, marking them read, and exporting the collection nightly to a JSON file.

## 2. Target Audience

One owner — technically comfortable, using the app from a desktop browser.

### 3. Actors & Roles

| ROLE-ID | Name | Kind | Authentication | Trust boundary | Source |
|---------|------|------|----------------|----------------|--------|
| ROLE-001 | Owner | human | session cookie | own data only | request quote: "it is just for me, nobody else logs in" |
| ROLE-002 | Nightly export job | system | internal cron token | internal | request quote: "dump the whole list to a file every night" |

- ROLE-002 is a system actor and is not counted by the use-case rule.
- Exactly one human role is listed, so the use cases stay in section 6 below and no `docs/use-cases.md` is created.

### 4. Functional Requirements

FR-001: Save a link
  Priority: Must Have
  - AC-001: Given an authenticated owner, When they submit a valid http or https URL, Then the link is stored with its fetched page title and appears at the top of the unread list.
  - AC-002: Given a URL already saved, When the owner submits it again, Then no second row is created and the existing entry's timestamp is updated.
  - AC-003: Given a string that is not an http or https URL, When the owner submits it, Then the response is HTTP 400 and nothing is stored.

FR-002: Mark a link read
  Priority: Must Have
  - AC-004: Given a saved unread link, When the owner marks it read, Then the entry moves to the read section and the unread count decreases by exactly one.

FR-003: Nightly export
  Priority: Should Have
  - AC-005: Given at least one saved link, When the nightly job runs, Then a JSON file containing every link is written, and a second run the same night overwrites that file rather than appending to it.

### 5. Non-Functional Requirements

- Performance: the list view renders in under 200 ms with 1000 saved links.
- Security: the session cookie is HttpOnly and SameSite=Lax; unauthenticated requests receive HTTP 401 and no data.
- Accessibility: the list view and the save form meet WCAG 2.1 AA.

### 6. User Stories & Use Cases

- As a ROLE-001, I want to save a link in one step, so that I can keep reading without losing the page.
- As a ROLE-001, I want to mark links read, so that my unread list stays short.

UC-001 | Actor: ROLE-001 | Title: Save a link
  Trigger: the owner submits a URL in the save form
  Preconditions: ROLE-001 is authenticated
  Main flow:
    1. The owner pastes a URL and submits the form
    2. The system fetches the page title and stores the link
    3. The system shows the entry at the top of the unread list
  Alternative flows:
    A1 (step 2): the URL is already saved -> the existing entry's timestamp is updated, no second row
    A2 (step 1): the input is not an http or https URL -> HTTP 400, nothing stored
  Error paths:
    E1 (step 2): the title fetch fails -> the link is stored with its URL as the title
  Postconditions: exactly one entry exists for that URL
  Covers: AC-001, AC-002, AC-003

UC-002 | Actor: ROLE-001 | Title: Mark a link read
  Trigger: the owner activates "Mark read" on a list entry
  Preconditions: the entry exists and is unread
  Main flow:
    1. The owner activates "Mark read"
    2. The system records the read state
    3. The system moves the entry into the read section
  Alternative flows:
    A1 (step 1): the entry is already read -> the control is not rendered, no request is sent
  Error paths:
    E1 (step 2): the store is unavailable -> the error is surfaced and the entry stays unread
  Postconditions: the unread count is one lower
  Covers: AC-004

AC-005 belongs to the system actor ROLE-002 and is exempt from reverse use-case coverage.

### 7. Constraints, Assumptions & Open Questions

- Constraint: one user, no sharing and no invitations (request quote: "it is just for me").
- OQ-001: Which directory should the nightly export be written to? Affects AC-005. Confirm before: slice 2.

### 11. Out of Scope

Sharing, multi-user accounts, browser extensions, and full-text search of article bodies.
