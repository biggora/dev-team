#!/usr/bin/env python3
"""
run_tests.py — Execute mobile test scenarios via Appium or in static mode.

Usage:
  python3 run_tests.py --apk app.apk --tests tests.json --output results/
  python3 run_tests.py --static --tests tests.json --output results/
"""
import argparse
import json
import os
import time
import datetime
import traceback
from pathlib import Path


# ─────────────────────────────────────────
#  Data structures
# ─────────────────────────────────────────

class TestResult:
    def __init__(self, test_id: str, title: str):
        self.test_id = test_id
        self.title = title
        self.status = "PENDING"   # PASS | FAIL | SKIP | MANUAL_REQUIRED | ERROR
        self.steps_log = []
        self.assertions = []
        self.error = None
        self.screenshot_path = None
        self.duration_ms = 0
        self.issues_found = []

    def to_dict(self):
        return {
            "test_id": self.test_id,
            "title": self.title,
            "status": self.status,
            "steps_log": self.steps_log,
            "assertions": self.assertions,
            "error": self.error,
            "screenshot_path": self.screenshot_path,
            "duration_ms": self.duration_ms,
            "issues_found": self.issues_found,
        }


# ─────────────────────────────────────────
#  Appium driver helpers
# ─────────────────────────────────────────

def create_driver(apk_path: str, device_id: str = None):
    """Create Appium WebDriver for Android."""
    try:
        from appium import webdriver
        from appium.options import AppiumOptions
    except ImportError:
        raise RuntimeError("appium-python-client not installed. Run: pip install Appium-Python-Client --break-system-packages")

    options = AppiumOptions()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.app = os.path.abspath(apk_path)
    options.no_reset = False
    options.full_reset = False

    if device_id:
        options.udid = device_id

    driver = webdriver.Remote("http://localhost:4723/wd/hub", options=options)
    driver.implicitly_wait(10)
    return driver


def safe_find(driver, by, value, timeout=10):
    """Find element with explicit wait."""
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )


def check_for_crash(driver):
    """Returns crash message if a crash dialog is detected, else None."""
    try:
        # Look for common crash dialog text
        from appium.webdriver.common.appiumby import AppiumBy
        crash_indicators = [
            "has stopped",
            "keeps stopping",
            "isn't responding",
            "Unfortunately",
        ]
        page_source = driver.page_source
        for indicator in crash_indicators:
            if indicator.lower() in page_source.lower():
                return f"Crash dialog detected: '{indicator}'"
        return None
    except Exception:
        return None


def take_screenshot(driver, output_dir: str, test_id: str, step: int) -> str:
    """Take screenshot and save to output dir."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    path = os.path.join(output_dir, f"{test_id}_step{step}.png")
    try:
        driver.save_screenshot(path)
        return path
    except Exception:
        return None


# ─────────────────────────────────────────
#  Core test runner
# ─────────────────────────────────────────

def run_test_automated(driver, test: dict, output_dir: str) -> TestResult:
    """Execute a single test case via Appium driver."""
    from appium.webdriver.common.appiumby import AppiumBy

    result = TestResult(test["id"], test["title"])
    start = time.time()

    try:
        steps = test.get("steps", [])

        for i, step in enumerate(steps):
            action = step.get("action", "")
            result.steps_log.append(f"Step {i+1}: {action}")

            # Crash check after each step
            crash = check_for_crash(driver)
            if crash:
                result.status = "FAIL"
                result.error = crash
                result.issues_found.append({"severity": "Critical", "description": crash})
                result.screenshot_path = take_screenshot(driver, output_dir, test["id"], i)
                return result

            # Execute action
            try:
                act_type = step.get("type", "")

                if act_type == "tap" and step.get("locator"):
                    el = safe_find(driver, AppiumBy.ACCESSIBILITY_ID, step["locator"])
                    el.click()

                elif act_type == "tap_id" and step.get("locator"):
                    el = safe_find(driver, AppiumBy.ID, step["locator"])
                    el.click()

                elif act_type == "type" and step.get("locator"):
                    el = safe_find(driver, AppiumBy.ACCESSIBILITY_ID, step["locator"])
                    el.clear()
                    el.send_keys(step.get("value", ""))

                elif act_type == "type_id" and step.get("locator"):
                    el = safe_find(driver, AppiumBy.ID, step["locator"])
                    el.clear()
                    el.send_keys(step.get("value", ""))

                elif act_type == "scroll_down":
                    driver.swipe(500, 1000, 500, 300, 500)

                elif act_type == "back":
                    driver.back()

                elif act_type == "wait":
                    time.sleep(step.get("seconds", 1))

                elif act_type == "assert_visible":
                    locator = step.get("locator", "")
                    try:
                        el = safe_find(driver, AppiumBy.ACCESSIBILITY_ID, locator, timeout=5)
                        result.assertions.append({"check": f"Element visible: {locator}", "passed": True})
                    except Exception:
                        result.assertions.append({"check": f"Element visible: {locator}", "passed": False})
                        result.status = "FAIL"
                        result.screenshot_path = take_screenshot(driver, output_dir, test["id"], i)

                elif act_type == "assert_text":
                    expected = step.get("expected", "")
                    page_source = driver.page_source
                    found = expected.lower() in page_source.lower()
                    result.assertions.append({"check": f"Text present: '{expected}'", "passed": found})
                    if not found:
                        result.status = "FAIL"
                        result.screenshot_path = take_screenshot(driver, output_dir, test["id"], i)

                elif act_type == "assert_no_error":
                    page = driver.page_source.lower()
                    error_words = ["error", "ошибка", "failed", "exception"]
                    has_error = any(w in page for w in error_words)
                    result.assertions.append({"check": "No error on screen", "passed": not has_error})
                    if has_error:
                        result.status = "FAIL"
                        result.issues_found.append({"severity": "Major", "description": "Error text found on screen"})

            except Exception as step_err:
                result.steps_log.append(f"  ⚠️ Step failed: {step_err}")
                result.screenshot_path = take_screenshot(driver, output_dir, test["id"], i)

        # Final crash check
        crash = check_for_crash(driver)
        if crash:
            result.status = "FAIL"
            result.error = crash
            result.issues_found.append({"severity": "Critical", "description": crash})
        elif result.status == "PENDING":
            result.status = "PASS"

    except Exception as e:
        result.status = "ERROR"
        result.error = traceback.format_exc()
    finally:
        result.duration_ms = int((time.time() - start) * 1000)

    return result


def run_test_static(test: dict) -> TestResult:
    """Mark test as requiring manual execution (no emulator available)."""
    result = TestResult(test["id"], test["title"])
    result.status = "MANUAL_REQUIRED"
    result.steps_log = [f"Step {i+1}: {s.get('action', s)}" for i, s in enumerate(test.get("steps", []))]
    result.assertions = [{"check": a, "passed": None} for a in test.get("assertions", [])]
    result.duration_ms = 0
    return result


# ─────────────────────────────────────────
#  Main
# ─────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apk", help="Path to APK file")
    parser.add_argument("--tests", help="Path to tests.json", default="tests.json")
    parser.add_argument("--output", help="Output directory", default="results")
    parser.add_argument("--device", help="Device/emulator ID", default=None)
    parser.add_argument("--suite", help="Test suite filter: smoke|functional|all", default="all")
    parser.add_argument("--static", action="store_true", help="Static mode — no emulator")
    args = parser.parse_args()

    Path(args.output).mkdir(parents=True, exist_ok=True)

    # Load tests
    if not os.path.exists(args.tests):
        print(f"❌ Tests file not found: {args.tests}")
        print("   Generate tests first with Claude's Phase 2-3 workflow.")
        return

    with open(args.tests) as f:
        tests_data = json.load(f)

    tests = tests_data.get("tests", tests_data) if isinstance(tests_data, dict) else tests_data

    # Filter by suite
    if args.suite != "all":
        tests = [t for t in tests if t.get("type", "").lower() == args.suite.lower()]

    print(f"\n🚀 Running {len(tests)} tests | Mode: {'STATIC' if args.static else 'AUTOMATED'}")
    print("=" * 60)

    results = []
    driver = None

    if not args.static and args.apk:
        try:
            print("📱 Connecting to device via Appium...")
            driver = create_driver(args.apk, args.device)
            print("✅ Device connected\n")
        except Exception as e:
            print(f"⚠️  Could not connect to device: {e}")
            print("   Falling back to STATIC mode.\n")
            driver = None

    for test in tests:
        test_id = test.get("id", "?")
        title = test.get("title", "Untitled")
        print(f"  {'▶' if driver else '📋'} {test_id}: {title}", end=" ", flush=True)

        if driver:
            result = run_test_automated(driver, test, args.output)
        else:
            result = run_test_static(test)

        results.append(result)

        status_icon = {"PASS": "✅", "FAIL": "❌", "ERROR": "💥",
                       "SKIP": "⏭️", "MANUAL_REQUIRED": "📋"}.get(result.status, "?")
        print(f"→ {status_icon} {result.status} ({result.duration_ms}ms)")

    if driver:
        try:
            driver.quit()
        except Exception:
            pass

    # Save raw results
    results_path = os.path.join(args.output, "results.json")
    summary = {
        "timestamp": datetime.datetime.now().isoformat(),
        "mode": "static" if not driver else "automated",
        "apk": args.apk,
        "total": len(results),
        "passed": sum(1 for r in results if r.status == "PASS"),
        "failed": sum(1 for r in results if r.status == "FAIL"),
        "errors": sum(1 for r in results if r.status == "ERROR"),
        "manual": sum(1 for r in results if r.status == "MANUAL_REQUIRED"),
        "tests": [r.to_dict() for r in results],
    }

    with open(results_path, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print(f"📊 RESULTS: {summary['passed']} passed | {summary['failed']} failed | {summary['errors']} errors | {summary['manual']} manual")
    print(f"💾 Saved to: {results_path}")
    print(f"\n📄 Generate report: python3 scripts/generate_report.py --results {args.output}/ --output test_report.html")


if __name__ == "__main__":
    main()