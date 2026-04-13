---
name: test-web-ui
description: >
  Automated web QA skill: analyzes a website or project, generates end-user use cases,
  derives a structured test plan, executes tests via Playwright browser automation, and
  produces a full HTML/Markdown QA report with screenshots and pass/fail results.

  TRIGGER this skill whenever the user asks to: test a website, run QA on a web app,
  check if a site works, find bugs on a site, validate a web project, create a test plan
  for a website, run functional tests, check a landing page, audit a web app for issues,
  test user flows — or any variation of "проверить сайт", "протестировать сайт",
  "QA сайта", "тест веб-приложения", "найти баги на сайте". Even if the user just says
  "посмотри работает ли всё нормально на сайте" — use this skill.
---

# Web Tester Skill

Transforms any website or project into a structured QA run:
**Discover → Plan → Execute → Report**

---

## Overview of Phases

```
Phase 1 → DISCOVERY   : Explore the site, understand its purpose and features
Phase 2 → USE CASES   : Generate end-user use case list
Phase 3 → TEST PLAN   : Convert use cases into concrete, executable test cases
Phase 4 → EXECUTION   : Run tests with Playwright, capture screenshots
Phase 5 → REPORT      : Compile HTML + Markdown report with all results
```

---

## Choosing Your Execution Tool

Pick the first option that works in your environment:

### Option 1: Playwright MCP Tools (recommended)

If Playwright MCP tools are available (e.g., `mcp__plugin_playwright_playwright__*`),
use them — they are the fastest and most token-efficient option (~2.8x faster than CLI,
fewer tool calls needed since each MCP call does more work):

```
browser_navigate → navigate to URL
browser_snapshot → get page state and element refs
browser_take_screenshot → capture screenshots
browser_click → click elements
browser_type → type into inputs
browser_evaluate → run JS assertions
browser_resize → test mobile viewports
browser_console_messages → check for JS errors
```

### Option 2: Playwright CLI

The [`@playwright/cli`](https://github.com/microsoft/playwright-cli) is a CLI
designed for coding agents. Use it when MCP tools are not available.
Install if needed:

```bash
npm install -g @playwright/cli@latest
```

Key commands for QA testing:

```bash
# Open a page
playwright-cli open https://example.com

# Take a snapshot (returns element refs for interaction)
playwright-cli snapshot

# Screenshot the page
playwright-cli screenshot

# Click, fill forms, type
playwright-cli click <ref>
playwright-cli fill <ref> "text value"
playwright-cli type "search query"
playwright-cli press Enter

# Mobile viewport testing — use a named session with mobile config
playwright-cli -s=mobile open https://example.com
# (configure viewport in .playwright/cli.config.json)

# Check console errors via snapshot output
playwright-cli snapshot

# Close when done
playwright-cli close
```

Playwright CLI is headless by default. Add `--headed` to watch the browser visually.
Use `playwright-cli show` to open a dashboard of all active sessions.

### Option 3: Python Playwright Scripts

If Python and Playwright are installed, use the bundled scripts in `scripts/`:

```bash
# Install if needed
pip install playwright && playwright install chromium

# Run discovery
python scripts/discover.py --url <URL> --output discovery.json

# Run tests
python scripts/run_tests.py --url <URL> --test-plan test_plan.json --output test_results/

# Generate report
python scripts/generate_report.py --results test_results/results.json --output qa_report.html
```

### Option 4: Manual Testing

If none of the above are available, read the source code directly and perform
manual analysis. Use `curl` or `fetch` for basic HTTP checks.

---

## Phase 1: Discovery

### What to gather
- **URL** — if the user provides a live URL, navigate to it and explore
- **Project files** — if no live URL, inspect source files in the project directory
- **Purpose** — what does the site do? (landing page, e-commerce, dashboard, blog, etc.)
- **Key pages** — home, auth, main feature pages, forms, checkout, etc.
- **Tech stack** — optional but helpful for targeted checks

### Discovery with Playwright MCP
```
1. browser_navigate to the URL
2. browser_snapshot to get the page structure
3. browser_take_screenshot for visual reference
4. Examine links, forms, headings, navigation from the snapshot
5. Navigate to discovered subpages and repeat
```

### Discovery with Playwright CLI
```bash
playwright-cli open <URL>
playwright-cli screenshot --name discovery_home
playwright-cli snapshot
# Examine snapshot output for links, forms, navigation, headings
# Follow important links to discover subpages
playwright-cli goto <subpage-url>
playwright-cli screenshot --name discovery_subpage
```

### Discovery with Python script
```bash
python scripts/discover.py --url <URL> --max-pages 10 --output discovery.json
```

### Local project (no live URL)
When only source files are available:
1. Start a local server: `python -m http.server 8080 --directory <project-path>`
   (or `npx serve <project-path>` or any other static server)
2. Run discovery against `http://localhost:8080`
3. If the port is busy, try 8081, 8082, etc.

**Important:** `file://` URLs may be blocked by some tools. Always prefer HTTP serving.

---

## Phase 2: Generate Use Cases

After discovery, produce a use case list **from the perspective of an end user**.

### Format
```
UC-01: [Actor] can [action] so that [goal]
UC-02: [Actor] can [action] so that [goal]
...
```

### Categories to cover
- **Navigation** — user browses pages, menu works, links resolve
- **Authentication** — sign up, log in, password reset, logout
- **Core feature flows** — the main thing the site does (purchase, search, submit form, etc.)
- **Content validation** — required text, images, prices, labels appear correctly
- **Forms** — fill in, submit, validate errors, success states
- **Responsiveness** — works on mobile viewport
- **Error handling** — 404 pages, empty states, invalid inputs
- **Performance / visual** — no broken images, no console errors, reasonable load
- **Accessibility basics** — alt text on images, heading hierarchy, landmark elements

Aim for **10–25 use cases** depending on site complexity.

---

## Phase 3: Test Plan

Convert each use case into a concrete test case:

```
TC-01 [UC-01]: Homepage Navigation
  Given: User opens the site root URL
  When:  Page finishes loading
  Then:  - Page title is not empty
         - Navigation menu is visible
         - Logo/brand element is present
         - No 404/500 status code
         Checks: title, nav links count > 0, hero text present
```

### Test case types to include
| Type | Examples |
|------|---------|
| **Presence checks** | Element exists, text is visible, image loads |
| **Functional checks** | Button clickable, form submits, menu expands |
| **Data validation** | Price format, phone format, required fields |
| **Navigation checks** | Links don't 404, routing works |
| **Form validation** | Empty submit shows errors, valid submit succeeds |
| **Responsiveness** | Mobile viewport renders without overflow |
| **Console errors** | No JS errors on page load |
| **Accessibility basics** | Images have alt text, headings hierarchy, landmarks |

If using the Python scripts, save the test plan as `test_plan.json` — see
`references/test_case_schema.md` for the JSON schema.

---

## Phase 4: Test Execution

For each test case, follow this pattern regardless of which tool you use:

1. **Navigate** to the target page
2. **Capture a "before" screenshot**
3. **Execute steps** — clicks, form fills, scrolling, waiting
4. **Run assertions** — element presence, text content, console errors, image loading
5. **Capture an "after" screenshot** if any interaction occurred
6. **Record result** — PASS / FAIL / SKIP + error message + duration

### Execution with Playwright MCP

```
browser_navigate to target URL
browser_take_screenshot for "before" capture
browser_snapshot to check element presence
browser_evaluate to run JS assertions:
  - document.title !== ''
  - document.querySelectorAll('nav').length > 0
  - document.querySelectorAll('img').filter(i => i.naturalWidth === 0).length
browser_click / browser_type for interactions
browser_take_screenshot for "after" capture
browser_console_messages to check for JS errors
browser_resize for mobile viewport testing
```

### Execution with Playwright CLI

```bash
# Navigate and screenshot
playwright-cli goto <URL>
playwright-cli screenshot --name tc01_before

# Get page state for assertions
playwright-cli snapshot
# Parse snapshot output to verify elements exist, text content matches, etc.

# Interact
playwright-cli click <ref>
playwright-cli fill <ref> "test@example.com"
playwright-cli press Enter

# After screenshot
playwright-cli screenshot --name tc01_after
```

For **mobile viewport testing**, open a separate session with mobile dimensions
or resize the browser.

For **status code testing** (e.g., checking that /404 returns 404): use
`playwright-cli` navigation — the tool reports HTTP status in its output. Note that
navigating to a 4xx/5xx page may throw an error in some tools; catch it gracefully
and record the status code from the error message.

### Execution with Python scripts

```bash
python scripts/run_tests.py \
  --url <URL> \
  --test-plan test_plan.json \
  --output test_results/
```

### Console error collection

Console errors are important signals. Collect them during each test:
- **Playwright MCP**: Use `browser_console_messages` or `browser_evaluate`
- **Playwright CLI**: Check snapshot output or use `playwright-cli` evaluation
- **Python scripts**: The script registers a console listener before navigation

### Image loading checks

To detect broken images, run this JS on the page:
```javascript
Array.from(document.images)
  .filter(img => img.naturalWidth === 0 && img.src && !img.src.startsWith('data:'))
  .map(img => img.src)
```
An empty result means all images loaded. Otherwise, list the broken URLs.

### Accessibility checks

Quick checks to run on each page:
```javascript
// Images missing alt text
document.querySelectorAll('img:not([alt]), img[alt=""]').length

// Heading hierarchy (should have h1, not skip levels)
[...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map(h => h.tagName)

// Landmark elements
document.querySelectorAll('main, nav, header, footer, [role]').length
```

---

## Phase 5: Report Generation

### Report contents
- **Summary dashboard** — total tests, pass/fail/skip counts, pass rate %, tested URL, timestamp
- **Use case list** with traceability to test cases
- **Test results table** — TC ID, name, status badge, duration, error message
- **Screenshot gallery** — inline base64 screenshots per test case (or file paths)
- **Console errors log** — any JS errors captured
- **Recommendations** — auto-generated improvement suggestions based on failures

### Report format
- Primary: **HTML** (self-contained, with embedded screenshots as base64)
- Secondary: **Markdown** summary for quick reading

### Using the Python report generator
```bash
python scripts/generate_report.py \
  --results test_results/results.json \
  --screenshots test_results/screenshots/ \
  --output qa_report.html
```

### Manual report generation
If the Python script is not available, generate the HTML report directly.
Build a self-contained HTML file with:
- A dark header with site name, URL, and timestamp
- Stat cards: total tests, passed, failed, skipped, pass rate
- A results table with status badges (green PASS, red FAIL, yellow SKIP)
- Embedded screenshots (base64-encoded PNGs)
- Recommendations section based on failures

Save the report in the current working directory or wherever the user specified.

---

## Workflow Summary (step-by-step)

```
1. Receive URL or project files from user
2. Pick your execution tool (MCP > Playwright CLI > Python > Manual)
3. Run discovery → understand pages, structure, features
4. Generate use case list (10–25 use cases)
5. Generate test plan → structured test cases
6. Run tests → collect results + screenshots
7. Generate HTML report
8. Show the report path to the user
```

---

## Handling Common Situations

**Local project without a live URL**
→ Serve files locally: `python -m http.server 8080` or `npx serve .`
→ Test against `http://localhost:8080`
→ Do NOT use `file://` URLs — they may be blocked

**Site requires authentication**
→ Ask user for test credentials OR
→ Test only the public-facing pages
→ Mark auth-gated tests as SKIP with note

**Single-page app (React/Vue/Angular)**
→ Wait for page to fully render (networkidle or specific selectors)
→ Check that JS bundle loads without console errors
→ Use snapshot/evaluate to verify dynamically rendered content

**Large site (many pages)**
→ Focus on critical user paths first
→ Limit to top 5–10 most important flows
→ Mention in report which pages were NOT covered

**Status code testing (4xx/5xx pages)**
→ Some tools throw errors on non-2xx responses
→ Catch the error and extract the status code from it
→ Or use JS `fetch()` to check status codes without navigation

**Mobile responsiveness testing**
→ Resize viewport to 390×844 (iPhone) or 360×800 (Android)
→ Check for horizontal overflow: `document.body.scrollWidth > window.innerWidth`
→ Verify key elements are still visible and readable

---

## Reference Files

- `references/test_case_schema.md` — JSON schema for test_plan.json
- `scripts/discover.py` — Site discovery automation (Python + Playwright)
- `scripts/run_tests.py` — Test execution engine (Python + Playwright)
- `scripts/generate_report.py` — HTML report generator (Python)
