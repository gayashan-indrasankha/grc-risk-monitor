"""Stage 5 read-only regression tests using disposable copies of synthetic SQLite data.

All new test records and mutations stay in a temporary copy. Windows-safe closing.
"""
import sqlite3
import sys
import unittest
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from detect_exceptions import detect_findings  # noqa: E402


class Stage5DetectionScenarios(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / 'scenario.sqlite'
        source = ROOT / 'grc_stage1.sqlite'
        if not source.is_file():
            self.fail('Missing grc_stage1.sqlite. See README: recreate baseline first.')
        with closing(sqlite3.connect(source)) as original, closing(sqlite3.connect(self.db)) as copy:
            original.backup(copy)

    def edit(self, sql, parameters=()):
        with closing(sqlite3.connect(self.db)) as conn:
            with conn:
                conn.execute(sql, parameters)

    def findings(self):
        with closing(sqlite3.connect(self.db)) as conn:
            return detect_findings(conn)

    def has(self, rule, ids=None):
        for f in self.findings():
            if f['rule_id'] == rule and (ids is None or f['reference_ids'] == ids):
                return True
        return False

    def test_a01_baseline_four_distinct_planted_findings(self):
        fs = self.findings()
        self.assertEqual(len(fs), 4)
        self.assertEqual({f['rule_id'] for f in fs}, {'R01', 'R02', 'R03', 'R04'})
        self.assertEqual(sum(f['severity'] == 'High' for f in fs), 3)

    def test_a02_cancelled_extra_payment_does_not_trigger_duplicate(self):
        self.edit('INSERT INTO payments VALUES (?,?,?,?,?)', ('PAY-S5-01', 'INV-0001', '2026-10-16', 22000, 'Cancelled'))
        self.assertFalse(any(f['invoice_id'] == 'INV-0001' and f['rule_id'] == 'R01' for f in self.findings()))

    def test_a03_partial_extra_payment_does_not_trigger_full_duplicate(self):
        self.edit('INSERT INTO payments VALUES (?,?,?,?,?)', ('PAY-S5-02', 'INV-0001', '2026-10-16', 500, 'Completed'))
        self.assertFalse(any(f['invoice_id'] == 'INV-0001' and f['rule_id'] == 'R01' for f in self.findings()))

    def test_a04_new_full_completed_payment_triggers_duplicate(self):
        self.edit('INSERT INTO payments VALUES (?,?,?,?,?)', ('PAY-S5-03', 'INV-0001', '2026-10-16', 22000, 'Completed'))
        self.assertTrue(any(f['invoice_id'] == 'INV-0001' and f['rule_id'] == 'R01' for f in self.findings()))

    def test_a05_pending_payment_is_not_a_paid_without_approval_exception(self):
        self.edit("UPDATE payments SET payment_status = 'Pending' WHERE invoice_id = 'INV-0006'")
        self.assertFalse(self.has('R02', 'PR-0006'))

    def test_a06_missing_manager_approval_triggers_role_exception(self):
        self.edit("UPDATE purchase_requests SET approved_by = NULL WHERE request_id = 'PR-0014'")
        self.assertTrue(self.has('R03', 'PR-0014'))

    def test_a07_correct_manager_approval_clears_role_exception(self):
        self.edit("UPDATE purchase_requests SET approved_by = 'EMP-003' WHERE request_id = 'PR-0014'")
        self.assertFalse(self.has('R03', 'PR-0014'))

    def test_a08_exactly_at_threshold_is_not_above_threshold(self):
        self.edit("UPDATE purchase_requests SET amount = 100000 WHERE request_id = 'PR-0014'")
        self.assertFalse(self.has('R03', 'PR-0014'))

    def test_a09_split_outside_three_day_window_is_not_flagged(self):
        self.edit("UPDATE purchase_requests SET requested_on = '2026-11-20' WHERE request_id = 'PR-0010'")
        self.assertFalse(self.has('R04', 'PR-0009;PR-0010'))

    def test_a10_split_pair_below_threshold_is_not_flagged(self):
        self.edit("UPDATE purchase_requests SET amount = 39000 WHERE request_id = 'PR-0010'")
        self.assertFalse(self.has('R04', 'PR-0009;PR-0010'))

    def test_a11_detector_is_read_only_on_disposable_database(self):
        with closing(sqlite3.connect(self.db)) as conn:
            before = conn.total_changes
            detect_findings(conn)
            self.assertEqual(conn.total_changes, before)


if __name__ == '__main__':
    unittest.main(verbosity=2)
