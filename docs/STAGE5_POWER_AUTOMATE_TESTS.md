# Stage 5 — Power Automate Reliability Tests

## What you already verified in Stage 4

A manual flow read Excel `tblExceptions`, filtered for `severity=High`, `status=Open`, `alert_status=Pending`, iterated over three findings, sent three Gmail test messages, then updated their Excel rows. The archived rerun diagram shows skipped send/update actions. Empty Filter array output, explicit zero iterations and no-new-mail verification remain partially evidenced in the results report; the diagram alone does not establish those outcomes.

## Test 1: Verify persistent Excel state (safe, read-only)

Open your OneDrive `GRC_Exception_Register.xlsx` and confirm:

| Finding | Severity | Expected `alert_status` | Expected `alert_sent_at` |
|---|---|---|---|
| EX-0001 | High | Sent | Nonempty UTC timestamp |
| EX-0002 | High | Sent | Nonempty UTC timestamp |
| EX-0003 | High | Sent | Nonempty UTC timestamp |
| EX-0004 | Medium | Pending | Empty |

Do not publish the `reviewer_email` column, authentication information or actual account addresses on GitHub.

## Test 2: Check filtered output (safe, read-only)

Open the **second** Power Automate flow run in Run History. Select **Filter array**. It should show `[]` or `0` objects. The Apply to each loop should have `0` iterations. Save a redacted screenshot of the run history.

## Test 3: Confirm action ordering

Open designer and check that **Send email (V2)** is immediately before **Update a row**, both inside **Apply to each**. In `Update a row`, verify **Run after** is configured for success only. It must not mark Sent for an email action that failed.

## Test 4: Understand failure modes (do not sabotage the live flow)

**Scenario A:** Gmail action fails before sending. Excel update must not happen; alert stays Pending for a later attempt. Test only on a **copied flow** and **copied Excel file** with a recipient set to your own controlled address.

**Scenario B:** Gmail sends successfully, but Excel Update a row then fails. On rerun, `alert_status` may still be Pending and a duplicate email can be sent. **Your current two-step design is not true exactly-once delivery.** Record this as a known limitation, not a failure you must reproduce by sending more messages.

**Scenario C:** Two flow runs start simultaneously while the same row is still Pending. Both can select it before either updates status. For the prototype, keep the flow **manual**, test with one run at a time and do not enable trigger concurrency. A production solution would need durable claiming, deduplication keys or transactional processing.

**Scenario D:** Workbook changed or locked. Excel connector may fail or lag. Ensure failure is visible in run history, capture timestamps and retry cautiously; don't silently mark Sent.

## Future production-grade improvements

- A durable alert/notification table keyed by a stable **business exception identity**, with delivery state (`Pending`, `Sending`, `Sent`, `Failed`) and attempt count.
- Distinguish notification delivery success from human investigation status.
- Stable finding identifiers: sequential IDs `EX-0001` etc. may be reassigned on regenerated data; avoid using them as permanent business identities across different datasets.
- A controlled retry policy, failure logs, and monitored errors.
- A database-backed outbox and safe concurrent claiming if workflows run automatically.
- Ensure reruns do not replace `Sent` rows with newly generated `Pending` values.

These are documented **limitations and proposed improvements**, not features already implemented.
