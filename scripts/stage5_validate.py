#!/usr/bin/env python3
"""Stage 5: non-destructive end-to-end reconciliation of local stage outputs.

Compares the exception CSV with the current SQLite detection result, the five
Power BI CSVs with an independently regenerated export in a temporary directory,
and the planted baseline to report a transparent precision/recall calculation.

Does NOT contact Gmail, OneDrive, Power Automate, or the live Power BI service.
"""
from __future__ import annotations
import argparse
import csv
import json
import sqlite3
import sys
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from detect_exceptions import detect_findings  # noqa: E402
from export_powerbi import export_tables  # noqa: E402

RENAME = {'unapproved_large_purchase':'completed_payment_without_approval'}
FILENAMES = ['FactRequests.csv', 'FactPayments.csv', 'FactExceptions.csv', 'DimSuppliers.csv', 'DimDates.csv']


def read(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def normalized(rows, scenario_key, ids_key):
    return {(RENAME.get(r[scenario_key], r[scenario_key]), tuple(sorted(r[ids_key].split(';')))) for r in rows}


def validate():
    problems = []
    required = [ROOT / 'grc_stage1.sqlite', ROOT / 'output/exceptions.csv', ROOT / 'data/ground_truth_FOR_TESTS_ONLY.csv']
    required += [ROOT / 'powerbi/data' / n for n in FILENAMES]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError('Missing prerequisites: ' + ', '.join(missing))
    exceptions = read(ROOT / 'output/exceptions.csv')
    truth = read(ROOT / 'data/ground_truth_FOR_TESTS_ONLY.csv')
    expected, found = normalized(truth, 'scenario', 'record_ids'), normalized(exceptions, 'exception_type', 'reference_ids')
    tp, fp, fn = len(expected & found), len(found - expected), len(expected - found)
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    if fp or fn:
        problems.append(f'Planted-case mismatch: unexpected={fp}, missed={fn}')
    with closing(sqlite3.connect(ROOT / 'grc_stage1.sqlite')) as conn:
        if conn.execute('PRAGMA foreign_key_check').fetchall():
            problems.append('SQLite foreign key violations')
        current = detect_findings(conn)
        cols = ('finding_id', 'rule_id', 'exception_type', 'reference_ids', 'severity', 'status', 'related_amount_lkr')
        key = lambda rows: sorted(tuple(str(r.get(c, '')) for c in cols) for r in rows)
        if key(current) != key(exceptions):
            problems.append('output/exceptions.csv differs from current SQLite detection output')
        with TemporaryDirectory() as temp:
            counts = export_tables(conn, exceptions, Path(temp))
            for filename in FILENAMES:
                actual_path, expected_path = ROOT / 'powerbi/data' / filename, Path(temp) / filename
                if read(actual_path) != read(expected_path):
                    problems.append(f'powerbi/data/{filename} differs from expected current export; rerun export_powerbi.py')
    counts_current = {name: len(read(ROOT / 'powerbi/data' / name)) for name in FILENAMES}
    findings = read(ROOT / 'powerbi/data/FactExceptions.csv')
    totals = {
        'purchase_requests': counts_current['FactRequests.csv'],
        'payments': counts_current['FactPayments.csv'],
        'findings': counts_current['FactExceptions.csv'],
        'high_risk_findings': sum(r['severity'] == 'High' for r in findings),
        'open_findings': sum(r['status'] == 'Open' for r in findings),
        'medium_risk_findings': sum(r['severity'] == 'Medium' for r in findings),
    }
    baseline = {'purchase_requests':20,'payments':21,'findings':4,'high_risk_findings':3,'open_findings':4,'medium_risk_findings':1}
    for name, value in baseline.items():
        if totals[name] != value:
            problems.append(f'Baseline change: {name} expected {value}, saw {totals[name]}')
    return {
        'generated_utc': datetime.now(timezone.utc).isoformat(),
        'scope':'Local synthetic baseline only; cloud behavior requires manual tests',
        'result': 'PASS' if not problems else 'FAIL',
        'counts': totals, 'planted_case_tp':tp, 'planted_case_fp':fp,
        'planted_case_fn':fn, 'planted_case_precision':round(precision,4),
        'planted_case_recall':round(recall,4), 'problems':problems,
    }


def main():
    p = argparse.ArgumentParser(description='Stage 5 local GRC validation; read-only')
    p.add_argument('--json', type=Path, default=ROOT / 'docs' / 'stage5_validation_result.json')
    args = p.parse_args()
    try:
        result = validate()
    except (OSError, ValueError, sqlite3.Error) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        raise SystemExit(1)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f"Stage 5 validation: {result['result']}")
    for key, count in result['counts'].items():
        print(f'  {key}: {count}')
    print(f"  Planted-case TP={result['planted_case_tp']}, FP={result['planted_case_fp']}, FN={result['planted_case_fn']}")
    print(f"  Synthetic fixture precision={result['planted_case_precision']:.0%}, recall={result['planted_case_recall']:.0%}")
    for problem in result['problems']:
        print('  ISSUE:', problem)
    print(f'  Evidence written to {args.json}')
    print('Important: these metrics do not establish accuracy on real-world data.')
    if result['problems']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
