# Use Case Catalogue — Community Blog

Scope note: roles are defined in `docs/prd.md` section 3 and are referenced here by ROLE-ID only.

## ROLE-001 — Anonymous reader

UC-001 | Actor: ROLE-001 | Title: Read a published post
  Trigger: the reader opens a post URL
  Preconditions: the post is published
  Main flow:
    1. The reader requests the post URL
    2. The system returns the rendered post
  Alternative flows:
    A1 (step 1): the post is still a draft -> HTTP 404, no content disclosed
  Error paths:
    E1 (step 2): the store is unavailable -> error page shown, nothing served from a stale cache
  Postconditions: no state changes
  Covers: AC-001, AC-002

## ROLE-002 — Registered author

UC-002 | Actor: ROLE-002 | Title: Write and publish a post
  Trigger: the author activates "New post" and later confirms publication
  Preconditions: ROLE-002 is authenticated and owns the draft
  Main flow:
    1. The author submits a title and body, and the system stores a draft
    2. The author confirms publication and the system makes the post publicly readable
  Alternative flows:
    A1 (step 1): the body is empty -> validation error shown, no draft stored
  Error paths:
    E1 (step 2): storage unavailable -> error surfaced, the draft is left unpublished
  Postconditions: the post is readable by ROLE-001
  Covers: AC-003, AC-004

UC-003 | Actor: ROLE-002 | Title: Schedule a post for later publication
  Trigger: the author picks a future publish time on a draft
  Preconditions: ROLE-002 is authenticated and owns the draft
  Main flow:
    1. The author sets a publish time in the future
    2. The system stores the schedule and leaves the draft unpublished
  Alternative flows:
    A1 (step 1): the chosen time is in the past -> validation error, no schedule stored
  Error paths:
    E1 (step 2): the scheduler store is unavailable -> error surfaced, no schedule stored
  Postconditions: the draft carries a pending publish time
  Covers: <!-- DEFECT: uncovered-use-case -->

UC-004 | Actor: ROLE-002 | Title: Hide a comment
  Trigger: the author activates "Hide" on a comment in their own thread
  Preconditions: ROLE-002 is authenticated and the comment is visible
  Main flow:
    1. The author activates "Hide" on the comment
    2. The system marks the comment hidden and writes an audit entry
  Alternative flows:
    A1 (step 1): the comment is already hidden -> the control is not rendered, no request sent
  Error paths:
    E1 (step 2): the audit write fails -> the hide is rolled back and the comment stays visible
  Postconditions: the comment is no longer returned to ROLE-001
  Covers: AC-006

## ROLE-003 — Moderator

UC-005 | Actor: ROLE-003 | Title: Hide a comment <!-- DEFECT: role-duplicated-uc -->
  Trigger: the moderator activates "Hide" on a comment
  Preconditions: ROLE-003 is authenticated and the comment is visible
  Main flow:
    1. The moderator activates "Hide" on the comment
    2. The system marks the comment hidden and writes an audit entry
  Alternative flows:
    A1 (step 1): the comment is already hidden -> the control is not rendered, no request sent
  Error paths:
    E1 (step 2): the audit write fails -> the hide is rolled back and the comment stays visible
  Postconditions: the comment is no longer returned to ROLE-001
  Covers: AC-006

## Permission matrix

| UC | ROLE-001 anonymous | ROLE-002 author | ROLE-003 moderator | ROLE-004 scheduler |
|----|--------------------|-----------------|--------------------|--------------------|
| UC-001 Read a published post | allowed | allowed | allowed | N/A |
| UC-002 Write and publish a post | denied (AC-041) | allowed | allowed | allowed |
| UC-003 Schedule a post | denied (AC-042) | allowed | allowed | N/A |
| UC-004 Hide a comment | denied (AC-043) | allowed | allowed |  | <!-- DEFECT: incomplete-matrix -->
| UC-005 Hide a comment | denied (AC-044) | allowed | allowed | N/A |
