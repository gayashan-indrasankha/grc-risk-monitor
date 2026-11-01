# IFS AI & Automation Intern — Project interview practice

These are practice questions, not leaked/verified IFS questions. Responses should be adjusted to what you actually built.

**1. What business problem does the system solve?**
It helps an audit/risk reviewer identify potential duplicate payments, missing or improper approvals, and related split-purchase patterns, then review and track findings using Power BI and alerts.

**2. Why Python and SQL instead of an LLM?**
The four baseline checks are structured, auditable business conditions. SQL and deterministic Python are easier to test and explain. An LLM could assist with drafting summaries later, with evidence verification and human approval.

**3. Explain R01 duplicate-payment detection.**
It detects multiple completed full-value payments against the same invoice. This is a potential exception, not proof of fraud. Refunds, installments and corrections would require expanded logic.

**4. How is the LKR 100,000 threshold used?**
The fictional policy requires a Manager for requests *above* LKR 100,000. Tests check a case exactly at the threshold, which should not violate a strict greater-than condition.

**5. How does the split-purchase rule work?**
It examines pairs with the same requester, supplier and business need within three days; each request is at/below threshold, and the combined amount exceeds it. Such a pattern could be legitimate, so it must be reviewed.

**6. What are your Power BI measures?**
They count requests, payments, findings, High severity and Open status using fact tables. Supplier/date dimensions filter visuals via relationships. Explain the difference between event dates and request/payment dates.

**7. How does Power Automate avoid sending the same email twice?**
The filter selects only High/Open/Pending rows. On successful Gmail send, Excel updates `alert_status` to `Sent`. Sent rows should be excluded on a normal sequential rerun. The current screenshot shows skipped send/update actions; the exact empty-filter and no-new-mail outcomes remain partially evidenced. This does not guarantee exactly-once delivery under partial failures or overlapping runs.

**8. What if Gmail succeeds but the Excel update fails?**
The same record could still be Pending and be sent again. I would improve this with a durable notification state/outbox, stable IDs, controlled retries, and idempotency checks.

**9. What did you test?**
28 automated tests covering baseline cases, false-positive scenarios, boundary rules, data quality and export consistency; plus manual dashboard/notification checks. The synthetic fixture validation found all four planted scenarios, which does not establish production accuracy.

**10. What would you improve before production?**
Data privacy, realistic labeled cases, approval chronology, notification retry/recovery, concurrency control, stable business identities, monitoring, deployment, audit trail, and cloud sync.

**11. Where does AI fit?**
This project is a rule-based automation and analytics prototype. A future AI layer might prepare evidence-linked exception summaries or assist with policy document review. It must not replace verified control rules or human sign-off.

**12. What did you personally learn?**
Explain in your own words: schema design, SQL detection rules, testing against ground truth, DAX filter behavior, connector permissions, and operational failure modes. Avoid presenting AI-assisted code as unaided original implementation if asked.
