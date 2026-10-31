#!/usr/bin/env python3
"""Compare detected findings against planted test cases (never used by detector)."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read_csv(path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

# Stage 1 called this scenario unapproved_large_purchase; the rule covers
# all completed payments missing approval, even below the manager threshold.
RENAME = {"unapproved_large_purchase": "completed_payment_without_approval"}

def normalized(scenario, record_ids):
    return (RENAME.get(scenario, scenario), tuple(sorted(record_ids.split(";"))))


def main():
    truth = read_csv(ROOT / "data" / "ground_truth_FOR_TESTS_ONLY.csv")
    findings_path = ROOT / "output" / "exceptions.csv"
    if not findings_path.is_file():
        raise SystemExit("Missing output/exceptions.csv. Run detect_exceptions.py first.")
    findings = read_csv(findings_path)
    expected = {normalized(r["scenario"], r["record_ids"]) for r in truth}
    found = {normalized(r["exception_type"], r["reference_ids"]) for r in findings}
    tp, fp, fn = len(expected & found), len(found - expected), len(expected - found)
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    print(f"Exact scenario/ID matches: TP={tp}, FP={fp}, FN={fn}")
    print(f"Precision = {precision:.1%}; Recall = {recall:.1%}")
    for label, values in (("Unexpected detections", found - expected),
                          ("Missed planted cases", expected - found)):
        print(f"{label}: {sorted(values) if values else 'None'}")
    print("NOTE: Results on 4 planted synthetic cases are not real-world accuracy.")
    if fp or fn:
        raise SystemExit("FAIL: findings do not exactly match planted baseline cases")
    print("PASS: all planted cases identified without extra baseline findings.")

if __name__ == "__main__":
    main()
