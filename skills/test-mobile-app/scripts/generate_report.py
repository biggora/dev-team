#!/usr/bin/env python3
"""
generate_report.py — Generate a rich HTML test report from results.json.
Usage: python3 generate_report.py --results results/ --output test_report.html
"""
import argparse
import json
import os
import datetime
from pathlib import Path

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mobile Test Report — {app_name}</title>
<style>
  :root {{
    --pass: #22c55e; --fail: #ef4444; --error: #f97316;
    --manual: #8b5cf6; --skip: #94a3b8; --bg: #0f172a;
    --card: #1e293b; --border: #334155; --text: #e2e8f0;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Inter', system-ui, sans-serif; background: var(--bg); color: var(--text); padding: 24px; }}
  h1 {{ font-size: 1.8rem; margin-bottom: 4px; color: #f8fafc; }}
  .subtitle {{ color: #94a3b8; margin-bottom: 24px; font-size: 0.9rem; }}
  .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 16px; margin-bottom: 32px; }}
  .stat-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 16px; text-align: center; }}
  .stat-card .number {{ font-size: 2.4rem; font-weight: 700; }}
  .stat-card .label {{ font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }}
  .pass {{ color: var(--pass); }} .fail {{ color: var(--fail); }}
  .error {{ color: var(--error); }} .manual {{ color: var(--manual); }}
  .skip {{ color: var(--skip); }}
  .progress-bar {{ height: 8px; border-radius: 4px; background: var(--border); overflow: hidden; margin-bottom: 32px; display: flex; }}
  .pb-pass {{ background: var(--pass); }} .pb-fail {{ background: var(--fail); }}
  .pb-error {{ background: var(--error); }} .pb-manual {{ background: var(--manual); }}
  .section-title {{ font-size: 1.1rem; font-weight: 600; margin-bottom: 16px; color: #f1f5f9; border-bottom: 1px solid var(--border); padding-bottom: 8px; }}
  .test-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; margin-bottom: 12px; overflow: hidden; }}
  .test-header {{ display: flex; align-items: center; gap: 12px; padding: 14px 16px; cursor: pointer; user-select: none; }}
  .test-header:hover {{ background: #263148; }}
  .status-badge {{ font-size: 0.7rem; font-weight: 700; padding: 3px 10px; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.05em; }}
  .badge-PASS {{ background: #14532d; color: var(--pass); }}
  .badge-FAIL {{ background: #7f1d1d; color: var(--fail); }}
  .badge-ERROR {{ background: #431407; color: var(--error); }}
  .badge-MANUAL_REQUIRED {{ background: #2e1065; color: var(--manual); }}
  .badge-SKIP {{ background: #1e293b; color: var(--skip); }}
  .test-id {{ color: #64748b; font-family: monospace; font-size: 0.85rem; }}
  .test-title {{ font-size: 0.95rem; flex: 1; }}
  .duration {{ color: #64748b; font-size: 0.8rem; }}
  .test-body {{ display: none; padding: 0 16px 16px; border-top: 1px solid var(--border); }}
  .test-body.open {{ display: block; }}
  .steps {{ margin-top: 12px; }}
  .step {{ font-size: 0.85rem; color: #94a3b8; margin-bottom: 4px; padding-left: 12px; border-left: 2px solid var(--border); }}
  .assertions {{ margin-top: 12px; }}
  .assertion {{ display: flex; align-items: center; gap: 8px; font-size: 0.85rem; margin-bottom: 4px; }}
  .assert-pass {{ color: var(--pass); }} .assert-fail {{ color: var(--fail); }} .assert-null {{ color: var(--manual); }}
  .error-box {{ background: #1c0a0a; border: 1px solid #7f1d1d; border-radius: 6px; padding: 10px; margin-top: 10px; font-family: monospace; font-size: 0.8rem; color: #fca5a5; white-space: pre-wrap; }}
  .issues {{ margin-top: 12px; }}
  .issue {{ display: flex; gap: 8px; font-size: 0.85rem; margin-bottom: 4px; }}
  .severity-Critical {{ color: var(--fail); font-weight: 600; }}
  .severity-Major {{ color: var(--error); font-weight: 600; }}
  .severity-Minor {{ color: #fbbf24; }}
  .screenshot {{ margin-top: 12px; }}
  .screenshot img {{ max-width: 200px; border-radius: 8px; border: 1px solid var(--border); }}
  .issues-section {{ margin-top: 32px; }}
  .issue-card {{ background: var(--card); border-left: 4px solid var(--fail); border-radius: 6px; padding: 12px 16px; margin-bottom: 8px; }}
  .footer {{ margin-top: 48px; color: #475569; font-size: 0.8rem; text-align: center; }}
  .toggle-icon {{ color: #64748b; transition: transform 0.2s; }}
  .open .toggle-icon {{ transform: rotate(180deg); }}
</style>
</head>
<body>
<h1>📱 Mobile Test Report</h1>
<div class="subtitle">App: {app_name} &nbsp;|&nbsp; {timestamp} &nbsp;|&nbsp; Mode: {mode}</div>

<div class="summary-grid">
  <div class="stat-card"><div class="number">{total}</div><div class="label">Total</div></div>
  <div class="stat-card"><div class="number pass">{passed}</div><div class="label">Passed</div></div>
  <div class="stat-card"><div class="number fail">{failed}</div><div class="label">Failed</div></div>
  <div class="stat-card"><div class="number error">{errors}</div><div class="label">Errors</div></div>
  <div class="stat-card"><div class="number manual">{manual}</div><div class="label">Manual</div></div>
  <div class="stat-card"><div class="number" style="color:#60a5fa">{pass_rate}%</div><div class="label">Pass Rate</div></div>
</div>

<div class="progress-bar">
  {progress_bars}
</div>

<div class="section-title">Test Results</div>
{test_cards}

{issues_html}

<div class="footer">Generated by Mobile App Testing Skill &nbsp;•&nbsp; {timestamp}</div>

<script>
document.querySelectorAll('.test-header').forEach(h => {{
  h.addEventListener('click', () => {{
    const body = h.nextElementSibling;
    body.classList.toggle('open');
    h.classList.toggle('open');
  }});
}});
</script>
</body>
</html>"""


def build_test_card(test: dict) -> str:
    status = test.get("status", "UNKNOWN")
    duration = test.get("duration_ms", 0)

    steps_html = ""
    if test.get("steps_log"):
        steps_html = '<div class="steps">' + "".join(
            f'<div class="step">{s}</div>' for s in test["steps_log"]
        ) + "</div>"

    assertions_html = ""
    if test.get("assertions"):
        def ass_icon(a):
            if a.get("passed") is True: return '<span class="assert-pass">✅</span>'
            if a.get("passed") is False: return '<span class="assert-fail">❌</span>'
            return '<span class="assert-null">📋</span>'
        assertions_html = '<div class="assertions"><strong>Assertions:</strong>' + "".join(
            f'<div class="assertion">{ass_icon(a)}<span>{a["check"]}</span></div>'
            for a in test["assertions"]
        ) + "</div>"

    error_html = ""
    if test.get("error"):
        error_html = f'<div class="error-box">{test["error"]}</div>'

    issues_html = ""
    if test.get("issues_found"):
        issues_html = '<div class="issues"><strong>Issues:</strong>' + "".join(
            f'<div class="issue"><span class="severity-{i["severity"]}">[{i["severity"]}]</span><span>{i["description"]}</span></div>'
            for i in test["issues_found"]
        ) + "</div>"

    screenshot_html = ""
    if test.get("screenshot_path") and os.path.exists(test["screenshot_path"]):
        screenshot_html = f'<div class="screenshot"><strong>Screenshot:</strong><br><img src="{test["screenshot_path"]}" alt="screenshot"></div>'

    return f"""
<div class="test-card">
  <div class="test-header">
    <span class="test-id">{test.get("test_id", "?")}</span>
    <span class="status-badge badge-{status}">{status.replace("_", " ")}</span>
    <span class="test-title">{test.get("title", "")}</span>
    <span class="duration">{duration}ms</span>
    <span class="toggle-icon">▼</span>
  </div>
  <div class="test-body">
    {steps_html}
    {assertions_html}
    {error_html}
    {issues_html}
    {screenshot_html}
  </div>
</div>"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default="results/", help="Results directory with results.json")
    parser.add_argument("--output", default="test_report.html")
    args = parser.parse_args()

    results_file = os.path.join(args.results, "results.json")
    if not os.path.exists(results_file):
        # Try direct path
        if os.path.exists(args.results) and args.results.endswith(".json"):
            results_file = args.results
        else:
            print(f"❌ results.json not found at {results_file}")
            return

    with open(results_file) as f:
        data = json.load(f)

    total = data.get("total", 0)
    passed = data.get("passed", 0)
    failed = data.get("failed", 0)
    errors = data.get("errors", 0)
    manual = data.get("manual", 0)

    pass_rate = round(passed / total * 100) if total > 0 else 0

    def pct(n):
        return round(n / total * 100) if total > 0 else 0

    progress_bars = (
        f'<div class="pb-pass" style="width:{pct(passed)}%"></div>'
        f'<div class="pb-fail" style="width:{pct(failed)}%"></div>'
        f'<div class="pb-error" style="width:{pct(errors)}%"></div>'
        f'<div class="pb-manual" style="width:{pct(manual)}%"></div>'
    )

    tests = data.get("tests", [])
    test_cards = "".join(build_test_card(t) for t in tests)

    # Collect all issues
    all_issues = []
    for t in tests:
        for issue in t.get("issues_found", []):
            all_issues.append({**issue, "test": t.get("test_id"), "title": t.get("title")})

    issues_html = ""
    if all_issues:
        critical = [i for i in all_issues if i.get("severity") == "Critical"]
        major = [i for i in all_issues if i.get("severity") == "Major"]
        minor = [i for i in all_issues if i.get("severity") == "Minor"]

        def render_issues(issues_list):
            return "".join(
                f'<div class="issue-card"><strong>[{i["severity"]}]</strong> {i["description"]} '
                f'<span style="color:#64748b">— {i.get("test","")}: {i.get("title","")}</span></div>'
                for i in issues_list
            )

        issues_html = f"""
<div class="issues-section">
  <div class="section-title">🐛 Issues Found ({len(all_issues)})</div>
  {render_issues(critical + major + minor)}
</div>"""

    apk = data.get("apk") or "Unknown App"
    app_name = Path(apk).stem if apk else "Unknown"
    timestamp = data.get("timestamp", datetime.datetime.now().isoformat())[:19].replace("T", " ")
    mode = data.get("mode", "unknown").upper()

    html = HTML_TEMPLATE.format(
        app_name=app_name, timestamp=timestamp, mode=mode,
        total=total, passed=passed, failed=failed, errors=errors,
        manual=manual, pass_rate=pass_rate,
        progress_bars=progress_bars, test_cards=test_cards,
        issues_html=issues_html,
    )

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Report generated: {args.output}")
    print(f"   {passed}/{total} tests passed ({pass_rate}%), {len(all_issues)} issues found")


if __name__ == "__main__":
    main()