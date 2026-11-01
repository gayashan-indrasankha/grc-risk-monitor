# Stage 5 screenshot evidence

These six reviewed screenshots support the [Stage 5 results report](../../STAGE5_RESULTS_TEMPLATE.md). Their original S01-S06 evidence IDs are retained in the report; filenames now describe their contents. Renaming did not change image content.

| ID | File | What the archived image establishes |
|---|---|---|
| S01 | [power-bi-dashboard-overview.png](power-bi-dashboard-overview.png) | Baseline cards 20 / 21 / 4 / 3 / 4, charts and finding rows. |
| S02 | [power-bi-dashboard-date-filter.png](power-bi-dashboard-date-filter.png) | 1-10 October filter with cards 10 / 7 / 3 / 2 / 3. |
| S03 | [power-bi-dashboard-supplier-filter.png](power-bi-dashboard-supplier-filter.png) | Fictional Facilities Co Ltd selected; cards 3 / 3 / 1 / 1 / 1. |
| S04 | [excel-exception-register-redacted.png](excel-exception-register-redacted.png) | Fictional exception rows; cropped before the notification-state and reviewer-email columns. |
| S05 | [power-automate-rerun-skipped-actions.png](power-automate-rerun-skipped-actions.png) | Successful upstream steps/loop container with skipped Gmail and Excel update actions; filter output is not expanded. |
| S06 | [gmail-synthetic-risk-alerts.png](gmail-synthetic-risk-alerts.png) | Three synthetic alert subjects for EX-0001, EX-0002 and EX-0003. |

## Privacy and evidence boundaries

The original Excel attachment contained a real reviewer address and remains outside the public archive. The archived crop excludes that address **and** the `alert_status` / `alert_sent_at` columns. The report preserves the original observation of Sent/Pending state, but this public crop cannot independently demonstrate those values.

The run diagram supports skipped actions only. An empty Filter array, explicit zero iterations and no new messages are still separate PA04 evidence gaps. Do not describe the archived diagram as proof of exactly-once delivery or as a failure test.

Still needed: a supplier-reset observation, readable Power BI evidence/actions, focused first-/second-run filter outputs, and a redacted register capture that preserves notification status/timestamps. The existing report includes the supplied 28-test transcript and local validation JSON; no terminal screenshot is claimed here.

Add new screenshots only after removing personal addresses, account/tenant identifiers, credentials and unrelated messages. Keep the [main README](../../../README.md) and report links synchronized when filenames change.
