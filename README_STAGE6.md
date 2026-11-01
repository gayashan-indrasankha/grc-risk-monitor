# Stage 6 — Publish the GRC Risk Monitor Portfolio

The reviewed Stage 6 draft has been merged into the [main README](README.md). Use that file as the canonical project overview. The existing detection code and live Power Automate flow do not need changes for this documentation merge. All business data are synthetic.

## Installation

1. Commit or back up your current Git repository.
2. Extract this ZIP at the root of `D:\grc-risk-monitor`; files deliberately avoid the current root `README.md` and existing `docs/STAGE5_*.md`.
3. Review the merged `README.md`. `README_STAGE6_DRAFT.md` now points to it so there are no competing project overviews. Preserve the partial/manual test boundaries when making future edits.
4. Add **redacted** screenshots only after examining them for student email addresses, tenant IDs, messages, account names, secret tokens, and other personal information.
5. Follow `docs/STAGE6_CHECKLIST.md`, `docs/DEMO_SCRIPT.md`, and `docs/IFS_INTERVIEW_PREP.md`.
6. Optional: `.github/workflows/python-tests.yml` runs local scripts + tests against **synthetic fixtures only**. It does not use Gmail or Microsoft cloud accounts.

## Don't accidentally lose your cloud state

- Do not reset/reupload `GRC_Exception_Register.xlsx` just to make the demo appear fresh. It stores delivery status needed to avoid duplicate notifications.
- The Power Automate flow and Gmail/Excel connector configuration live in your Microsoft environment, **not in Git automatically**.
- Use a redacted flow diagram, setup notes and screenshots for public documentation. Never publish connector credentials or unredacted email/tenant information.
- The test `ground_truth_FOR_TESTS_ONLY.csv` is synthetic grading data; make clear that the runtime detector never reads ground truth.

## Stage 6 completion criteria

- Public README explains the business problem, demo, five-stage pipeline, controls, testing, limitations, and setup.
- Architecture document identifies the manual Excel sync boundary between local detector and cloud flow.
- At least one redacted Power BI screenshot and one redacted workflow/evidence screenshot are linked and visible in GitHub.
- Verification commands and expected synthetic counts are reproducible (20 requests; 21 payments; 4 exceptions; 3 High; 4 Open).
- All 28 local tests and Stage 5 validator pass against the same documented baseline.
- Demo explains the system in 3–5 minutes, with human review and remaining cloud reliability limitations.
- Resume bullets accurately describe personal, completed work only.

## Recommended Git workflow

```powershell
git status
# copy Stage 6 files into the existing repository
# review the merged README.md and its evidence links
# add redacted screenshots (never original screenshots with university email)
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/stage5_validate.py
git status
git diff --stat
git add README.md README_STAGE6_DRAFT.md docs/ .github/workflows/python-tests.yml
git diff --cached --stat
git commit -m "docs: merge project overview and organize portfolio evidence"
git push
```

If any files are untracked or ignored, stage only the files you intend to publish. Do not blindly use `git add .` when local cloud exports or personal screenshots are present.
