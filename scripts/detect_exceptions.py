#!/usr/bin/env python3
"""Stage 2: transparent SQL-based exception detection (stdlib only).

Never loads data/ground_truth_FOR_TESTS_ONLY.csv. All records are fictional.
Run from the project folder: python scripts/detect_exceptions.py
"""
from __future__ import annotations
import argparse
import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THRESHOLD_LKR = 100_000
FIELDS = [
    "finding_id", "rule_id", "exception_type", "severity", "reference_ids",
    "supplier_id", "supplier_name", "request_id", "invoice_id",
    "related_amount_lkr", "evidence", "recommended_action", "status",
]


def sql(name: str) -> str:
    return (ROOT / "sql" / "detection_rules" / name).read_text(encoding="utf-8")


def detect_findings(conn: sqlite3.Connection) -> list[dict[str, str]]:
    """Find potential exceptions from underlying business records only."""
    conn.row_factory = sqlite3.Row
    findings = []

    def add(rule_id, exception_type, severity, ids, supplier_id, supplier_name,
            request_id, invoice_id, amount, evidence, action):
        findings.append(dict(
            finding_id="", rule_id=rule_id, exception_type=exception_type,
            severity=severity, reference_ids=";".join(sorted(ids)),
            supplier_id=supplier_id, supplier_name=supplier_name,
            request_id=request_id, invoice_id=invoice_id,
            related_amount_lkr=f"{float(amount):.2f}", evidence=evidence,
            recommended_action=action, status="Open",
        ))

    for r in conn.execute(sql("duplicate_payment.sql")):
        ids = r["payment_ids"].split(",")
        add("R01", "duplicate_payment", "High", ids,
            r["supplier_id"], r["supplier_name"], r["request_id"], r["invoice_id"],
            r["invoice_amount"],
            f"Invoice {r['invoice_id']} has {r['completed_full_payments']} completed full-value payments: {', '.join(sorted(ids))}.",
            "Review bank confirmations and supporting invoices; check for refunds or valid corrections.")

    for r in conn.execute(sql("completed_payment_without_approval.sql")):
        add("R02", "completed_payment_without_approval", "High", [r["request_id"]],
            r["supplier_id"], r["supplier_name"], r["request_id"], "",
            r["amount"],
            f"Request {r['request_id']} is {r['approval_status']} but a completed payment exists ({r['payment_ids']}).",
            "Verify approval records and payment timing; escalate to the authorized reviewer.")

    for r in conn.execute(sql("wrong_approver_role.sql"), (THRESHOLD_LKR,)):
        add("R03", "wrong_approver_role", "High", [r["request_id"]],
            r["supplier_id"], r["supplier_name"], r["request_id"], "",
            r["amount"],
            f"Request {r['request_id']} exceeds LKR {THRESHOLD_LKR:,} but was approved by {r['approved_by']} (role: {r['actual_role']}).",
            "Check the approval delegation policy and obtain manager review.")

    for r in conn.execute(sql("potential_split_purchase.sql"),
                          (THRESHOLD_LKR, THRESHOLD_LKR, THRESHOLD_LKR)):
        ids = [r["first_request_id"], r["second_request_id"]]
        add("R04", "potential_split_purchase", "Medium", ids,
            r["supplier_id"], r["supplier_name"], "", "",
            r["combined_amount"],
            f"Requests {', '.join(ids)} share supplier, requester and business need within 3 days; amounts LKR {r['first_amount']:,.2f} and {r['second_amount']:,.2f} exceed threshold when combined.",
            "Examine business justification and whether the requests were legitimately separate.")

    for i, item in enumerate(findings, 1):
        item["finding_id"] = f"EX-{i:04d}"
    return findings


def write_findings(findings: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(findings)


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect potential procurement control exceptions")
    parser.add_argument("--db", type=Path, default=ROOT / "grc_stage1.sqlite")
    parser.add_argument("--out", type=Path, default=ROOT / "output" / "exceptions.csv")
    args = parser.parse_args()
    if not args.db.is_file():
        parser.error("Database not found. Run python scripts/setup_local.py first.")
    with sqlite3.connect(args.db) as conn:
        findings = detect_findings(conn)
    write_findings(findings, args.out)
    print(f"Detected {len(findings)} potential exceptions:")
    for f in findings:
        print(f"  {f['finding_id']} | {f['rule_id']} | {f['reference_ids']} | {f['severity']}")
    print(f"Exported: {args.out}")
    print("All findings are investigation leads, not confirmed fraud or financial loss.")


if __name__ == "__main__":
    main()
