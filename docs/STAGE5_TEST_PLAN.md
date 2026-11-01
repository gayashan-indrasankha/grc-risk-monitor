# Stage 5 — End-to-End Test Plan

## Purpose and terminology

This project is an internal-audit training prototype. Its rule engine flags **potential control exceptions**, not verified fraud or financial losses. `related_amount_lkr` measures the transaction value associated with a finding, which can overlap other findings.

- **Functional testing:** does a business detection rule return the right candidates?
- **Regression testing:** do previous cases still work after a change?
- **Data-quality testing:** are IDs, references, dates, amounts and required values valid?
- **Integration testing:** does information transfer correctly between SQLite, CSV, Power BI and Power Automate?
- **Reliability testing:** do notifications avoid routine duplicates, and are failures visible?
- **Audit evidence:** screenshots, CSV outputs and test logs that another reviewer can reproduce.

## A. Automated test cases

Run `python -m unittest discover -s tests -p "test_*.py" -v`. These cases are implemented in the new Stage 5 files; the existing Stage 2/3 tests remain active.

| Test ID | Scenario | Expected behavior |
|---|---|---|
| A01 | Original four planted cases | Exactly R01, R02, R03, R04; three High |
| A02 | Extra **cancelled** full payment | Does not trigger duplicate for new invoice |
| A03 | Extra **partial** completed payment | Does not trigger full-duplicate rule |
| A04 | Extra full-value **completed** payment | Triggers a new duplicate finding |
| A05 | Pending payment on a pending approval | No completed-payment-without-approval finding |
| A06 | Missing manager for approved high-value request | Wrong-approver-role finding remains |
| A07 | Correct manager approves high-value request | Wrong-role finding disappears |
| A08 | Amount exactly LKR 100,000 | Does not meet the **greater-than** threshold |
| A09 | Possible split requests separated by more than three days | Does not meet the three-day screening rule |
| A10 | Possible split pair totals less than threshold | Does not meet amount rule |
| A11 | Detection run | Does not update database data |
| B01 | Database foreign keys and payment amounts | No orphan references or nonpositive payments |
| B02 | Stage 2 findings CSV | Agrees with latest SQLite detection results |
| B03 | Finding record quality | Unique IDs and key fields present |
| B04 | Power BI baseline | 20 requests, 21 payments, four findings, three High, four Open |
| B05 | Data-model relationships | Supplier/date dimension values cover facts |
| B06 | Related exception amount | Nonnegative, but **not** confirmed loss |
| B07 | Export keys | Unique fact and dimension keys |

These tests are **illustrative synthetic cases**. They do not yet test every real-world edge case, such as credit notes, refunded transactions, changing approval delegations, timezone boundaries, or concurrent financial events.

## B. Power BI manual verification

| Test ID | Steps | Expected | Evidence to record |
|---|---|---|---|
| BI01 | Clear all filters, click **Refresh** | Cards: 20 requests, 21 payments, 4 findings, 3 High, 4 Open | Screenshot of all cards |
| BI02 | Inspect findings by type and severity | One each for R01-R04; 3 High, 1 Medium | Screenshot of both charts |
| BI03 | Select a supplier with a flagged finding | Relevant exception visuals change; clear selection to reset | Before/after counts |
| BI04 | Select a date range covering a known finding, then exclude it | Date-linked exception counts change as expected | Before/after screenshots |
| BI05 | Inspect table and filter by finding | Each finding ID maps to its evidence and action | Screenshot (redact identifiers if needed) |
| BI06 | Examine the related-value total | Label says **related amount**, not fraud or confirmed loss | Screenshot of table title |
| BI07 | Save and reopen `.pbix` | Model relationships, visuals and slicers persist | Result in test report |

**Important:** Requests, payments and findings have **different date roles** (`requested_on`, `paid_on`, `event_date`). Date-filtered card totals may differ because they represent distinct business events.

## C. Power Automate manual verification

Follow `STAGE5_POWER_AUTOMATE_TESTS.md` for safe scenarios. The completed first and second runs already provide evidence of basic filtering and duplicate prevention. Do not rerun the live flow just to cause more email traffic.

| Test ID | Scenario | Expected |
|---|---|---|
| PA01 | Four rows, three High/Open/Pending | Filter produces three |
| PA02 | Initial test to **your** Gmail address | Three test emails, for EX-0001/2/3 |
| PA03 | Excel update after email success | Three rows have `alert_status=Sent` and timestamps |
| PA04 | Rerun without resetting Excel | Zero qualifying rows, no emails |
| PA05 | Medium risk stays Pending | EX-0004 does not trigger High-risk alert |
| PA06 | Gmail send fails in copied test flow | Excel row must not become Sent |
| PA07 | Excel update fails **after** successful send in copied flow | Document duplicate-send risk on retry; design an improvement |
| PA08 | Two simultaneous flow runs | Explain why Excel Pending/Sent alone does not guarantee exactly-once delivery |

## D. Reporting rules

- Write *observed* results, not guessed outcomes.
- Keep screenshots of green checks AND field-level values such as status/timestamp.
- Report limitations and open defects.
- Don't copy live credentials or personal account details into public GitHub evidence.
- Avoid claiming real-world 100% accuracy from four planted anomalies.

## E. Stage 5 acceptance criteria

- [ ] Automated suite passes in your Windows environment.
- [ ] `scripts/stage5_validate.py` reports PASS.
- [ ] Power BI BI01–BI07 checked.
- [ ] Stage 4 PA01–PA05 checked from existing screenshots; PA06–PA08 discussed and, if safe, tested in clones.
- [ ] All defects and limitations listed in the test report.
- [ ] Redacted evidence captured and committed appropriately.
