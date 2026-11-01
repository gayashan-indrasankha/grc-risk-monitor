"""Stage 5 data-quality and Power BI export checks. No modification of inputs."""
import csv
import sqlite3
import sys
import unittest
from contextlib import closing
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from detect_exceptions import detect_findings  # noqa: E402
from export_powerbi import current_exception_matches  # noqa: E402


def csv_rows(filename):
    path = ROOT / filename
    with path.open(encoding='utf-8-sig', newline='') as file:
        return list(csv.DictReader(file))


class Stage5DataQuality(unittest.TestCase):
    def test_b01_foreign_keys_and_positive_payment_amounts(self):
        with closing(sqlite3.connect(ROOT / 'grc_stage1.sqlite')) as c:
            self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(), [])
            self.assertEqual(c.execute('SELECT COUNT(*) FROM payments WHERE paid_amount <= 0').fetchone()[0], 0)

    def test_b02_exception_export_matches_current_database(self):
        with closing(sqlite3.connect(ROOT / 'grc_stage1.sqlite')) as c:
            self.assertTrue(current_exception_matches(c, csv_rows('output/exceptions.csv')))

    def test_b03_finding_identifiers_unique_and_required_values_present(self):
        rows = csv_rows('output/exceptions.csv')
        ids = [r['finding_id'] for r in rows]
        self.assertEqual(len(set(ids)), len(ids))
        for r in rows:
            for key in ('rule_id', 'exception_type', 'severity', 'evidence', 'recommended_action', 'supplier_id'):
                self.assertTrue(r[key].strip(), f'Missing {key} in {r["finding_id"]}')

    def test_b04_expected_baseline_counts(self):
        self.assertEqual(len(csv_rows('powerbi/data/FactRequests.csv')), 20)
        self.assertEqual(len(csv_rows('powerbi/data/FactPayments.csv')), 21)
        findings = csv_rows('powerbi/data/FactExceptions.csv')
        self.assertEqual(len(findings), 4)
        self.assertEqual(sum(r['severity'] == 'High' for r in findings), 3)
        self.assertEqual(sum(r['status'] == 'Open' for r in findings), 4)

    def test_b05_suppliers_and_dates_reference_valid_dimensions(self):
        suppliers = {r['supplier_id'] for r in csv_rows('powerbi/data/DimSuppliers.csv')}
        dates = {r['date'] for r in csv_rows('powerbi/data/DimDates.csv')}
        for dataset, field in (
            ('powerbi/data/FactRequests.csv', 'requested_on'),
            ('powerbi/data/FactPayments.csv', 'paid_on'),
            ('powerbi/data/FactExceptions.csv', 'event_date'),
        ):
            for r in csv_rows(dataset):
                self.assertIn(r['supplier_id'], suppliers)
                self.assertIn(r[field], dates)
                date.fromisoformat(r[field])

    def test_b06_related_amounts_not_negative(self):
        for row in csv_rows('powerbi/data/FactExceptions.csv'):
            self.assertGreater(float(row['related_amount_lkr']), 0)

    def test_b07_table_keys_are_unique(self):
        for dataset, key in (
            ('FactRequests.csv','request_id'), ('FactPayments.csv','payment_id'),
            ('FactExceptions.csv','finding_id'), ('DimSuppliers.csv','supplier_id'),
            ('DimDates.csv','date')
        ):
            vals = [r[key] for r in csv_rows('powerbi/data/' + dataset)]
            self.assertEqual(len(vals), len(set(vals)), f'Duplicate {key} in {dataset}')


if __name__ == '__main__':
    unittest.main(verbosity=2)
