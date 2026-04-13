---
name: test-mobile-app
description: >
  Automated mobile application testing skill. Use this skill whenever the user
  wants to test a mobile app (Android or iOS), write test cases, analyze app
  structure, run automated UI tests via emulator, or generate test reports.
  Trigger when user mentions: "test my app", "run tests", "UI testing",
  "write test cases", "check app functionality", "test on emulator",
  "mobile QA", "test coverage", "use case testing", "user scenario testing",
  or any combination of mobile + test/check/verify/validate.
  Also trigger when user uploads or references an APK, .ipa, or a mobile
  project folder (React Native, Flutter, Android, iOS) and asks what to do next.
  Always use this skill for any mobile app QA task — even partial ones like
  "just write some use cases" or "show me what tests I should run".
---

# Mobile App Testing Skill

This skill enables Claude to perform end-to-end mobile application testing:
1. **Analyze** the app structure and infer user-facing functionality
2. **Generate** use cases from an end-user perspective
3. **Write** concrete test scenarios with expected results
4. **Execute** tests via Appium + Android emulator (or interpret results statically)
5. **Produce** a structured HTML/Markdown test report

---

## Phase 1 — App Analysis

### What to collect

Before generating use cases, gather as much context as possible:

- **Source code** (Android/Java/Kotlin, iOS/Swift, React Native, Flutter)
- **APK file** — use `androguard` to extract Activity list, permissions, Manifest
- **Screenshots** — analyze UI from images
- **Description** — what the app does, target audience

### APK Analysis (Android)

Read `scripts/analyze_apk.py` for full script. Quick usage:
```bash
python3 scripts/analyze_apk.py path/to/app.apk
```
Outputs: package name, activities, permissions, strings → feeds into use case generation.

### Source Code Analysis

If source is available, scan for:
- Screen/Activity/Fragment/Page names → each is a potential use case surface
- Navigation graphs (React Navigation, NavController)
- API endpoints called (network requests)
- Form fields, validation logic
- Authentication flows

---

## Phase 2 — Use Case Generation

### Methodology

Think from the perspective of a **real end user** — not a developer.
Ask: *"What would a person actually do with this app?"*

Use case format:
```
UC-<N>: <Short Title>
Actor: End User
Precondition: <What must be true before this action>
Steps:
  1. <action>
  2. <action>
  ...
Expected outcome: <what the user sees/gets>
Priority: High / Medium / Low
```

### Use Case Categories to Always Cover

1. **Onboarding** — first launch, tutorial, permissions prompt
2. **Authentication** — registration, login, logout, password reset
3. **Core Feature Flow** — the primary value action of the app (1-3 flows)
4. **Data Entry** — any form: required fields, validation, error states
5. **Navigation** — bottom nav, back button, deep links
6. **Empty States** — what happens when there's no data
7. **Error Handling** — no internet, server error, invalid input
8. **Settings / Profile** — change preferences, update data
9. **Notifications** — if the app uses push notifications
10. **Accessibility** — basic: is text readable, are tap targets big enough

Aim for **15–30 use cases** depending on app complexity.

---

## Phase 3 — Test Scenario Writing

For each use case, write a test scenario:

```
TEST-<N>: <Title>
Related UC: UC-<N>
Type: Functional | UI | Regression | Smoke
Steps:
  1. Launch app
  2. <specific action with exact input data>
  3. ...
Assertions:
  - Element <locator> is visible
  - Text "<expected>" is displayed
  - Screen navigates to <ScreenName>
  - No crash / error dialog
Expected Result: PASS / FAIL criteria
```

### Test Types to Include

| Type | When to use |
|------|-------------|
| **Smoke** | Quick sanity — does app launch, core screens load? |
| **Functional** | Does feature X work correctly? |
| **UI/Visual** | Are elements present, correctly labeled, accessible? |
| **Edge Case** | Empty fields, special characters, very long strings |
| **Regression** | After a change — did existing features break? |

---

## Expo / React Native — Local Backend Setup

When the user's backend runs on the same machine as the development environment, the mobile app **cannot use `localhost` or `127.0.0.1`** — on a physical device or emulator, those addresses resolve to the device itself, not the host computer.

### Find the host machine's IP

```bash
# macOS / Linux
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows (PowerShell)
ipconfig
```

Use the LAN IP (e.g. `192.168.1.15`). The device and the machine must be on the same Wi-Fi network.

**Android emulator shortcut:** `10.0.2.2` is a special alias that always points to the host machine, so you don't need the LAN IP when testing on the built-in Android emulator.

### Configure the Expo app

Expo supports `.env` files with the `EXPO_PUBLIC_` prefix:

1. Create `.env.local` in the project root:
   ```
   EXPO_PUBLIC_API_URL=http://192.168.1.15:5000
   ```
2. Add `.env.local` to `.gitignore` (machine-specific setting).
3. Use the variable in code:
   ```js
   const response = await fetch(`${process.env.EXPO_PUBLIC_API_URL}/users`);
   ```

For multi-environment setups, use `app.config.js`:
```js
// app.config.js
export default ({ config }) => ({
  ...config,
  extra: {
    apiUrl: process.env.EXPO_PUBLIC_API_URL || 'http://localhost:5000',
  },
});
// Access via: Constants.expoConfig.extra.apiUrl  (expo-constants)
```

### Configure the backend

Two things must be set on the server side:

| Setting | Why |
|---------|-----|
| **Bind to `0.0.0.0`** | Default `127.0.0.1` binding rejects requests from outside the loopback interface — the device can't reach it |
| **Allow CORS** | The app's origin differs from the server origin; use `cors` (Express/Node), `django-cors-headers` (Django), `rack-cors` (Rails), etc. |

Example for Express:
```js
const cors = require('cors');
app.use(cors()); // or restrict to: { origin: 'http://192.168.1.15:8081' }
app.listen(5000, '0.0.0.0', () => console.log('listening on all interfaces'));
```

### Tunneling fallback (ngrok / Expo tunnel)

If direct LAN access fails (VPN, restrictive router, office firewall), use tunneling:

```bash
# Expo built-in tunnel (wraps ngrok)
npx expo start --tunnel
```

This creates a public HTTPS URL that forwards traffic to the local server. It's slower than LAN but works through any network. Update `EXPO_PUBLIC_API_URL` to the tunnel URL while using it.

### Testing checklist for local backend scenarios

- [ ] Backend bound to `0.0.0.0`, not `127.0.0.1`
- [ ] CORS configured on the server
- [ ] `EXPO_PUBLIC_API_URL` set to LAN IP (or `http://10.0.2.2:<port>` for Android emulator)
- [ ] Device and machine on the same Wi-Fi (for physical device)
- [ ] No firewall blocking the backend port on the host machine
- [ ] API endpoints respond to direct `curl http://<host-ip>:<port>/health` from terminal before running app tests

---

## Phase 4 — Test Execution

### Environment Setup

Read `references/setup-appium.md` for full Appium + emulator setup.

**Quick check:**
```bash
python3 scripts/check_environment.py
```
This verifies: adb, emulator, Appium server, Python client.

### Running Tests

```bash
# Run all tests
python3 scripts/run_tests.py --apk path/to/app.apk --output results/

# Run smoke tests only
python3 scripts/run_tests.py --apk path/to/app.apk --suite smoke --output results/

# Run on specific device
python3 scripts/run_tests.py --apk path/to/app.apk --device emulator-5554 --output results/
```

### Test Execution Without Emulator (Static Mode)

If no emulator is available (which is common — most users won't have Appium set up),
Claude can still provide significant value:
1. Analyze source code / screenshots / APK statically
2. Generate use cases and write all test scenarios
3. Mark execution status as `MANUAL_REQUIRED`
4. Generate a comprehensive report with all test cases ready to be run manually
5. Provide step-by-step manual testing instructions the user can follow

This is the **most common execution path** — don't treat it as a fallback.
Make the static report just as polished and detailed as the automated one.

Use `--static` flag:
```bash
python3 scripts/run_tests.py --static --tests tests.json --output results/
```

---

## Phase 5 — Report Generation

```bash
python3 scripts/generate_report.py --results results/ --output test_report.html
```

Report includes:
- Summary: total tests, passed, failed, skipped
- Per-test details: steps, assertions, actual vs expected, screenshots
- Use case coverage matrix
- Issues found (with severity: Critical / Major / Minor)
- Environment info (device, OS, app version)

Read `references/report-template.md` for report structure details.

---

## Workflow Summary

```
1. Receive app (APK / source / description / screenshots)
        ↓
2. Run analyze_apk.py OR inspect source code
        ↓
3. Generate use cases (UC-1...UC-N) — show to user, ask for feedback
        ↓
4. Write test scenarios (TEST-1...TEST-N) — derive from use cases
        ↓
5. Check environment (check_environment.py)
        ↓
6a. Emulator available → run_tests.py → capture results
6b. No emulator → static mode → mark for manual execution
        ↓
7. generate_report.py → HTML report → present to user
```

---

## Important Notes

- **Always show use cases to the user before writing tests** — they know their app best.
- **Locators**: Prefer `accessibility id` > `resource-id` > `xpath`. Never use index-based xpath.
- **Waits**: Always use explicit waits (`WebDriverWait`), never `time.sleep`.
- **Screenshots**: Capture on every assertion failure automatically.
- **Crash detection**: After every interaction, check for crash dialogs (the `check_for_crash()` function in `scripts/run_tests.py` handles this automatically).
- **Language**: Generate use cases and reports in the language the user is using.