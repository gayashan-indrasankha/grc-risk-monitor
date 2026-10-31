#!/usr/bin/env python3
"""Stage 3: build reproducible, dashboard-ready CSV files for Power BI.

Reads the *current* Stage 2 SQLite database and Stage 2 exception export.
Uses only Python standard library; read-only for source files.
Run: python scripts/export_powerbi.py
No real company data is included in this training project.
"""
from __future__ import annotations

import argparse
import csv
import sqlite3
from contextlib import closing
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "powerbi" / "data"

REQUEST_COLUMNS = [
    "request_id", "requested_on", "requester_id", "department", "supplier_id",
    "category", "business_need_id", "amount_lkr", "approval_status",
    "approved_by", "approver_role",
]
PAYMENT_COLUMNS = [
    "payment_id", "paid_on", "invoice_id", "request_id", "supplier_id",
    "paid_amount_lkr", "payment_status",
]
EXCEPTION_COLUMNS = [
    "finding_id", "rule_id", "exception_type", "exception_label", "severity",
    "severity_sort", "event_date", "reference_ids", "supplier_id",
    "request_id", "invoice_id", "related_amount_lkr", "evidence",
    "recommended_action", "status",
]
SUPPLIER_COLUMNS = ["supplier_id", "supplier_name"]
DATE_COLUMNS = ["date", "year", "month_number", "month_name", "year_month", "day_of_month"]

RULE_LABELS = {
    "R01": "Potential duplicate payment",
    "R02": "Payment without approval",
    "R03": "Wrong approver role",
    "R04": "Potential split purchase",
}
SEVERITY_ORDER = {"Critical": 1, "High": 2, "Medium": 3, "Low": 4}


def write_csv(path: Path, columns: list[str], records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def read_exceptions(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. First run: python scripts/detect_exceptions.py")
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def current_exception_matches(conn: sqlite3.Connection, exported: list[dict]) -> bool:
    """Refuse clearly stale Stage 2 export (e.g., DB changed after detection)."""
    from detect_exceptions import detect_findings
    actual = detect_findings(conn)
    keys = ("finding_id", "rule_id", "reference_ids", "supplier_id", "status", "related_amount_lkr")
    def compact(rows):
        return sorted(tuple(str(row.get(k, "")) for k in keys) for row in rows)
    return compact(actual) == compact(exported)


def event_date_for_finding(conn: sqlite3.Connection, finding: dict[str, str]) -> str:
    """Date of the underlying event, NOT the date an auditor detected the finding."""
    rule = finding["rule_id"]
    if rule == "R01":
        payment_ids = [part for part in finding["reference_ids"].split(";") if part]
        if not payment_ids:
            raise ValueError(f"Missing payment IDs in {finding['finding_id']}")
        marks = ",".join("?" for _ in payment_ids)
        q = f"SELECT MAX(paid_on) FROM payments WHERE payment_id IN ({marks}) AND payment_status = 'Completed'"
        result = conn.execute(q, payment_ids).fetchone()[0]
    elif rule in ("R02", "R03"):
        result = conn.execute(
            """SELECT MAX(p.paid_on) FROM payments p
               JOIN invoices i ON i.invoice_id = p.invoice_id
               WHERE i.request_id = ? AND p.payment_status = 'Completed'""",
            (finding["request_id"],),
        ).fetchone()[0]
    elif rule == "R04":
        request_ids = [part for part in finding["reference_ids"].split(";") if part]
        if not request_ids:
            raise ValueError(f"Missing purchase requests in {finding['finding_id']}")
        marks = ",".join("?" for _ in request_ids)
        q = f"SELECT MAX(requested_on) FROM purchase_requests WHERE request_id IN ({marks})"
        result = conn.execute(q, request_ids).fetchone()[0]
    else:
        raise ValueError(f"Unexpected rule {rule!r} in finding {finding['finding_id']}")
    if result is None:
        raise ValueError(f"Cannot derive event date for {finding['finding_id']}")
    return date.fromisoformat(str(result)).isoformat()


def export_tables(conn: sqlite3.Connection, exceptions: list[dict], output_dir: Path) -> dict[str, int]:
    """Generate two dimensions and three facts, with explicit star-schema keys."""
    conn.row_factory = sqlite3.Row

    request_rows = [dict(row) for row in conn.execute(
        """SELECT pr.request_id, pr.requested_on, pr.requester_id, e.department,
                  pr.supplier_id, pr.category, pr.business_need_id,
                  pr.amount AS amount_lkr, pr.approval_status, pr.approved_by,
                  approver.role AS approver_role
           FROM purchase_requests pr
           JOIN employees e ON e.employee_id = pr.requester_id
           LEFT JOIN employees approver ON approver.employee_id = pr.approved_by
           ORDER BY pr.request_id"""
    )]
    for row in request_rows:
        row["amount_lkr"] = f"{float(row['amount_lkr']):.2f}"
        row["approved_by"] = row["approved_by"] or ""
        row["approver_role"] = row["approver_role"] or ""

    payment_rows = [dict(row) for row in conn.execute(
        """SELECT p.payment_id, p.paid_on, p.invoice_id, i.request_id,
                  pr.supplier_id, p.paid_amount AS paid_amount_lkr,
                  p.payment_status
           FROM payments p
           JOIN invoices i ON i.invoice_id = p.invoice_id
           JOIN purchase_requests pr ON pr.request_id = i.request_id
           ORDER BY p.payment_id"""
    )]
    for row in payment_rows:
        row["paid_amount_lkr"] = f"{float(row['paid_amount_lkr']):.2f}"

    exception_rows = []
    for finding in exceptions:
        rule = finding["rule_id"]
        if rule not in RULE_LABELS:
            raise ValueError(f"Unknown exception rule: {rule}")
        severity = finding["severity"]
        if severity not in SEVERITY_ORDER:
            raise ValueError(f"Unexpected severity: {severity}")
        exception_rows.append({
            **finding,
            "exception_label": RULE_LABELS[rule],
            "severity_sort": SEVERITY_ORDER[severity],
            "event_date": event_date_for_finding(conn, finding),
            "related_amount_lkr": f"{float(finding['related_amount_lkr']):.2f}",
        })

    supplier_rows = [dict(row) for row in conn.execute(
        "SELECT supplier_id, supplier_name FROM suppliers ORDER BY supplier_id"
    )]

    day_values = [date.fromisoformat(row["requested_on"]) for row in request_rows]
    day_values += [date.fromisoformat(row["paid_on"]) for row in payment_rows]
    day_values += [date.fromisoformat(row["event_date"]) for row in exception_rows]
    if not day_values:
        raise ValueError("No dates found to build DimDate")
    first, last = min(day_values), max(day_values)
    day_rows = []
    day = first
    while day <= last:
        day_rows.append({
            "date": day.isoformat(), "year": day.year,
            "month_number": day.month, "month_name": day.strftime("%B"),
            "year_month": day.strftime("%Y-%m"), "day_of_month": day.day,
        })
        day += timedelta(days=1)

    supplier_ids = {row["supplier_id"] for row in supplier_rows}
    for table_name, rows in (("FactRequests", request_rows), ("FactPayments", payment_rows), ("FactExceptions", exception_rows)):
        for row in rows:
            if row["supplier_id"] not in supplier_ids:
                raise ValueError(f"Unknown supplier referenced by {table_name}: {row['supplier_id']}")

    files = {
        "FactRequests.csv": (REQUEST_COLUMNS, request_rows),
        "FactPayments.csv": (PAYMENT_COLUMNS, payment_rows),
        "FactExceptions.csv": (EXCEPTION_COLUMNS, exception_rows),
        "DimSuppliers.csv": (SUPPLIER_COLUMNS, supplier_rows),
        "DimDates.csv": (DATE_COLUMNS, day_rows),
    }
    for filename, (columns, rows) in files.items():
        write_csv(output_dir / filename, columns, rows)
    return {filename: len(rows) for filename, (_, rows) in files.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description="Export dashboard data for Power BI Desktop")
    parser.add_argument("--db", type=Path, default=ROOT / "grc_stage1.sqlite")
    parser.add_argument("--exceptions", type=Path, default=ROOT / "output" / "exceptions.csv")
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if not args.db.is_file():
        parser.error("Stage 2 database missing. Run python scripts/setup_local.py first.")
    try:
        findings = read_exceptions(args.exceptions)
        # Explicitly close the connection: important for Windows file handling.
        with closing(sqlite3.connect(args.db)) as conn:
            if not current_exception_matches(conn, findings):
                raise ValueError("Stage 2 exceptions are out of date. Run python scripts/detect_exceptions.py, then rerun export.")
            counts = export_tables(conn, findings, args.out)
    except (OSError, sqlite3.Error, ValueError) as exc:
        parser.exit(status=1, message=f"ERROR: {exc}\n")
    print("Stage 3 Power BI export completed:")
    for name, count in counts.items():
        print(f"  {name}: {count} rows")
    print(f"Open these files in Power BI Desktop: {args.out.resolve()}")
    print("All records are synthetic. Related amounts are NOT confirmed losses.")


if __name__ == "__main__":
    main()
