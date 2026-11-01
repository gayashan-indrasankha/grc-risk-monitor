# Stage 5 — Validation Evidence & Test Report

> **Status: PARTIAL.** All 28 local automated tests passed, and local reconciliation returned PASS. Screenshots and explicit tester confirmations support the manual results below; remaining checks and failure scenarios are identified separately.
>
> **Project:** GRC Risk Monitoring Dashboard with Automated Alerts (synthetic data).

## Test session and evidence provenance

- Report date: **2026-11-01**, Asia/Colombo (UTC+05:30).
- Tester: **Gayashan Indrasankha**; results supplied from the tester's PowerShell session, six screenshots and the follow-up confirmations recorded below.
- Unittest command: `python -m unittest discover -s tests -p "test_*.py" -v`.
- Validation command: `python scripts/stage5_validate.py`.
- Python and Power BI Desktop versions: **not recorded in the supplied evidence**.
- Power Automate environment: cloud flow using Gmail and Excel actions; environment name and tenant identifiers are not recorded here.
- Repository HEAD at report preparation: `9cbf5c95567b14f13e2d95a1ecfc7c0d0e2a1c00`. The supplied console transcript does not independently identify the commit used for its test run.
- Data: existing synthetic baseline in `data/`, local `grc_stage1.sqlite`, `output/exceptions.csv`, and the five `powerbi/data/` exports.
- Validation timestamp: **2026-11-01 08:25:45 UTC / 13:55:45 Asia/Colombo**, from [stage5_validation_result.json](stage5_validation_result.json).

Automated run results below are transcribed from the tester's supplied console output and checked against the existing validation JSON. The report update did not rerun the tests or operate the live cloud flow. Screenshot observations were also compared with the local Power BI CSVs; this comparison is separate from running the Power BI report.

Result meanings: **Pass** records the observed or explicitly tester-confirmed scope stated in the row; **Partial** means only part of the planned check is evidenced; **Not evidenced** means the supplied material does not establish execution or outcome; **Not run** identifies failure/concurrency scenarios for which no execution was reported. No unperformed failure test is recorded as passed.

## Automated tests

**28 run, 28 passed, 0 failures, 0 errors**, in **0.271 seconds**. The supplied output contains no skipped-test entries.

| Suite | Passed | Recorded coverage |
|---|---:|---|
| [test_detection.py](../tests/test_detection.py) | 5 | Baseline, cancelled/full duplicate payments, corrected approver, pending approval below threshold |
| [test_powerbi_export.py](../tests/test_powerbi_export.py) | 5 | Fact/dimension coverage, severity and dates, totals, export output checks, finding identities |
| [test_stage5_data_quality.py](../tests/test_stage5_data_quality.py) | 7 | B01-B07: references, current export agreement, required values, counts, dimensions, amounts and unique keys |
| [test_stage5_scenarios.py](../tests/test_stage5_scenarios.py) | 11 | A01-A11: baseline, payment variants, approval roles, threshold boundary, split window/amount and detection write check |
| **Total** | **28** | **All passed in the supplied run** |

### Supplied unittest transcript

```text
test_baseline_four ... ok
test_cancelled_payment_is_not_duplicate ... ok
test_correcting_approver_clears_finding ... ok
test_new_completed_full_payment_is_flagged ... ok
test_payment_with_pending_approval_below_threshold ... ok
test_dimensions_cover_facts ... ok
test_exception_severity_and_dates ... ok
test_expected_baseline_totals ... ok
test_export_does_not_change_stage2_files ... ok
test_findings_match_underlying_stage2_export ... ok
test_b01_foreign_keys_and_positive_payment_amounts ... ok
test_b02_exception_export_matches_current_database ... ok
test_b03_finding_identifiers_unique_and_required_values_present ... ok
test_b04_expected_baseline_counts ... ok
test_b05_suppliers_and_dates_reference_valid_dimensions ... ok
test_b06_related_amounts_not_negative ... ok
test_b07_table_keys_are_unique ... ok
test_a01_baseline_four_distinct_planted_findings ... ok
test_a02_cancelled_extra_payment_does_not_trigger_duplicate ... ok
test_a03_partial_extra_payment_does_not_trigger_full_duplicate ... ok
test_a04_new_full_completed_payment_triggers_duplicate ... ok
test_a05_pending_payment_is_not_a_paid_without_approval_exception ... ok
test_a06_missing_manager_approval_triggers_role_exception ... ok
test_a07_correct_manager_approval_clears_role_exception ... ok
test_a08_exactly_at_threshold_is_not_above_threshold ... ok
test_a09_split_outside_three_day_window_is_not_flagged ... ok
test_a10_split_pair_below_threshold_is_not_flagged ... ok
test_a11_detector_is_read_only_on_disposable_database ... ok

Ran 28 tests in 0.271s
OK
```

Method names are retained; unittest class/module prefixes and the separator line are omitted for readability. These are local Python/SQLite/CSV checks. They do not execute Gmail, Excel cloud actions, live Power BI refresh, or failure/concurrency scenarios in Power Automate.

## Stage 5 reconciliation

**Overall local result: PASS.** The console output agrees with [the validation JSON](stage5_validation_result.json), whose `problems` list is empty.

| Metric | Observed | Expected synthetic baseline |
|---|---:|---:|
| Purchase requests | 20 | 20 |
| Payments | 21 | 21 |
| Findings | 4 | 4 |
| High-risk findings | 3 | 3 |
| Medium-risk findings | 1 | 1 |
| Open findings | 4 | 4 |
| Planted-case true positives | 4 | 4 |
| Planted-case false positives | 0 | 0 |
| Planted-case false negatives | 0 | 0 |
| Synthetic fixture precision | 100% | Exact match on four planted cases |
| Synthetic fixture recall | 100% | Exact match on four planted cases |

The validator reports agreement between current local detection results, the exceptions CSV and regenerated Power BI exports, plus the baseline checks. **These metrics describe four deliberately planted synthetic cases and do not establish real-world detection accuracy or cloud workflow reliability.**

## Screenshot evidence register

S01-S06 identify the six screenshots attached to the test report request, in attachment order. They are conversation evidence references, not links to image files already stored in Git. Repository copies and durable image links are **pending**; archive reviewed, redacted copies under `docs/evidence/stage5/` before publishing the screenshot evidence.

| ID | Screenshot | Observed evidence |
|---|---|---|
| S01 | Baseline Power BI dashboard | Cards 20 / 21 / 4 / 3 / 4; supplier All; full displayed date range; four type bars; 3 High and 1 Medium; four finding rows; related-value total LKR 520,000 |
| S02 | Power BI with narrowed date range | 1-10 October 2026; cards 10 / 7 / 3 / 2 / 3; EX-0001, EX-0002 and EX-0004 remain; related-value total LKR 375,000 |
| S03 | Power BI with supplier selected | Fictional Facilities Co Ltd; cards 3 / 3 / 1 / 1 / 1; only EX-0003, wrong approver role; related value LKR 145,000 |
| S04 | Excel exception register | Three High/Open rows show Sent with nonempty timestamps; the Medium/Open split-purchase row remains Pending with an empty sent timestamp; finding ID column is clipped |
| S05 | Power Automate run diagram | Trigger, List rows and Filter array show success; Apply to each, Send email (V2) and Update a row show skipped indicators; email precedes row update in the displayed loop |
| S06 | Mailbox alert list | Three synthetic High Risk alert subjects reference EX-0001, EX-0002 and EX-0003; message bodies and full recipient fields are not shown |

**Redaction required:** S04 exposes a real `reviewer_email` address. Its value is deliberately not copied into this report. Mask that column before saving or publishing the screenshot. Check other screenshot copies for unrelated personal/account details and publish only reviewed evidence.

The Power BI screenshot totals were compared with the current CSV exports:

| View | Requests | Payments | Findings | High | Open | Visible finding IDs |
|---|---:|---:|---:|---:|---:|---|
| Baseline, S01 | 20 | 21 | 4 | 3 | 4 | EX-0001, EX-0002, EX-0003, EX-0004 |
| 1-10 October, S02 | 10 | 7 | 3 | 2 | 3 | EX-0001, EX-0002, EX-0004 |
| Fictional Facilities Co Ltd, S03 | 3 | 3 | 1 | 1 | 1 | EX-0003 |

All three displayed views match their source-data counts. EX-0003 has event date **18 October 2026**, so the narrowed date range correctly excludes it. Requests, payments and findings use `requested_on`, `paid_on` and `event_date` respectively; their filtered counts intentionally differ. Related amounts are associated values, can overlap, and are not confirmed losses.

## Follow-up tester confirmations

On **2026-11-01**, the tester explicitly supplied these results in response to the evidence-gap questions. They are recorded as tester confirmations; no additional screenshots or independent executions were supplied for these three checks.

| ID | Check | Confirmed result |
|---|---|---|
| C01 | Power BI Refresh | **Pass** |
| C02 | Saving and reopening the `.pbix` | **Pass** |
| C03 | Update a row - Run after configured for email success only | **Pass** |

C03 confirms the inspected configuration. It does not establish the outcome of an actual Gmail failure, a row-update failure after sending, or concurrent flow executions; PA06-PA08 remain Not run.

## Manual Power BI validation

Test definitions: [STAGE5_TEST_PLAN.md](STAGE5_TEST_PLAN.md).

| Test | Result | Evidence and remaining boundary |
|---|---|---|
| BI01 - Refresh and baseline cards | **Pass, screenshot and tester confirmation** | S01 shows the correct 20 / 21 / 4 / 3 / 4 cards, supplier All and the full displayed date range. The tester confirmed Power BI Refresh passed (C01). |
| BI02 - Type and severity breakdown | **Pass** | S01 shows four type bars of one finding each and a severity breakdown of 3 High / 1 Medium, agreeing with R01-R04 in the CSV. |
| BI03 - Supplier filtering and reset | **Partial** | S01 versus S03 demonstrates correct filtering to Fictional Facilities Co Ltd: 3 requests, 3 payments and one High/Open finding, EX-0003. Clearing that supplier selection and observing the reset was not evidenced. |
| BI04 - Date filtering | **Pass** | S01 versus S02 demonstrates the expected inclusion/exclusion of dated findings and matching counts. EX-0003 on 18 October is excluded from 1-10 October. |
| BI05 - Finding detail, evidence and action | **Partial** | S01 shows the four IDs, types, severity and amounts; S03 shows the single supplier-related finding. Evidence text is truncated, recommended actions are offscreen, and filtering by finding itself was not demonstrated. |
| BI06 - Related-value labeling | **Pass, observed label** | The visible header is `Sum of related_amount_lkr`, not a fraud/loss label. Improve it to a readable title such as "Related transaction amount (LKR)" and add the overlapping-value/human-review explanation. |
| BI07 - Save and reopen report | **Pass, tester-confirmed** | The tester confirmed that saving and reopening the `.pbix` passed (C02). This result is based on the tester's confirmation; a separate reopen screenshot was not supplied. |

## Manual Power Automate validation

Test definitions: [STAGE5_TEST_PLAN.md](STAGE5_TEST_PLAN.md) and [STAGE5_POWER_AUTOMATE_TESTS.md](STAGE5_POWER_AUTOMATE_TESTS.md).

| Test | Result | Evidence and remaining boundary |
|---|---|---|
| PA01 - First-run filter selects three eligible rows | **Partial** | S04 and S06 corroborate processing of three High-risk cases. The first-run Filter array output containing exactly three High/Open/Pending objects was not supplied. |
| PA02 - Three synthetic alert messages | **Pass, visible subjects** | S06 shows three test alert subjects for EX-0001, EX-0002 and EX-0003. This records the visible messages only; full recipient fields and message bodies were not inspected. |
| PA03 - Excel notification state | **Pass, observed state and tester-confirmed configuration** | S04 shows three High/Open rows marked Sent with nonempty sent timestamps. S05 shows email before update, and the tester confirmed success-only Run after configuration (C03). The finding ID column is clipped, and the first successful update run was not supplied as a separate screenshot. No failure-handling outcome is inferred from the configuration check. |
| PA04 - Rerun selects zero rows and sends no new mail | **Partial** | S05 shows skipped loop/email/update actions, consistent with no loop work. It does not display an empty Filter array, explicit zero iteration count, or before/after mailbox evidence of no new mail; those outcomes remain unconfirmed. |
| PA05 - Medium-risk case remains Pending | **Pass, observed state** | S04 shows the Medium/Open split-purchase row Pending with an empty sent timestamp. S06 contains only the three High-risk subjects; no Medium-risk message is shown. |
| PA06 - Gmail failure leaves alert unsent | **Not run** | No controlled failure execution was reported or evidenced. Expected behavior is a pending/failed alert state without marking Sent. |
| PA07 - Row update fails after email success | **Not run; risk documented** | No controlled execution was reported. A successful email followed by failed state update can leave Pending and cause duplicate delivery on retry. This is a design limitation, not an observed successful failure-handling test. |
| PA08 - Concurrent runs | **Not run; risk documented** | No simultaneous-run test was reported. Two runs may select the same Pending row before either updates it; exactly-once delivery is not established. |

The skipped actions in S05 are not a Gmail failure test. Any future failure exercises should use a copied flow and copied workbook with a controlled test recipient. No live flow was run, reset or deliberately broken to prepare this report.

## Defects, evidence gaps and remaining limitations

| ID | Description | Status / mitigation |
|---|---|---|
| L01 | Four planted baseline exceptions and a small deterministic dataset cannot demonstrate real-world effectiveness. | Retain the synthetic-only metric scope; expand reviewed positive and negative cases before broader claims. |
| L02 | Detection uses simplified rules. The supplied suite does not establish approval-before-payment chronology, refunds/corrections, cumulative installment overpayments or changing approval delegations. | Add reviewed requirements and tests; the current approval-status check does not by itself prove approval occurred before payment. |
| L03 | Associated amounts can overlap across findings and are not confirmed fraud, financial loss or recovered value. | Keep human review and clear monetary labels; do not present the LKR 520,000 baseline sum as proven loss. |
| L04 | Gmail send and Excel row update are separate actions. A send can succeed while its state update fails. | Duplicate delivery on retry remains possible; PA07 is unperformed. Consider durable delivery state, stable deduplication keys and an outbox/claiming design. |
| L05 | Simultaneous runs can read the same Pending row. | Concurrency behavior and exactly-once delivery are unverified; PA08 is unperformed. Use controlled sequential prototype runs and design durable claiming before automated concurrent use. |
| L06 | The live Excel workbook is not automatically synchronized from current local detection. Regeneration can also reassign sequential finding IDs. | Preserve Sent state; reconcile intentionally and use stable business identities before integrating refresh and notification automation. |
| L07 | Local automated checks do not execute live Power BI or cloud connector behavior. | Complete the remaining manual checks and record their actual results. |
| L08 | Screenshot files are referenced from the review conversation and are not yet archived with this report; S04 contains a personal address. | Add redacted repository copies and durable links. Do not publish the unredacted register screenshot. |
| L09 | Detail evidence is truncated and recommendations are offscreen in the report screenshots; the amount header is a raw field name. | Capture readable detail/action evidence and improve the title to "Related transaction amount (LKR)". |
| L10 | Python/Power BI versions, the test-run commit, first-run filter output and rerun empty-filter output are not recorded. | Add version/run metadata and focused screenshots or explicit tester observations. Success-only Run after configuration is now recorded as tester-confirmed (C03); dynamic failure behavior remains untested. |

No automated failures were reported in the supplied run. Pending manual checks and documented design risks remain open; they are not converted into passes by the local PASS result.

## Outcome and remaining work

- **Overall Stage 5 acceptance status: PARTIAL.** Local automated testing and reconciliation passed. Screenshots support manual filtering, chart counts, visible email subjects and notification state; the tester also confirmed Refresh, save/reopen and success-only Run after configuration, with the specific boundaries above.
- Confirm supplier reset and readable finding evidence/actions (BI03, BI05). Power BI Refresh and save/reopen are now recorded as passed through C01-C02.
- Capture or explicitly record first-run eligible filter output and second-run empty filter/zero iterations/no new mail (PA01, PA04). Success-only Run after configuration is now recorded as passed through C03.
- Keep PA06-PA08 marked Not run unless controlled exercises are actually performed. Retain the failure/concurrency limitations even if the basic happy path works.
- Archive redacted S01-S06 copies and link them from the screenshot register; record tool versions and test-run commit when known.
- Before describing Stage 5 as complete or moving to Stage 6, review these open items against the acceptance criteria in the test plan.

### Learning demonstrated by the supplied evidence

- Positive and negative local cases help distinguish a full duplicate payment from cancelled or partial records and exercise threshold/window boundaries.
- Reconciliation links SQLite detection, CSV outputs and reporting tables; baseline and filtered dashboard totals agree with the source data.
- Date roles explain why request, payment and finding counts differ under the same slicer.
- An investigation finding, notification delivery state and confirmed misconduct are different concepts.
- A successful local suite and basic alert evidence do not prove failure recovery, concurrency safety or real-world detection accuracy.

Further personal reflections can be added by the tester. No additional learning experience or unperformed test outcome is asserted here.
