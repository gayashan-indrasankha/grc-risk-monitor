"""Stage 3 CSV export tests: no external dependencies or temporary database locks."""
import csv
import sqlite3
import sys
import unittest
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from export_powerbi import export_tables, read_exceptions, current_exception_matches


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = ROOT / "grc_stage1.sqlite"
        if not self.db.exists():
            self.fail("Run python scripts/setup_local.py")
        self.exceptions = read_exceptions(ROOT / "output" / "exceptions.csv")
        with closing(sqlite3.connect(self.db)) as conn:
            self.assertTrue(current_exception_matches(conn, self.exceptions))
            self.counts = export_tables(conn, self.exceptions, Path(self.tmp.name))

    def read(self, name):
        with (Path(self.tmp.name) / name).open(encoding="utf-8", newline="") as file:
            return list(csv.DictReader(file))

    def test_expected_baseline_totals(self):
        self.assertEqual(self.counts["FactRequests.csv"], 20)
        self.assertEqual(self.counts["FactPayments.csv"], 21)
        self.assertEqual(self.counts["FactExceptions.csv"], 4)
        self.assertEqual(self.counts["DimSuppliers.csv"], 5)

    def test_exception_severity_and_dates(self):
        findings = self.read("FactExceptions.csv")
        self.assertEqual(sum(r["severity"] == "High" for r in findings), 3)
        self.assertEqual(sum(r["status"] == "Open" for r in findings), 4)
        self.assertTrue(all(r["event_date"] for r in findings))
        self.assertEqual({r["rule_id"] for r in findings}, {"R01", "R02", "R03", "R04"})

    def test_dimensions_cover_facts(self):
        suppliers = {r["supplier_id"] for r in self.read("DimSuppliers.csv")}
        dates = {r["date"] for r in self.read("DimDates.csv")}
        for file_name, date_key in (("FactRequests.csv", "requested_on"), ("FactPayments.csv", "paid_on"), ("FactExceptions.csv", "event_date")):
            for row in self.read(file_name):
                self.assertIn(row["supplier_id"], suppliers)
                self.assertIn(row[date_key], dates)

    def test_findings_match_underlying_stage2_export(self):
        src = {(r["finding_id"], r["rule_id"], r["reference_ids"]) for r in self.exceptions}
        exported = {(r["finding_id"], r["rule_id"], r["reference_ids"]) for r in self.read("FactExceptions.csv")}
        self.assertEqual(src, exported)

    def test_export_does_not_change_stage2_files(self):
        # No input file is created in the temporary output directory.
        paths = {p.name for p in Path(self.tmp.name).iterdir()}
        self.assertEqual(paths, {"FactRequests.csv", "FactPayments.csv", "FactExceptions.csv", "DimSuppliers.csv", "DimDates.csv"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
