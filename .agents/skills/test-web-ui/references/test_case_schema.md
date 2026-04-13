# Test Plan JSON Schema

## Structure

```json
{
  "meta": {
    "site_name": "My Site",
    "url": "https://example.com",
    "created_at": "2025-01-01T12:00:00",
    "description": "QA test plan for homepage and auth flows"
  },
  "use_cases": [
    {
      "id": "UC-01",
      "actor": "Visitor",
      "action": "views the homepage",
      "goal": "understand what the product offers",
      "test_cases": ["TC-01", "TC-02"]
    }
  ],
  "test_cases": [
    {
      "id": "TC-01",
      "use_case": "UC-01",
      "name": "Homepage loads and shows key content",
      "path": "/",
      "mobile": false,
      "steps": [
        { "action": "scroll", "selector": "", "value": "" }
      ],
      "assertions": [
        { "type": "title_not_empty",    "description": "Page has a title" },
        { "type": "visible",            "selector": "nav",     "description": "Navigation is visible" },
        { "type": "visible",            "selector": "h1",      "description": "Main heading exists" },
        { "type": "count_gt",           "selector": "a",       "expected": "2", "description": "Multiple links exist" },
        { "type": "images_loaded",      "description": "All images loaded" },
        { "type": "no_console_errors",  "description": "No JS console errors" }
      ]
    }
  ]
}
```

## Assertion Types

| type | required fields | description |
|------|----------------|-------------|
| `visible` | selector | Element is visible on page |
| `not_visible` | selector | Element is NOT visible |
| `text_contains` | selector, expected | Element text contains string |
| `title_not_empty` | — | Page title is not blank |
| `title_contains` | expected | Page title contains string |
| `count_gt` | selector, expected | Count of elements > N |
| `count_eq` | selector, expected | Count of elements == N |
| `url_contains` | expected | Current URL contains string |
| `no_console_errors` | — | No JS errors in console |
| `images_loaded` | — | All img elements loaded (naturalWidth > 0) |
| `has_alt_text` | — | All images have alt attributes |
| `clickable` | selector | Element is visible and enabled |
| `attribute_equals` | selector, attribute, expected | Element attribute == value |

## Step Actions

| action | selector | value | description |
|--------|----------|-------|-------------|
| `click` | CSS selector | — | Click element |
| `fill` | CSS selector | text | Fill input with text |
| `wait_for` | CSS selector | — | Wait until element appears |
| `scroll` | — | — | Scroll to bottom of page |
| `hover` | CSS selector | — | Hover over element |

## Common Selectors Cheatsheet

```css
/* Navigation */
nav, header nav, [role=navigation]

/* Buttons */
button, [role=button], input[type=submit]

/* Forms */
form, input, textarea, select

/* Images */
img

/* Headings */
h1, h2, h3

/* Links */
a[href]

/* Footer */
footer

/* Error messages */
.error, [role=alert], .alert-danger

/* Success messages */
.success, .alert-success, [role=status]
```