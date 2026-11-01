# Stage 6 — 3–5 minute interview demo

**Before recording:** Open your local repository in VS Code, Power BI report, and **redacted** Power Automate run-history screenshot. Avoid showing personal email addresses, school identifiers, tenant IDs, or active connectors. Use previously captured results; you do not need to resend notifications.

## 0:00–0:35 — Business problem

"This is a synthetic GRC risk-monitoring prototype for a fictional company's procure-to-pay process. Manual checking of invoices and approvals can be slow, so my solution flags potential control exceptions for review. It does not decide that fraud has occurred."

## 0:35–1:20 — Data and detection

Show `data/`, `sql/detection_rules/`, and `scripts/detect_exceptions.py`. Explain each of R01-R04. Mention 20 requests, 21 payment records and four planted findings. Explain the LKR 100,000 **fictional** approval policy.

**Likely question:** How is detection different from ML? **Answer:** The current engine uses deterministic SQL/Python business rules, not an Isolation Forest or trained model.

## 1:20–2:20 — Power BI

Show KPI cards (20, 21, 4, 3, 4). Filter by supplier and date. Open a finding and point out evidence and recommended action. Explain that the monetary sum is related transaction value, not proven loss.

## 2:20–3:10 — Automation

Explain the workflow: List Excel rows -> Filter High/Open/Pending -> Apply to each -> Gmail send -> Update Excel `Sent` + UTC timestamp. Show the three synthetic alert subjects and the rerun diagram with skipped email/update actions. Explain that the empty filter output, explicit zero iterations and no-new-mail outcome remain partially evidenced. Do not trigger new live emails during a recorded demo unless necessary and authorized.

## 3:10–4:00 — Testing

Run or show `python -m unittest discover -s tests -p "test_*.py" -v` and `python scripts/stage5_validate.py`. State 28 passing tests and planted-case precision/recall of 100% **only on four designed cases**. Include one negative case such as cancelled or partial payment.

## 4:00–5:00 — Limitations and what you'd do next

Mention manual cloud sync, small sample size, unverified real-world accuracy, possible duplicate alerts after partial send/update failure, and concurrency risk. Explain the next design improvement: a durable notification register/outbox and stable finding IDs.

## Recording checklist

- [ ] GitHub page or local repo structure visible
- [ ] Power BI report shown after refreshing locally
- [ ] One supplier filter and one date filter demonstrated
- [ ] SQL rule or Python detector briefly explained
- [ ] Gmail/Power Automate evidence shown *redacted*
- [ ] Test results shown with correct synthetic-only qualification
- [ ] No live credentials or personal accounts exposed
- [ ] No unbuilt AI agent or ML model claimed
