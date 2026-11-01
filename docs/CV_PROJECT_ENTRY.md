# CV project description — based on completed, verifiable scope

**GRC Risk Monitoring Dashboard with Automated Alerts**  
*Python, SQL, SQLite, Power BI, DAX, Power Query, Power Automate, Excel Online, Gmail*

- Built a Power BI dashboard using fictional procurement and audit data, including risk KPIs, severity trends, supplier/date filters and exception drill-down views; validated results against SQL/CSV exports.
- Developed SQL/Python rules to flag potential duplicate payments, approval exceptions and split purchases; tested the four planted scenarios and documented false-positive and boundary conditions.
- Implemented a Power Automate workflow that filters High-risk Open findings, sends test Gmail alerts, and updates Excel notification status; documented three initial synthetic test alert subjects and observed notification state, with rerun filter-output verification still pending.
- Executed 28 automated tests and a Stage 5 reconciliation check; documented results, known failure/concurrency risks and the synthetic-only limits of evaluation metrics.

**Use only 2–3 bullets in a one-page internship CV.** Keep full details in the GitHub README. Do **not** add Claude, Microsoft Copilot, Copilot Studio, Isolation Forest, or real-world precision claims to *this project* unless you independently implemented and tested those features.

## 35-second interview summary

"I built a GRC monitoring prototype on fictional procurement records. SQL and Python detect potential control exceptions, Power BI visualizes them, and a Power Automate flow sends alerts to a test recipient and records notification state. The baseline produces four findings and the test suite includes 28 passing tests. I also documented that its synthetic precision/recall does not predict real-world performance and that the cloud alert flow needs stronger failure and concurrency handling before production use."
