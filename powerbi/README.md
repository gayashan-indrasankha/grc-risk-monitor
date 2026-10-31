# Stage 3 — Build the Power BI Risk Monitoring Dashboard

This is an **add-on for your existing Stage 2 Git repository**. The ZIP contains **only new files**; copy/extract them directly inside your repository folder (`scripts/`, `tests/`, `powerbi/`). You should not replace your completed Stage 1/2 work. All source records are **synthetic**.

## 1. Understand the business goal

An internal auditor wants to know:

1. How many purchase requests and payments are being monitored?
2. How many potential control exceptions were found?
3. How many findings are High risk and still Open?
4. Which suppliers and types of findings need investigation?
5. When did the underlying suspicious business events occur?

Stage 2 *detected* the exceptions. Stage 3 *explains* them to a decision-maker. A detected exception is not proof of fraud.

## 2. Produce the Power BI source files

From the **root of your existing Git repository**:

```powershell
python scripts/detect_exceptions.py
python scripts/export_powerbi.py
python -m unittest discover -s tests -p "test_*.py" -v
```

The second command creates these tables under `powerbi/data/`:

| CSV / Power BI table | Grain (one row per...) | Default row count |
|---|---|---:|
| `FactRequests.csv` | Purchase request | 20 |
| `FactPayments.csv` | Payment record | 21 |
| `FactExceptions.csv` | Detected finding | 4 |
| `DimSuppliers.csv` | Supplier | 5 |
| `DimDates.csv` | Calendar day covering source records | Depends on dates |

The export reads your existing `grc_stage1.sqlite` and `output/exceptions.csv`. It rejects stale exceptions if you've edited database records since running detection. **No original Stage 2 data is overwritten by the export.**

## 3. Import to Power BI Desktop (Windows)

1. Open **Power BI Desktop**. Save a new report as `powerbi/report/GRC_Risk_Monitor.pbix`.
2. On **Home**, choose **Get data > Text/CSV**. Import each of the **five** CSV files inside `powerbi/data/` separately.
3. Choose **Transform Data** when you import, or open **Transform data** afterward.
4. Rename queries (remove `.csv` if present) to **exactly**: `FactRequests`, `FactPayments`, `FactExceptions`, `DimSuppliers`, `DimDates`.
5. Verify data types:
   - **Date**: `FactRequests[requested_on]`, `FactPayments[paid_on]`, `FactExceptions[event_date]`, `DimDates[date]`.
   - **Decimal number / fixed decimal**: `FactRequests[amount_lkr]`, `FactPayments[paid_amount_lkr]`, `FactExceptions[related_amount_lkr]`.
   - **Whole number**: `FactExceptions[severity_sort]`, `DimDates[year]`, `DimDates[month_number]`, `DimDates[day_of_month]`.
   - **Text**: IDs, status, rule names, severity, document evidence.
6. Click **Close & Apply**.
7. If Power BI has auto-created unwanted relationships, **delete/adjust them** before creating the model described below.

**Why we use CSV:** it lets you learn Power BI without needing a database driver or paid connector. When Python re-exports the files, use **Refresh** in Power BI Desktop. Re-import only if paths or column structures change.

## 4. Create the data model (IMPORTANT)

In **Model view**, create exactly these **six** relationships:

```text
DimSuppliers[supplier_id]  1 ---> * FactRequests[supplier_id]
DimSuppliers[supplier_id]  1 ---> * FactPayments[supplier_id]
DimSuppliers[supplier_id]  1 ---> * FactExceptions[supplier_id]

DimDates[date]             1 ---> * FactRequests[requested_on]
DimDates[date]             1 ---> * FactPayments[paid_on]
DimDates[date]             1 ---> * FactExceptions[event_date]
```

All should be **active**, **Many-to-one (*:1)** (from Fact to Dim), with **Single** cross-filter direction **from the dimension to the fact**. There should be **no direct relationships between FactRequests, FactPayments, and FactExceptions**.

**Why:** one supplier can appear in many purchase requests/payments/findings; one date can appear in many records. This is a beginner-friendly multi-fact star schema.

Date semantics matter: `FactExceptions[event_date]` is the date of the underlying business event (later payment or later related request), **not the date an auditor discovered the issue**.

## 5. Create DAX measures

Open `powerbi/DAX_Measures.txt`. Under **Modeling > New measure**, create each of the measures separately. The first five are essential:

- Total Purchase Requests
- Total Payments
- Total Findings
- High Risk Findings
- Open Findings

With **no slicer filters**, expect: **20 requests, 21 payments, 4 findings, 3 high-risk, 4 open**.

Why measures? Unlike typing `4` into a textbox, a measure can recalculate automatically when you filter by supplier or date.

## 6. Assemble a one-page report

Set the canvas to a widescreen/16:9 layout if desired.

```text
+--------------------------------------------------------------+
| GRC RISK MONITORING | Synthetic Data | October 2026         |
+--------------------------------------------------------------+
| Requests: 20 | Payments: 21 | Findings: 4 | High: 3 | Open: 4|
+--------------------------------------------------------------+
| Findings by type               | Findings by severity        |
| [Clustered column chart]       | [Bar / donut chart]         |
+--------------------------------------------------------------+
| Findings by event date         | Supplier and date slicers   |
| [Line or column chart]         | [Filter controls]           |
+--------------------------------------------------------------+
| DETAIL TABLE: finding, type, severity, supplier, amount,      |
| evidence, recommendation, status, event date                 |
+--------------------------------------------------------------+
| Important: all findings require human review.               |
| Related amounts are NOT proven losses.                       |
+--------------------------------------------------------------+
```

### Visual setup guide

| Visual | Field / measure | Why |
|---|---|---|
| Card | `[Total Purchase Requests]` | Monitored workload |
| Card | `[Total Payments]` | Payment records |
| Card | `[Total Findings]` | Cases for review |
| Card | `[High Risk Findings]` | Risk priority |
| Card | `[Open Findings]` | Pending follow-up |
| Clustered column | X: `FactExceptions[exception_label]`; Y: `[Total Findings]` | Types of findings |
| Bar/donut | Category: `FactExceptions[severity]`; Values: `[Total Findings]` | Severity breakdown |
| Line/column | X: `DimDates[date]`; Y: `[Total Findings]` | Underlying event timeline |
| Table | `FactExceptions[finding_id]`, `exception_label`, `severity`, `DimSuppliers[supplier_name]`, `event_date`, `related_amount_lkr`, `evidence`, `recommended_action`, `status` | Evidence and action |
| Slicer | `DimSuppliers[supplier_name]` | Cross-filters all 3 fact tables |
| Slicer | `DimDates[date]` | Filters each fact table by its respective event date |
| Optional slicer | `FactExceptions[severity]` | Filters findings-related visuals only |

Consider sorting `FactExceptions[severity]` by `FactExceptions[severity_sort]` in Column tools so that High precedes Medium (the original labels may be alphabetical).

### Report design notes

- Use a consistent navy/teal color palette, but don't rely only on color to communicate severity.
- Display **LKR** for monetary columns. `related_amount_lkr` is the **associated amount**, not a loss or proven fraud.
- The demonstration has only **four** deliberately planted exceptions. Its charts will be sparse—that's correct for Stage 3. Later you can extend the synthetic dataset for better trend analysis.
- Some slicers affect only relevant measures: severity is a property of findings, not a property of all requests or payments.
- If a card shows `(Blank)` after selecting a date with no findings, verify the DAX measure uses `COALESCE` or adjust your zero behavior.

## 7. Test the dashboard before completing Stage 3

- [ ] With all slicers cleared: **20 requests, 21 payments, 4 findings, 3 High, 4 Open**.
- [ ] Finding types R01/R02/R03/R04 each appear once.
- [ ] All findings in the details table come from the CSV source; no fabricated rows.
- [ ] Supplier filtering changes the three fact-table cards appropriately.
- [ ] Date filtering changes counts in accordance with respective event dates.
- [ ] No many-to-many relationship warnings or ambiguous relationship errors.
- [ ] Amounts have LKR units and are never described as confirmed losses.
- [ ] Save your `.pbix` and capture screenshots of the dashboard and Model view.
- [ ] `python -m unittest discover -s tests -p "test_*.py" -v` passes.

## 8. Save your work in Git

```powershell
git status
git add scripts/export_powerbi.py tests/test_powerbi_export.py powerbi/
git commit -m "Complete Stage 3: Power BI reporting data model and dashboard"
git push
```

The Stage 3 add-on never replaces existing Stage 2 files. You can save `powerbi/report/GRC_Risk_Monitor.pbix` in the same repository if its size permits and it contains only synthetic data. **Do not upload real company data or secrets to a public repo.**

## 9. What you'll learn

- Difference between raw data, facts, dimensions and measures.
- Relationships, cardinality, filter direction, and dashboard interactivity.
- Difference between business-event date and detection date.
- Designing honest risk reporting with evidence and human review.

**Next Stage 4:** Power Automate automated notifications with controlled alert statuses and deduplication.

### Microsoft documentation

- CSV import: https://learn.microsoft.com/en-us/power-query/connectors/text-csv
- Relationships: https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-create-and-manage-relationships
- DAX measures: https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-measures
- Slicers: https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-slicers
