"""
test_framework.py
==================
Tests for the Python test_generator and report_publisher scripts.
Run with: pytest python_framework/test_framework.py -v
"""

import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from test_generator   import parse_functions, detect_namespace, build_test_file
from report_publisher import parse_junit, write_html_report, write_json_summary


# ── Fixtures ─────────────────────────────────────────────────────────────────

SAMPLE_HEADER = """\
#pragma once
namespace Calculator {
    double add(double a, double b);
    double subtract(double a, double b);
    double multiply(double a, double b);
    double divide(double a, double b);
    double power(double base, int exp);
    double factorial(int n);
    bool   isPrime(int n);
}
"""

SAMPLE_JUNIT_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
  <testsuite name="AddTest" tests="3" failures="0">
    <testcase name="PositiveNumbers" classname="AddTest" time="0.001"/>
    <testcase name="NegativeNumbers" classname="AddTest" time="0.001"/>
    <testcase name="Floats"          classname="AddTest" time="0.001"/>
  </testsuite>
  <testsuite name="DivideTest" tests="2" failures="1">
    <testcase name="BasicDivide"   classname="DivideTest" time="0.001"/>
    <testcase name="DivideByZero"  classname="DivideTest" time="0.001">
      <failure message="Expected exception was not thrown"/>
    </testcase>
  </testsuite>
</testsuites>
"""


# ── Generator tests ───────────────────────────────────────────────────────────

def test_parse_functions_finds_all_seven(tmp_path):
    h = tmp_path / "calc.h"
    h.write_text(SAMPLE_HEADER)
    fns = parse_functions(str(h))
    assert len(fns) == 7, f"Expected 7 functions, got {len(fns)}"


def test_parse_functions_names(tmp_path):
    h = tmp_path / "calc.h"
    h.write_text(SAMPLE_HEADER)
    names = [f['name'] for f in parse_functions(str(h))]
    assert 'add'       in names
    assert 'subtract'  in names
    assert 'multiply'  in names
    assert 'divide'    in names
    assert 'power'     in names
    assert 'factorial' in names
    assert 'isPrime'   in names


def test_detect_namespace(tmp_path):
    h = tmp_path / "calc.h"
    h.write_text(SAMPLE_HEADER)
    ns = detect_namespace(str(h))
    assert ns == 'Calculator'


def test_build_test_file_contains_gtest_include(tmp_path):
    h = tmp_path / "calc.h"
    h.write_text(SAMPLE_HEADER)
    fns = parse_functions(str(h))
    content = build_test_file(fns, 'Calculator')
    assert '#include <gtest/gtest.h>' in content


def test_build_test_file_contains_test_macros(tmp_path):
    h = tmp_path / "calc.h"
    h.write_text(SAMPLE_HEADER)
    fns = parse_functions(str(h))
    content = build_test_file(fns, 'Calculator')
    assert 'TEST(' in content
    assert 'EXPECT_DOUBLE_EQ' in content or 'EXPECT_EQ' in content


def test_build_test_file_has_main(tmp_path):
    h = tmp_path / "calc.h"
    h.write_text(SAMPLE_HEADER)
    fns = parse_functions(str(h))
    content = build_test_file(fns, 'Calculator')
    assert 'RUN_ALL_TESTS' in content


def test_build_test_file_has_auto_generated_comment(tmp_path):
    h = tmp_path / "calc.h"
    h.write_text(SAMPLE_HEADER)
    fns = parse_functions(str(h))
    content = build_test_file(fns, 'Calculator')
    assert 'AUTO-GENERATED' in content


# ── Reporter tests ────────────────────────────────────────────────────────────

def test_parse_junit_totals(tmp_path):
    x = tmp_path / "results.xml"
    x.write_text(SAMPLE_JUNIT_XML)
    r = parse_junit(str(x))
    assert r['total']  == 5
    assert r['passed'] == 4
    assert r['failed'] == 1


def test_parse_junit_pass_rate(tmp_path):
    x = tmp_path / "results.xml"
    x.write_text(SAMPLE_JUNIT_XML)
    r = parse_junit(str(x))
    pct = r['passed'] / r['total'] * 100
    assert pct == 80.0


def test_write_html_report_creates_file(tmp_path):
    x = tmp_path / "results.xml"
    x.write_text(SAMPLE_JUNIT_XML)
    r = parse_junit(str(x))
    out = str(tmp_path / "report.html")
    write_html_report(r, out)
    assert Path(out).exists()
    assert '<table' in Path(out).read_text()


def test_write_json_summary_structure(tmp_path):
    x = tmp_path / "results.xml"
    x.write_text(SAMPLE_JUNIT_XML)
    r = parse_junit(str(x))
    out = str(tmp_path / "summary.json")
    write_json_summary(r, out)
    data = json.loads(Path(out).read_text())
    for key in ('total', 'passed', 'failed', 'errors', 'skipped',
                'duration_seconds', 'pass_rate_pct', 'generated_at'):
        assert key in data, f"Missing key: {key}"
