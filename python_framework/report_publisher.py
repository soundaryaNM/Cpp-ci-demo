"""
report_publisher.py
====================
Reads the JUnit XML produced by ctest and generates:
  - A coloured terminal summary
  - An HTML report at python_framework/reports/report.html
  - A JSON summary at python_framework/reports/summary.json
  - Exits with code 1 if any test failed (so CI marks the step red)
"""

import sys
import json
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime


# ── Parse JUnit XML ──────────────────────────────────────────────────────────

def parse_junit(xml_path: str) -> dict:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Handle both <testsuites> wrapper and bare <testsuite>
    suites = root.findall('testsuite') if root.tag == 'testsuites' else [root]

    results = {
        'total':    0,
        'passed':   0,
        'failed':   0,
        'errors':   0,
        'skipped':  0,
        'duration': 0.0,
        'suites':   [],
    }

    for suite in suites:
        suite_data = {
            'name':  suite.get('name', 'Unknown'),
            'cases': [],
        }

        for case in suite.findall('testcase'):
            name = case.get('name', '?')
            classname = case.get('classname', '')
            duration = float(case.get('time', '0') or '0')
            failure = case.find('failure')
            error = case.find('error')
            skipped = case.find('skipped')

            if failure is not None:
                status = 'FAILED'
                message = failure.get('message', failure.text or '')
                results['failed'] += 1
            elif error is not None:
                status = 'ERROR'
                message = error.get('message', error.text or '')
                results['errors'] += 1
            elif skipped is not None:
                status = 'SKIPPED'
                message = ''
                results['skipped'] += 1
            else:
                status = 'PASSED'
                message = ''
                results['passed'] += 1

            results['total'] += 1
            results['duration'] += duration

            suite_data['cases'].append({
                'name':      f"{classname}.{name}" if classname else name,
                'status':    status,
                'duration':  round(duration, 4),
                'message':   message,
            })

        results['suites'].append(suite_data)

    results['duration'] = round(results['duration'], 3)
    return results


# ── Terminal summary ──────────────────────────────────────────────────────────

RESET = '\033[0m'
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BOLD = '\033[1m'
CYAN = '\033[96m'

STATUS_ICONS = {
    'PASSED':  f'{GREEN}✓{RESET}',
    'FAILED':  f'{RED}✗{RESET}',
    'ERROR':   f'{RED}!{RESET}',
    'SKIPPED': f'{YELLOW}~{RESET}',
}


def print_terminal_report(results: dict):
    print()
    print(f"{BOLD}{CYAN}{'═' * 60}{RESET}")
    print(f"{BOLD}{CYAN}  TEST RESULTS SUMMARY{RESET}")
    print(f"{BOLD}{CYAN}{'═' * 60}{RESET}")

    for suite in results['suites']:
        print(f"\n  Suite: {BOLD}{suite['name']}{RESET}")
        for case in suite['cases']:
            icon = STATUS_ICONS.get(case['status'], '?')
            dur = f"({case['duration']}s)" if case['duration'] > 0 else ''
            print(f"    {icon}  {case['name']}  {YELLOW}{dur}{RESET}")
            if case['message']:
                for line in case['message'].splitlines()[:3]:
                    print(f"         {RED}{line}{RESET}")

    print()
    total = results['total']
    passed = results['passed']
    failed = results['failed']
    errors = results['errors']
    skipped = results['skipped']
    dur = results['duration']

    pct = int(passed / total * 100) if total else 0
    bar_fill = '█' * (pct // 5)
    bar_empty = '░' * (20 - len(bar_fill))
    bar_color = GREEN if failed == 0 and errors == 0 else RED

    print(f"  {bar_color}{bar_fill}{bar_empty}{RESET}  {pct}%")
    print()
    print(f"  {GREEN}Passed : {passed}{RESET}   "
          f"{RED}Failed : {failed}{RESET}   "
          f"{RED}Errors : {errors}{RESET}   "
          f"{YELLOW}Skipped: {skipped}{RESET}")
    print(f"  Total  : {total}   Duration: {dur}s")
    print(f"{BOLD}{CYAN}{'═' * 60}{RESET}")
    print()


# ── HTML report ───────────────────────────────────────────────────────────────

def write_html_report(results: dict, output_path: str):
    rows = []
    for suite in results['suites']:
        for case in suite['cases']:
            color = {
                'PASSED':  '#d4edda',
                'FAILED':  '#f8d7da',
                'ERROR':   '#f8d7da',
                'SKIPPED': '#fff3cd',
            }.get(case['status'], '#fff')
            badge_color = {
                'PASSED':  '#28a745',
                'FAILED':  '#dc3545',
                'ERROR':   '#dc3545',
                'SKIPPED': '#ffc107',
            }.get(case['status'], '#999')

            msg = case['message'].replace('<', '&lt;').replace(
                '>', '&gt;') if case['message'] else ''
            msg_cell = f'<div style="font-size:12px;color:#555;margin-top:4px">{msg}</div>' if msg else ''

            rows.append(f"""
            <tr style="background:{color}">
                <td style="padding:8px 12px">{case['name']}</td>
                <td style="padding:8px 12px;text-align:center">
                    <span style="background:{badge_color};color:#fff;padding:2px 10px;
                    border-radius:12px;font-size:12px;font-weight:600">{case['status']}</span>
                </td>
                <td style="padding:8px 12px;text-align:right;color:#666">{case['duration']}s</td>
                <td style="padding:8px 12px">{msg_cell}</td>
            </tr>""")

    all_rows = "\n".join(rows)
    pct = int(results['passed'] / results['total']
              * 100) if results['total'] else 0
    bar_col = '#28a745' if results['failed'] == 0 and results['errors'] == 0 else '#dc3545'
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Test Report</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
         margin: 0; padding: 24px; background: #f5f5f5; color: #333; }}
  h1   {{ font-size: 22px; margin: 0 0 4px; }}
  .ts  {{ font-size: 13px; color: #888; margin-bottom: 20px; }}
  .stats {{ display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }}
  .stat  {{ background: #fff; border-radius: 8px; padding: 14px 20px;
            border: 1px solid #e0e0e0; min-width: 100px; }}
  .stat .n {{ font-size: 28px; font-weight: 700; margin-bottom: 2px; }}
  .stat .l {{ font-size: 12px; color: #888; text-transform: uppercase; }}
  .bar-bg {{ background: #e9ecef; border-radius: 8px; height: 10px;
             margin-bottom: 24px; overflow: hidden; }}
  .bar-fg {{ background: {bar_col}; height: 10px; width: {pct}%;
             border-radius: 8px; transition: width 0.5s; }}
  table  {{ width: 100%; border-collapse: collapse; background: #fff;
            border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,.08); }}
  th     {{ background: #343a40; color: #fff; padding: 10px 12px;
            text-align: left; font-size: 13px; font-weight: 600; }}
  tr:hover {{ filter: brightness(0.97); }}
</style>
</head>
<body>
<h1>Test Results</h1>
<div class="ts">Generated: {ts}</div>

<div class="stats">
  <div class="stat"><div class="n" style="color:#333">{results['total']}</div><div class="l">Total</div></div>
  <div class="stat"><div class="n" style="color:#28a745">{results['passed']}</div><div class="l">Passed</div></div>
  <div class="stat"><div class="n" style="color:#dc3545">{results['failed']}</div><div class="l">Failed</div></div>
  <div class="stat"><div class="n" style="color:#dc3545">{results['errors']}</div><div class="l">Errors</div></div>
  <div class="stat"><div class="n" style="color:#ffc107">{results['skipped']}</div><div class="l">Skipped</div></div>
  <div class="stat"><div class="n" style="color:#555">{results['duration']}s</div><div class="l">Duration</div></div>
</div>

<div class="bar-bg"><div class="bar-fg"></div></div>

<table>
  <thead>
    <tr>
      <th>Test case</th>
      <th style="text-align:center;width:100px">Status</th>
      <th style="text-align:right;width:80px">Time</th>
      <th>Message</th>
    </tr>
  </thead>
  <tbody>
    {all_rows}
  </tbody>
</table>
</body>
</html>"""

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(html)
    print(f"[reporter] HTML report written: {output_path}")


# ── JSON summary ──────────────────────────────────────────────────────────────

def write_json_summary(results: dict, output_path: str):
    summary = {
        'generated_at': datetime.now().isoformat(),
        'total':   results['total'],
        'passed':  results['passed'],
        'failed':  results['failed'],
        'errors':  results['errors'],
        'skipped': results['skipped'],
        'duration_seconds': results['duration'],
        'pass_rate_pct': round(results['passed'] / results['total'] * 100, 1)
        if results['total'] else 0,
    }
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(summary, indent=2))
    print(f"[reporter] JSON summary written: {output_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Test result publisher")
    parser.add_argument('--xml',  required=True,
                        help='Path to JUnit XML produced by ctest')
    parser.add_argument('--html', default='python_framework/reports/report.html',
                        help='Output path for HTML report')
    parser.add_argument('--json', default='python_framework/reports/summary.json',
                        help='Output path for JSON summary')
    args = parser.parse_args()

    if not Path(args.xml).exists():
        print(f"[reporter] ERROR: XML file not found: {args.xml}")
        sys.exit(1)

    print(f"[reporter] Parsing: {args.xml}")
    results = parse_junit(args.xml)

    print_terminal_report(results)
    write_html_report(results, args.html)
    write_json_summary(results, args.json)

    if results['failed'] > 0 or results['errors'] > 0:
        print(
            f"[reporter] PIPELINE FAIL — {results['failed']} failed, {results['errors']} errors")
        sys.exit(1)

    print(f"[reporter] All tests passed.")


if __name__ == '__main__':
    main()
