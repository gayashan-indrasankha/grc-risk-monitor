# Stage 5 — Testing, Validation & Reliability

**Scope:** Add-on for the existing `grc-risk-monitor` Git repository. All input records are synthetic. No existing Stage 1–4 files are overwritten by this ZIP. The script/test suite does NOT connect to Gmail, OneDrive, Power Automate or Power BI online.

## 1) Back up and add files

Before copying anything, from `D:\grc-risk-monitor`:

```powershell
git status
git add .
git commit -m "Complete Stage 4: Risk alert workflow"
```

Only commit if the staged changes contain no secrets, credentials, screenshots with private addresses, or generated real-contact data. In your current workflow, the Power Automate cloud configuration lives in your school tenant; **it is not automatically committed with Git.**

Extract this Stage 5 ZIP **into the root** of the same `D:\grc-risk-monitor` folder (beside `scripts`, `tests`, `data`, `sql`, `powerbi`). The ZIP adds new files to `scripts/`, `tests/` and `docs/`.

## 2) Run automated checks

**Do not regenerate data or reset your OneDrive exception register as part of Stage 5.** Your live Excel notification statuses matter for duplicate prevention.

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/stage5_validate.py
```

- Your original Stage 2 and Stage 3 tests should still pass.
- The new Stage 5 tests modify **temporary copies** of `grc_stage1.sqlite`, never the original database.
- `stage5_validate.py` reads the SQLite and CSV files, regenerates expected Power BI exports *inside a temporary folder*, and compares them with actual exports. It only writes `docs/stage5_validation_result.json`.
- If you deliberately changed the local data, the fixed 20/21/4 baseline tests may fail. Restore/verify the baseline before running the fixed-fixture regression suite, or redesign expected values using reviewed new ground truth.
- A PASS on four planted exceptions is a teaching result, not a production effectiveness claim.

Expected original dataset metrics: 20 requests, 21 payments, four findings (three High, one Medium), four Open findings, and 100% precision/recall **on the four planted baseline cases only**.

## 3) Manual checks (Power BI and Power Automate)

Read `docs/STAGE5_TEST_PLAN.md` and `docs/STAGE5_POWER_AUTOMATE_TESTS.md`. The Python tests **cannot** prove that the live Power BI `.pbix` or Gmail connector behaves correctly.

- Verify Power BI after **Refresh** and with cleared filters (20, 21, 4, 3, 4).
- Validate supplier/date slicers, exception detail table, DAX counts and amount labeling.
- Review completed Stage 4 evidence: three High-risk test emails, updated Excel statuses, and zero emails on the second run.
- Capture **redacted** screenshots and enter observations in `docs/STAGE5_RESULTS_TEMPLATE.md`.
- Test any failure or retry scenario only in a **separate copied flow and copied workbook**, addressed to yourself. Do not reset production `alert_status` or deliberately break your real flow.

## 4) Stage 5 done when

1. All local automated tests pass.
2. Stage 5 validation JSON returns `PASS`.
3. Manual Power BI refresh, filters and four findings are verified.
4. Gmail and Excel alert processing and zero-on-rerun are evidenced.
5. Known limitations are documented, including possible duplicate sends if Gmail succeeds but Excel row update fails, and concurrent runs.
6. Test evidence is documented in a clear report using **synthetic data only**.

## 5) Commit only reviewed, appropriate files

```powershell
git status
git diff --stat
git add scripts/stage5_validate.py tests/test_stage5_scenarios.py tests/test_stage5_data_quality.py docs/ README_STAGE5.md
git commit -m "Complete Stage 5: Validate GRC detection and monitoring"
git push
```

If your stage5 report includes your email address or any confidential information, redact it before committing. Do not commit school credentials, tokens, connection IDs, workbook containing your personal address, or `.pbix` with private data.
