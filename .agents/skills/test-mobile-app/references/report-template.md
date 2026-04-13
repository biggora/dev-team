# Test Report Structure

## tests.json Format

This is the input format for `run_tests.py`:

```json
{
  "app": "com.example.myapp",
  "version": "1.2.3",
  "generated_at": "2025-01-01T12:00:00",
  "use_cases": [
    {
      "id": "UC-1",
      "title": "User Login with valid credentials",
      "priority": "High"
    }
  ],
  "tests": [
    {
      "id": "TEST-001",
      "title": "Successful login with valid email and password",
      "related_uc": "UC-1",
      "type": "smoke",
      "steps": [
        { "action": "Launch app", "type": "wait", "seconds": 2 },
        { "action": "Tap Login button", "type": "tap", "locator": "Login" },
        { "action": "Enter email", "type": "type", "locator": "Email field", "value": "user@test.com" },
        { "action": "Enter password", "type": "type", "locator": "Password field", "value": "password123" },
        { "action": "Tap Submit", "type": "tap", "locator": "Submit" },
        { "action": "Assert home screen visible", "type": "assert_text", "expected": "Welcome" },
        { "action": "Assert no errors", "type": "assert_no_error" }
      ],
      "assertions": [
        "Home screen is displayed",
        "User name is shown",
        "No error messages"
      ]
    }
  ]
}
```

## Step Action Types

| type | Required fields | Description |
|------|----------------|-------------|
| `tap` | `locator` | Tap by accessibility id |
| `tap_id` | `locator` | Tap by resource-id |
| `type` | `locator`, `value` | Type text into field (by accessibility id) |
| `type_id` | `locator`, `value` | Type text into field (by resource-id) |
| `scroll_down` | — | Swipe screen upward |
| `back` | — | Press hardware back button |
| `wait` | `seconds` | Pause execution |
| `assert_visible` | `locator` | Assert element present by accessibility id |
| `assert_text` | `expected` | Assert text exists anywhere on screen |
| `assert_no_error` | — | Assert no error/crash text on screen |

## results.json Format (output)

```json
{
  "timestamp": "2025-01-01T12:05:00",
  "mode": "automated",
  "apk": "app.apk",
  "total": 10,
  "passed": 7,
  "failed": 2,
  "errors": 0,
  "manual": 1,
  "tests": [
    {
      "test_id": "TEST-001",
      "title": "Successful login",
      "status": "PASS",
      "steps_log": ["Step 1: Launch app", "Step 2: Tap Login"],
      "assertions": [
        { "check": "Text present: 'Welcome'", "passed": true }
      ],
      "error": null,
      "screenshot_path": null,
      "duration_ms": 3420,
      "issues_found": []
    }
  ]
}
```

## Issue Severity Levels

| Severity | Criteria |
|----------|----------|
| **Critical** | App crash, data loss, cannot complete core flow |
| **Major** | Feature broken, incorrect data displayed, error not handled |
| **Minor** | Visual glitch, misleading label, minor UX issue |