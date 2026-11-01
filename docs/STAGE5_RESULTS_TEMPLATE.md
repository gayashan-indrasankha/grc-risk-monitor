# Stage 5 — Validation Evidence & Test Report

> **Status:** TEMPLATE — fill in your observed results before describing Stage 5 as completed.
>
> **Project:** GRC Risk Monitoring Dashboard with Automated Alerts (synthetic data)

## Test session

- Test date:
- Tester:
- Python version:
- Power BI Desktop version:
- Power Automate environment (avoid exposing tenant IDs):
- Git commit hash:
- Data version / source dataset:

## Automated tests

- Command: `python -m unittest discover -s tests -p "test_*.py" -v`
- Tests run:
- Passed:
- Failed/errors:
- Evidence filename / screenshot:

## Stage 5 reconciliation

- Command: `python scripts/stage5_validate.py`
- Overall result:
- Purchase requests:  / Expected baseline: 20
- Payments:  / Expected baseline: 21
- Open findings:  / Expected baseline: 4
- High risk:  / Expected baseline: 3
- Planted-case TP / FP / FN:
- Precision / Recall (synthetic fixture only):
- Evidence: `docs/stage5_validation_result.json`

## Manual Power BI validation

| Test | Result (Pass/Fail/Not run) | Evidence / notes |
|---|---|---|
| BI01 | | |
| BI02 | | |
| BI03 | | |
| BI04 | | |
| BI05 | | |
| BI06 | | |
| BI07 | | |

## Manual Power Automate validation

| Test | Result (Pass/Fail/Not run) | Evidence / notes |
|---|---|---|
| PA01 | | |
| PA02 | | |
| PA03 | | |
| PA04 | | |
| PA05 | | |
| PA06 | | |
| PA07 | | |
| PA08 | | |

## Defects and limitations

| Defect ID | Description | Severity | Status / mitigation |
|---|---|---|---|
| | | | |

Important known limitations: tiny synthetic data, simple rule heuristics, overlapping exception amounts, no confirmed fraud/loss determination, live Excel workbook not automatically synced from the detector, potential duplicate send after email success + status update failure, and concurrency risks. List any more that you discover.

## Outcome

- Overall Stage 5 acceptance status (Pass/Fail/Partial):
- Remaining work before Stage 6:
- What I learned:

**Do not present test cases as passed until you actually executed and observed them.**
