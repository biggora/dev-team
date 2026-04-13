#!/usr/bin/env python3
"""
Web Tester - HTML Report Generator
Produces a self-contained HTML QA report from test results.
"""

import json
import os
import sys
import base64
import argparse
from datetime import datetime
from pathlib import Path


def load_screenshot_b64(path):
    if not path or not os.path.exists(path):
        return None
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def status_badge(status):
    colors = {'PASS': '#22c55e', 'FAIL': '#ef4444', 'SKIP': '#f59e0b', 'WARN': '#f97316'}
    color = colors.get(status, '#6b7280')
    return f'<span style="background:{color};color:#fff;padding:2px 10px;border-radius:4px;font-size:12px;font-weight:700">{status}</span>'


def generate_report(results_path, screenshots_dir, output_path):
    with open(results_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    meta = data['meta']
    results = data['results']

    total = meta.get('total', len(results))
    passed = meta.get('passed', 0)
    failed = meta.get('failed', 0)
    skipped = meta.get('skipped', 0)
    pass_rate = meta.get('pass_rate', 0)
    url = meta.get('url', 'N/A')
    run_at = meta.get('run_at', datetime.now().isoformat())
    site_name = meta.get('site_name', url)

    # Status color for header
    rate_color = '#22c55e' if pass_rate >= 80 else '#f97316' if pass_rate >= 50 else '#ef4444'

    # Build test rows
    rows_html = ''
    screenshots_html = ''

    for r in results:
        status = r.get('status', 'UNKNOWN')
        errors = r.get('errors', [])
        warnings = r.get('warnings', [])
        console_errors = r.get('console_errors', [])
        duration = r.get('duration_ms', 0)
        assertions = r.get('assertions_total', 0)
        assertions_passed = r.get('assertions_passed', 0)

        error_text = '<br>'.join(f'❌ {e}' for e in errors)
        warning_text = '<br>'.join(f'⚠️ {w}' for w in warnings)
        detail_text = error_text + ('<br>' if error_text and warning_text else '') + warning_text
        if not detail_text:
            detail_text = '—'

        rows_html += f"""
        <tr>
          <td style="font-family:monospace;font-size:12px;color:#64748b">{r.get('id','')}</td>
          <td style="font-weight:500">{r.get('name','')}</td>
          <td style="text-align:center">{status_badge(status)}</td>
          <td style="text-align:center;color:#64748b;font-size:13px">{assertions_passed}/{assertions}</td>
          <td style="text-align:center;color:#64748b;font-size:13px">{duration}ms</td>
          <td style="font-size:12px;color:#64748b;max-width:300px">{detail_text}</td>
        </tr>
        """

        # Screenshots section
        before_b64 = load_screenshot_b64(r.get('screenshot_before'))
        after_b64 = load_screenshot_b64(r.get('screenshot_after'))

        if before_b64 or after_b64:
            bg = '#fef2f2' if status == 'FAIL' else '#f0fdf4'
            screenshots_html += f"""
            <div style="border:1px solid #e2e8f0;border-radius:8px;padding:16px;margin-bottom:16px;background:{bg}">
              <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px">
                {status_badge(status)}
                <strong style="font-size:14px">{r.get('id','')} — {r.get('name','')}</strong>
              </div>
              """
            if errors:
                screenshots_html += f'<div style="color:#ef4444;font-size:12px;margin-bottom:10px">' + '<br>'.join(errors) + '</div>'

            screenshots_html += '<div style="display:flex;gap:16px;flex-wrap:wrap">'
            if before_b64:
                screenshots_html += f"""
                <div>
                  <div style="font-size:11px;color:#64748b;margin-bottom:4px;text-transform:uppercase;letter-spacing:0.5px">Before</div>
                  <img src="data:image/png;base64,{before_b64}" style="max-width:580px;width:100%;border:1px solid #e2e8f0;border-radius:4px">
                </div>"""
            if after_b64:
                screenshots_html += f"""
                <div>
                  <div style="font-size:11px;color:#64748b;margin-bottom:4px;text-transform:uppercase;letter-spacing:0.5px">After interaction</div>
                  <img src="data:image/png;base64,{after_b64}" style="max-width:580px;width:100%;border:1px solid #e2e8f0;border-radius:4px">
                </div>"""
            screenshots_html += '</div></div>'

    # Recommendations
    recs = []
    if failed > 0:
        failed_names = [r.get('name','') for r in results if r.get('status') == 'FAIL']
        recs.append(f"🔴 Fix {failed} failing test(s): {', '.join(failed_names[:3])}{'...' if len(failed_names) > 3 else ''}")
    console_err_total = sum(len(r.get('console_errors', [])) for r in results)
    if console_err_total > 0:
        recs.append(f"🟡 Resolve {console_err_total} JavaScript console error(s) to improve reliability")
    broken_img_tests = [r for r in results if any('broken image' in w.lower() for w in r.get('warnings', []))]
    if broken_img_tests:
        recs.append("🟡 Fix broken/unloaded images detected on the page")
    alt_warnings = [r for r in results if any('alt text' in w.lower() for w in r.get('warnings', []))]
    if alt_warnings:
        recs.append("🟡 Add missing alt text to images for accessibility compliance")
    if not recs:
        recs.append("✅ All critical checks passed. Site appears to be functioning correctly.")

    recs_html = ''.join(f'<li style="margin-bottom:8px">{r}</li>' for r in recs)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>QA Report — {site_name}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f8fafc; color: #1e293b; }}
  .header {{ background: linear-gradient(135deg, #1e293b 0%, #334155 100%); color: white; padding: 40px; }}
  .header h1 {{ font-size: 28px; font-weight: 700; margin-bottom: 4px; }}
  .header p {{ color: #94a3b8; font-size: 14px; }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 32px 24px; }}
  .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px; margin-bottom: 32px; }}
  .stat {{ background: white; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
  .stat .num {{ font-size: 36px; font-weight: 800; }}
  .stat .label {{ font-size: 13px; color: #64748b; margin-top: 4px; }}
  .section {{ background: white; border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
  .section h2 {{ font-size: 18px; font-weight: 600; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #f1f5f9; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
  th {{ background: #f8fafc; text-align: left; padding: 10px 12px; color: #64748b; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }}
  td {{ padding: 12px; border-top: 1px solid #f1f5f9; vertical-align: top; }}
  tr:hover td {{ background: #f8fafc; }}
  .progress-bar {{ height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden; margin-top: 8px; }}
  .progress-fill {{ height: 100%; background: {rate_color}; border-radius: 4px; width: {pass_rate}%; }}
</style>
</head>
<body>

<div class="header">
  <h1>🧪 QA Test Report</h1>
  <p>{site_name} &nbsp;|&nbsp; {run_at[:19].replace('T', ' ')} &nbsp;|&nbsp; {url}</p>
</div>

<div class="container">

  <div class="stats">
    <div class="stat">
      <div class="num" style="color:{rate_color}">{pass_rate}%</div>
      <div class="label">Pass Rate</div>
      <div class="progress-bar"><div class="progress-fill"></div></div>
    </div>
    <div class="stat">
      <div class="num">{total}</div>
      <div class="label">Total Tests</div>
    </div>
    <div class="stat">
      <div class="num" style="color:#22c55e">{passed}</div>
      <div class="label">Passed</div>
    </div>
    <div class="stat">
      <div class="num" style="color:#ef4444">{failed}</div>
      <div class="label">Failed</div>
    </div>
    <div class="stat">
      <div class="num" style="color:#f59e0b">{skipped}</div>
      <div class="label">Skipped</div>
    </div>
  </div>

  <div class="section">
    <h2>📋 Test Results</h2>
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Test Case</th>
          <th>Status</th>
          <th>Assertions</th>
          <th>Duration</th>
          <th>Details</th>
        </tr>
      </thead>
      <tbody>
        {rows_html}
      </tbody>
    </table>
  </div>

  <div class="section">
    <h2>💡 Recommendations</h2>
    <ul style="list-style:none;padding:0">
      {recs_html}
    </ul>
  </div>

  <div class="section">
    <h2>📸 Screenshots</h2>
    {screenshots_html if screenshots_html else '<p style="color:#64748b">No screenshots captured.</p>'}
  </div>

</div>
</body>
</html>"""

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ Report saved: {output_path}")
    return output_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', required=True)
    parser.add_argument('--screenshots', default='')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    generate_report(args.results, args.screenshots, args.output)