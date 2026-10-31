#!/usr/bin/env python3
"""Stage 2 detection tests (SQLite connections explicitly closed for Windows)."""
import sqlite3
import sys
import unittest
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from detect_exceptions import detect_findings  # noqa: E402


class RuleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / "test.sqlite"
        source = ROOT / "grc_stage1.sqlite"
        if not source.is_file():
            self.fail("Missing grc_stage1.sqlite; run scripts/setup_local.py")
        with closing(sqlite3.connect(source)) as s, closing(sqlite3.connect(self.db)) as d:
            s.backup(d)

    def findings(self):
        with closing(sqlite3.connect(self.db)) as conn:
            return detect_findings(conn)

    def test_baseline_four(self):
        f = self.findings()
        self.assertEqual(len(f), 4)
        self.assertEqual({row["rule_id"] for row in f}, {"R01", "R02", "R03", "R04"})

    def test_cancelled_payment_is_not_duplicate(self):
        with closing(sqlite3.connect(self.db)) as c, c:
            c.execute("INSERT INTO payments VALUES (?,?,?,?,?)",
                      ("PAY-9999", "INV-0001", "2026-10-15", 22000, "Cancelled"))
        f = self.findings()
        self.assertEqual(len(f), 4)
        self.assertFalse(any(row["invoice_id"] == "INV-0001" for row in f))

    def test_new_completed_full_payment_is_flagged(self):
        with closing(sqlite3.connect(self.db)) as c, c:
            c.execute("INSERT INTO payments VALUES (?,?,?,?,?)",
                      ("PAY-9999", "INV-0001", "2026-10-15", 22000, "Completed"))
        f = self.findings()
        self.assertEqual(len(f), 5)
        self.assertTrue(any(row["invoice_id"] == "INV-0001" and row["rule_id"] == "R01" for row in f))

    def test_correcting_approver_clears_finding(self):
        with closing(sqlite3.connect(self.db)) as c, c:
            c.execute("UPDATE purchase_requests SET approved_by='EMP-003' WHERE request_id='PR-0014'")
        f = self.findings()
        self.assertEqual(len(f), 3)
        self.assertFalse(any(row["rule_id"] == "R03" for row in f))

    def test_payment_with_pending_approval_below_threshold(self):
        with closing(sqlite3.connect(self.db)) as c, c:
            c.execute("UPDATE purchase_requests SET approval_status='Pending', approved_by=NULL, approval_on=NULL WHERE request_id='PR-0001'")
        f = self.findings()
        self.assertEqual(len(f), 5)
        self.assertTrue(any(row["rule_id"] == "R02" and row["request_id"] == "PR-0001" for row in f))


if __name__ == "__main__":
    unittest.main(verbosity=2)