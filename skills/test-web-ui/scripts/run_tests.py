#!/usr/bin/env python3
"""
Web Tester - Test Execution Engine
Runs a structured test plan against a website using Playwright.
"""

import json
import os
import sys
import time
import argparse
import base64
from datetime import datetime
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("ERROR: playwright not installed. Install with:")
    print("  pip install playwright && playwright install chromium")
    sys.exit(1)


def encode_screenshot(path):
    """Encode screenshot as base64 for embedding in report."""
    try:
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception:
        return None


def run_single_test(page, test_case, screenshot_dir, base_url):
    """Execute a single test case and return result dict."""
    tc_id = test_case.get('id', 'UNKNOWN')
    name = test_case.get('name', 'Unnamed test')
    steps = test_case.get('steps', [])
    assertions = test_case.get('assertions', [])
    target_path = test_case.get('path', '/')
    mobile = test_case.get('mobile', False)

    result = {
        'id': tc_id,
        'name': name,
        'status': 'PASS',
        'errors': [],
        'warnings': [],
        'console_errors': [],
        'duration_ms': 0,
        'screenshot_before': None,
        'screenshot_after': None,
        'assertions_total': len(assertions),
        'assertions_passed': 0,
    }

    start_time = time.time()

    # Collect console errors
    console_errors = []
    page.on('console', lambda msg: console_errors.append({
        'type': msg.type,
        'text': msg.text
    }) if msg.type in ('error', 'warning') else None)

    try:
        # Navigate to target
        target_url = base_url.rstrip('/') + target_path
        page.goto(target_url, wait_until='domcontentloaded', timeout=15000)
        page.wait_for_load_state('networkidle', timeout=10000)
    except PlaywrightTimeout:
        result['status'] = 'FAIL'
        result['errors'].append(f'Page load timeout: {target_url}')
        result['duration_ms'] = int((time.time() - start_time) * 1000)
        return result
    except Exception as e:
        result['status'] = 'FAIL'
        result['errors'].append(f'Navigation error: {str(e)}')
        result['duration_ms'] = int((time.time() - start_time) * 1000)
        return result

    # Screenshot before interactions
    before_path = os.path.join(screenshot_dir, f'{tc_id}_before.png')
    try:
        page.screenshot(path=before_path, full_page=True, timeout=5000)
        result['screenshot_before'] = before_path
    except Exception:
        pass

    # Execute steps (interactions)
    for step in steps:
        action = step.get('action', '')
        selector = step.get('selector', '')
        value = step.get('value', '')
        try:
            if action == 'click':
                page.locator(selector).first.click(timeout=5000)
                page.wait_for_load_state('networkidle', timeout=8000)
            elif action == 'fill':
                page.locator(selector).first.fill(value, timeout=5000)
            elif action == 'wait_for':
                page.wait_for_selector(selector, timeout=8000)
            elif action == 'scroll':
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(0.5)
            elif action == 'hover':
                page.locator(selector).first.hover(timeout=5000)
        except Exception as e:
            result['warnings'].append(f'Step [{action} {selector}] failed: {str(e)[:100]}')

    # Screenshot after interactions
    if steps:
        after_path = os.path.join(screenshot_dir, f'{tc_id}_after.png')
        try:
            page.screenshot(path=after_path, full_page=True, timeout=5000)
            result['screenshot_after'] = after_path
        except Exception:
            pass

    # Run assertions
    for assertion in assertions:
        atype = assertion.get('type', '')
        selector = assertion.get('selector', '')
        expected = assertion.get('expected', '')
        description = assertion.get('description', f'{atype} {selector}')

        try:
            passed = False

            if atype == 'visible':
                passed = page.locator(selector).first.is_visible()
            elif atype == 'not_visible':
                passed = not page.locator(selector).first.is_visible()
            elif atype == 'text_contains':
                text = page.locator(selector).first.text_content(timeout=5000) or ''
                passed = expected.lower() in text.lower()
            elif atype == 'title_not_empty':
                passed = bool(page.title().strip())
            elif atype == 'title_contains':
                passed = expected.lower() in page.title().lower()
            elif atype == 'count_gt':
                count = page.locator(selector).count()
                passed = count > int(expected)
            elif atype == 'count_eq':
                count = page.locator(selector).count()
                passed = count == int(expected)
            elif atype == 'url_contains':
                passed = expected in page.url
            elif atype == 'no_console_errors':
                passed = not any(e['type'] == 'error' for e in console_errors)
            elif atype == 'images_loaded':
                # Check that all images have naturalWidth > 0 (loaded)
                broken = page.evaluate("""
                    () => Array.from(document.images)
                         .filter(img => img.naturalWidth === 0 && img.src && !img.src.startsWith('data:'))
                         .map(img => img.src)
                """)
                passed = len(broken) == 0
                if not passed:
                    result['warnings'].append(f'Broken images: {broken[:3]}')
            elif atype == 'has_alt_text':
                missing_alt = page.evaluate("""
                    () => Array.from(document.images)
                         .filter(img => !img.alt || img.alt.trim() === '')
                         .length
                """)
                passed = missing_alt == 0
                if not passed:
                    result['warnings'].append(f'{missing_alt} images missing alt text')
            elif atype == 'clickable':
                el = page.locator(selector).first
                passed = el.is_visible() and el.is_enabled()
            elif atype == 'attribute_equals':
                attr_name = assertion.get('attribute', '')
                val = page.locator(selector).first.get_attribute(attr_name) or ''
                passed = val == expected
            else:
                result['warnings'].append(f'Unknown assertion type: {atype}')
                continue

            if passed:
                result['assertions_passed'] += 1
            else:
                result['status'] = 'FAIL'
                result['errors'].append(f'FAIL: {description}')

        except Exception as e:
            result['status'] = 'FAIL'
            result['errors'].append(f'ERROR in [{description}]: {str(e)[:120]}')

    # Collect console errors
    result['console_errors'] = [e for e in console_errors if e['type'] == 'error']
    if result['console_errors'] and result['status'] == 'PASS':
        # Downgrade to WARNING, not FAIL — console errors are informational
        result['warnings'].append(f"{len(result['console_errors'])} JS console error(s) detected")

    result['duration_ms'] = int((time.time() - start_time) * 1000)
    return result


def run_tests(url, test_plan_path, output_dir):
    """Main test runner."""
    os.makedirs(output_dir, exist_ok=True)
    screenshot_dir = os.path.join(output_dir, 'screenshots')
    os.makedirs(screenshot_dir, exist_ok=True)

    with open(test_plan_path, 'r', encoding='utf-8') as f:
        test_plan = json.load(f)

    test_cases = test_plan.get('test_cases', [])
    meta = test_plan.get('meta', {})

    print(f"\n{'='*60}")
    print(f"  WEB TESTER — Execution Engine")
    print(f"  URL: {url}")
    print(f"  Tests: {len(test_cases)}")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    all_results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(args=[
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
        ])

        for tc in test_cases:
            mobile = tc.get('mobile', False)
            if mobile:
                context = browser.new_context(
                    viewport={'width': 390, 'height': 844},
                    is_mobile=True,
                    user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)'
                )
            else:
                context = browser.new_context(
                    viewport={'width': 1280, 'height': 800}
                )

            page = context.new_page()

            print(f"  [{tc.get('id', '?')}] {tc.get('name', '?')} ...", end=' ', flush=True)
            result = run_single_test(page, tc, screenshot_dir, url)
            all_results.append(result)

            status_icon = '✓' if result['status'] == 'PASS' else '✗'
            print(f"{status_icon} {result['status']} ({result['duration_ms']}ms)")
            for err in result['errors']:
                print(f"         ↳ {err}")

            context.close()

        browser.close()

    # Summary
    total = len(all_results)
    passed = sum(1 for r in all_results if r['status'] == 'PASS')
    failed = sum(1 for r in all_results if r['status'] == 'FAIL')
    skipped = sum(1 for r in all_results if r['status'] == 'SKIP')

    print(f"\n{'='*60}")
    print(f"  RESULTS: {passed}/{total} passed | {failed} failed | {skipped} skipped")
    print(f"  Pass rate: {int(passed/total*100) if total else 0}%")
    print(f"{'='*60}\n")

    # Save results
    output = {
        'meta': {
            **meta,
            'url': url,
            'run_at': datetime.now().isoformat(),
            'total': total,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'pass_rate': int(passed/total*100) if total else 0,
        },
        'results': all_results
    }

    results_path = os.path.join(output_dir, 'results.json')
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"  Results saved: {results_path}")
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Web Tester - Execution Engine')
    parser.add_argument('--url', required=True, help='Base URL to test')
    parser.add_argument('--test-plan', required=True, help='Path to test_plan.json')
    parser.add_argument('--output', default='test_results', help='Output directory')
    args = parser.parse_args()

    run_tests(args.url, args.test_plan, args.output)